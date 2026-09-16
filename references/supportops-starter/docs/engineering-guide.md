# Engineering guide

## Truth and validation layers

Keep JSON syntax, schema validation, source support, policy eligibility, authorization, and execution outcomes distinct. Passing an earlier layer never implies passing a later one.

For source evidence, store start-inclusive/end-exclusive indices into the original unnormalized Python `str`. Python string indices are Unicode code points, not UTF-8 bytes and not grapheme clusters. Verify that every stored span round-trips to the expected substring; semantic support still needs a separate check.

## Retrieval

Preserve document/version/section/chunk provenance. Inspect chunks before generation. Evaluate retrieval recall/relevance separately from final answer support. Start with a non-AI lexical baseline before claiming embeddings improved search. The embedding provider may differ from the generation provider and must be verified against current primary docs/runtime before being treated as available.

## Tools and data

Use narrow parameterized read functions before model tool calling. Trusted server-side context owns actor/tenant identity. Model arguments cannot grant broader access. Distinguish not-found, not-authorized, invalid input, timeout/service error, and confirmed business facts.

## Approval and writes

Approval binds an immutable proposal/version or digest, trusted actor, target, normalized parameters, expiry, and current required evidence/rule versions. Recheck authorization and mutable conditions at execution. Mutated/stale/rejected/missing/replayed approvals produce zero effects in the defined local tests. Unknown external write outcomes enter reconciliation; never blindly retry a consequential action.

## Checks now, test engineering later

A boundary check is how the mechanism proves its invariant locally. Write these beside schema/span/query/approval behavior. Small pytest/unittest cases are appropriate once repeatability helps. Full fixture architecture, coverage targets, CI and broad mocks are deferred until complexity or role requirements justify them.

## Observability

First preserve enough local information to answer: what input, retrieved evidence, model/tool call, error, latency/usage (if available), and final outcome occurred? Adopt a tracing product only when it solves a real debugging/evaluation problem and data/spending rules permit it.

## Provider-specific caution

Do not generalize an OpenAI-compatible response shape into unsupported provider behavior. For the reviewed Groq compatibility surface, `choices` is a list but supplied `n` must be 1. Reverify current official docs when the active lesson reaches provider-specific syntax.
