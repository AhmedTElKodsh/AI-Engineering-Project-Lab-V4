# Sources and dependency version policy

**Primary documentation reviewed:** 2026-09-15 (S14-S17 added in baseline 1.1.0). These references support tool behavior and security considerations. Product scope, targets, quantities, business rules, and teaching choices are proposed design decisions, not claims copied from a vendor or measured results.

| ID | Primary reference | Used for |
|---|---|---|
| S1 | [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) | Checkpointed human pause/resume and replay-sensitive side effects |
| S2 | [pgvector project documentation](https://github.com/pgvector/pgvector) | Vector search, indexing, and combination with PostgreSQL full-text search |
| S3 | [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/) | Typed models, validation, serialization, schema, and limits of shape validation |
| S4 | [LangSmith evaluation concepts](https://docs.langchain.com/langsmith/evaluation-concepts) | Datasets, experiments, and evaluator types |
| S5 | [Sentence Transformers retrieve and rerank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html) | Retrieval followed by cross-encoder reranking |
| S6 | [Scikit-learn evaluation metrics](https://scikit-learn.org/stable/modules/model_evaluation.html) | Precision, recall, F1, averaging, and model evaluation |
| S7 | [OWASP prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | Untrusted message/document instructions and application risk |
| S8 | [OWASP excessive agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) | Least privilege, narrow tools, authorization, and human review |
| S9 | [GitHub Copilot repository instructions](https://docs.github.com/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot) | Repository instructions and AGENTS.md support by surface |
| S10 | [OpenAI skill authoring](https://developers.openai.com/plugins/build/skills.md) and [Codex skills](https://developers.openai.com/codex/skills) | SKILL.md, supporting resources, `.agents/skills` discovery, `agents/openai.yaml` metadata, and optional tool dependencies |
| S11 | [uv project guide](https://docs.astral.sh/uv/guides/projects/) | pyproject, lockfile, environment, add/sync/run workflow |
| S12 | [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/) | TestClient-based HTTP tests |
| S13 | [GitHub agent skills](https://docs.github.com/copilot/concepts/agents/about-agent-skills) | Repository skill folders (`.github/skills`, `.claude/skills`, `.agents/skills`) and host-dependent availability |
| S14 | [Agent Skills specification](https://agentskills.io/specification) | `name` must match the skill folder; description limit; progressive disclosure; relative references |
| S15 | [uv build backend](https://docs.astral.sh/uv/concepts/build-backend/) | `uv_build`, `module-name`, and `src/` layout |
| S16 | [uv project configuration](https://docs.astral.sh/uv/concepts/projects/config/) | Without `[build-system]`, uv installs dependencies but not the project itself |
| S17 | [Status of Python versions](https://devguide.python.org/versions/) | Bugfix versus security-only support phases |

## Version choices

Use Python 3.13 as the initial application compatibility target (see ADR-008 and S17). Declare a `[build-system]` so uv installs the `commerce_support` package into the environment (S15, S16). Do not install every library at once. Introduce and lock dependencies in the task that first needs them. The first task uses FastAPI, Pydantic, pytest, httpx, and development quality tools. Add database/retrieval libraries at M2, graph integrations at M3, ML at M5, and workers at M6.

Before adding a dependency, verify supported Python versions, current official imports, package compatibility, license, and any model-specific capabilities. Resolve exact versions, run relevant tests, and commit `uv.lock`. Record the model ID/revision, embedding dimension, prompt/schema version, chunking/index version, and container image reference independently.

Do not assume a documentation example's model name exists in the learner's account. Use a configurable model ID verified at the first live experiment. Recheck pricing and availability before paid work; never hard-code a stale price into an evaluation report.

## Updating the project

Upgrade one coherent dependency group at a time. Preserve the previous lockfile through version control. Run contract, retrieval, workflow-resume, and safety tests affected by the change. Update this record with the checked version/date and any changed APIs. A passing unit test alone does not establish compatibility with a live provider or hosted environment.

## Source-versus-design distinction

S1-S17 support general tool capabilities. The thirty tasks, proposed architecture, 120-case holdout composition, fictional policy, latency/cost aspirations, and coach pedagogy are original project design choices. They require implementation and empirical validation.
