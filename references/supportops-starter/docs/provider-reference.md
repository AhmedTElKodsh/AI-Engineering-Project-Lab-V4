# Provider reference — dated baseline

Provider APIs change. This file records concepts, not permanent proof of current executability. Check current official docs and installed versions at the lesson that uses the capability.

## Generation baseline

The project may start with Groq for chat generation if the learner has authorized access. The response's `choices` member is list-shaped. On the reviewed Groq compatibility documentation, if `n` is supplied it must equal `1`; do **not** teach `n=2` as a valid Groq experiment.

A generic shape example:

```python
response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[{"role": "user", "content": prompt}],
)
text = response.choices[0].message.content
```

Exact model names, initialization, timeouts, JSON/structured-output flags and installed SDK versions must be verified at runtime before being called current.

## Embeddings

No Groq embedding route is an active default in this repository. The previous claim of a Groq Nomic embedding endpoint was not sufficiently substantiated by the official docs checked during the redesign. Select one documented embedding route at J3 and record model, dimensions, preprocessing, language scope, cost/setup trade-off and observed retrieval behavior. Generation and embeddings may use different providers.
