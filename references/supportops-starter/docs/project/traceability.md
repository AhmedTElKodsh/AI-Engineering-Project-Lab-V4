# Traceability

This file maps destination product requirements to the stage where the learner first encounters the core responsibility. A mapping does not mean the full destination requirement must be implemented at that stage.

| Requirement | First learning stage | Initial evidence |
|---|---|---|
| FR01 case handling | J1 | validated synthetic intake object |
| FR02 structured analysis | J1/J2 | schema + evidence + transfer cases |
| FR03 knowledge lifecycle | J3 | small corpus/version metadata; full lifecycle optional depth |
| FR04 grounded answer | J3 | retrieval result then cited/abstaining answer |
| FR05 live/current facts | J4 | scoped synthetic order read tool |
| FR06 deterministic eligibility | J4 | typed rule result with reasons |
| FR07 persistent workflow | J4 core state; durable restart optional | explicit local state, optional LangGraph depth |
| FR08 exact review | J4 | immutable proposal + approval tests |
| FR09 safe write | J4 local simulation; external/concurrency optional | replay-prevention and zero-effect negative cases |
| FR10 inspectable UI | J5 only if it improves demo | reproducible interface/command |
| FR11 evaluation/trace | throughout/J5 | expected-vs-observed cases, configs, failure analysis |
| FR12 ML comparison | optional depth | held-out classifier-vs-LLM report |
| FR13 async ingestion | optional depth | worker/job evidence only if reopened |
| FR14 operations/deployment | optional depth | target-specific deployment evidence only if reopened |

NFR01/NFR02 security and duplicate-prevention invariants arrive before the corresponding J4 action. NFR03-NFR05 numerical targets remain planning hypotheses until measured. NFR06/NFR07 reproducibility and synthetic-data discipline apply from the beginning.
