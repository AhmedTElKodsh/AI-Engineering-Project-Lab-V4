# J0 first runnable slice — implementation plan

**Goal:** produce and inspect the smallest authorized SupportOps model-backed result without making the destination architecture a prerequisite.

## Preconditions

Use the learner's existing application environment if it exists. First reconcile its location and installed versions from actual evidence. Do not create a new FastAPI/database project merely because later planning files describe one.

## Slice

1. Put one synthetic customer message and one short policy excerpt in local Python values.
2. Make one provider SDK call using the currently verified provider syntax and an explicit model.
3. Extract the returned text through the actual SDK response object.
4. Print/show the draft and label it as a draft only.
5. Record expected versus observed command/output and any failure layer.
6. Ask the learner to explain which logic stayed deterministic in Python and which output came from the model.

## Acceptance behavior

- No order/database lookup is claimed.
- No action execution is claimed.
- Configuration/import failures are distinguished from provider/network/model-quality failures.
- Secret values are never printed or committed.
- On the reviewed Groq surface, do not use `n=2`; list-shaped `choices` and supported completion count are separate concerns.

## Stop here

The first slice is complete when the learner can run/inspect a real or clearly labeled fake result and explain the request/response boundary. Structured extraction, Pydantic, retrieval, FastAPI, databases and agent frameworks belong to later slices.
