"""Read-only structural validation for the SupportOps AI teaching workspace."""
from __future__ import annotations

from pathlib import Path
import argparse
import copy
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'README.md', 'AGENTS.md', '.github/copilot-instructions.md',
    'docs/CURRICULUM.md', 'docs/TEACHING_GUIDE.md', 'docs/LESSON_TEMPLATE.md',
    'docs/ENGINEERING_GUIDE.md', 'docs/ASSESSMENT_CARDS.md',
    'docs/PROGRESS_PROTOCOL.md', 'docs/PORTFOLIO.md', 'docs/PROVIDER_REFERENCE.md',
    'docs/DECISIONS.md', 'docs/project/RELEASES.md',
    'progress/current.json', 'progress/skills.json', 'progress/evidence.jsonl',
    'fixtures/support/cases.json', 'fixtures/support/payloads.json',
    '.agents/skills/ai-engineering-tutor/SKILL.md',
    '.agents/skills/ai-engineering-tutor/agents/openai.yaml',
]
VALID_STATUSES = {'pending', 'in_progress', 'ready', 'complete'}
ASSISTANCE = {'none', 'docs', 'hint', 'scaffold', 'worked_example', 'ai_implemented'}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_progress(root: Path) -> None:
    current = read_json(root / 'progress/current.json')
    skills = read_json(root / 'progress/skills.json')
    events = [json.loads(x) for x in (root / 'progress/evidence.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    require(current.get('route') == 'J0-J5', 'current route must remain J0-J5')
    require(current.get('stage') == 'J0', 'starter stage should be J0')
    require(current.get('milestone') == '0.3', 'starter milestone should be 0.3')
    require(current.get('assistance_level') in ASSISTANCE, 'invalid assistance level')
    ids = [m.get('id') for m in current.get('milestones', [])]
    expected = ['0.3','0.4','0.5','0.6','0.7','0.8','0.9','J1','J2','J3','J4','J5']
    require(ids == expected, 'milestone IDs/order drifted')
    require(all(m.get('status') in VALID_STATUSES for m in current['milestones']), 'invalid milestone status')
    skill_ids = {r.get('id') for r in skills.get('skills', [])}
    require(skill_ids == {f'E{i:02}' for i in range(1,23)}, 'E01-E22 capability set drifted')
    later = {r.get('id') for r in skills.get('later_modules', [])}
    require(later == {f'Q{i}' for i in range(5,13)}, 'Q5-Q12 module set drifted')
    require(events and events[0].get('kind') == 'initialization', 'evidence log must start with initialization')
    require(current.get('last_event_id') == events[-1].get('id'), 'current/evidence last_event mismatch')
    require(skills.get('last_event_id') == events[-1].get('id'), 'skills/evidence last_event mismatch')


def markdown_links(path: Path):
    text = path.read_text(encoding='utf-8')
    for match in re.findall(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)', text):
        yield match


def validate_links(root: Path) -> None:
    for path in root.rglob('*.md'):
        if '.git' in path.parts:
            continue
        for link in markdown_links(path):
            if link.startswith(('http://','https://','#','mailto:')):
                continue
            target = link.split('#',1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            require(resolved.is_relative_to(root.resolve()), f'link escapes repo: {path}: {link}')
            require(resolved.exists(), f'broken local link: {path.relative_to(root)} -> {link}')


def validate_skill_mirror(root: Path) -> None:
    source = root / '.agents/skills/ai-engineering-tutor'
    mirror = root / '.claude/skills/ai-engineering-tutor'
    if not mirror.exists():
        return
    src = {p.relative_to(source) for p in source.rglob('*') if p.is_file()}
    dst = {p.relative_to(mirror) for p in mirror.rglob('*') if p.is_file()}
    require(src == dst, 'Claude tutor mirror file set drifted')
    for rel in src:
        require((source/rel).read_bytes() == (mirror/rel).read_bytes(), f'Claude tutor mirror content drifted: {rel}')


def validate_documents(root: Path) -> None:
    for rel in REQUIRED:
        require((root/rel).is_file(), f'missing required file: {rel}')
    for path in list(root.rglob('*.md')) + list(root.rglob('*.py')):
        text = path.read_text(encoding='utf-8')
        if path.suffix == '.md':
            require(sum(1 for line in text.splitlines() if line.strip().startswith('```')) % 2 == 0, f'unbalanced code fence: {path.relative_to(root)}')
    validate_links(root)
    validate_skill_mirror(root)


def validate_fixture_shapes(root: Path) -> None:
    cases = read_json(root/'fixtures/support/cases.json')['cases']
    payloads = read_json(root/'fixtures/support/payloads.json')['cases']
    require(len(cases) == 7 and len({x['id'] for x in cases}) == 7, 'expected seven unique support cases')
    require({x['kind'] for x in cases} == {'baseline','absent_fields','negation','uncertainty','chronology','instruction_like','arabic'}, 'support case coverage drifted')
    require(len(payloads) == 8 and len({x['id'] for x in payloads}) == 8, 'expected eight unique failure payloads')


def self_test() -> int:
    count = 0
    # A tiny synthetic check of require/error behavior. Full workspace validation is run separately.
    for condition, should_pass in [(True, True), (False, False)]:
        try:
            require(condition, 'synthetic failure')
            passed = True
        except ValueError:
            passed = False
        if passed != should_pass:
            raise AssertionError('self-test mismatch')
        count += 1
    sample = copy.deepcopy(read_json(ROOT/'progress/current.json'))
    sample['route'] = 'M0-M7'
    try:
        require(sample.get('route') == 'J0-J5', 'synthetic route rejection')
        raise AssertionError('self-test expected route rejection')
    except ValueError:
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        print(f'self-test: {self_test()} checks passed')
        return 0
    validate_documents(ROOT)
    validate_progress(ROOT)
    validate_fixture_shapes(ROOT)
    print('workspace validation: PASS')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, json.JSONDecodeError) as exc:
        print(f'workspace validation: FAIL: {exc}', file=sys.stderr)
        raise SystemExit(1)
