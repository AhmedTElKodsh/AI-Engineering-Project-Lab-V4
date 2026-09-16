# Create a new repository from this bundle

1. Extract `supportops-ai-project-lab-starter.zip` into a new empty directory.
2. Review `README.md`, `AGENTS.md`, and `docs/CURRICULUM.md`.
3. Run:

```bash
python tools/validate_workspace.py
python tools/validate_workspace.py --self-test
python tools/test_supportops.py
```

4. Initialize Git only after the files look correct:

```bash
git init
git add .
git commit -m "chore: initialize SupportOps AI project lab"
```

5. Create an empty GitHub repository and add it as your remote using the instructions GitHub shows for that repository. Do not commit `.env` or provider keys.

The initial progress files intentionally say the learner application location is unverified. If you already have learner code elsewhere, reconcile that location rather than creating a second app. If this is a genuinely fresh start, `projects/supportops/` is reserved for the learner-owned application and should grow only with the active J-stage.
