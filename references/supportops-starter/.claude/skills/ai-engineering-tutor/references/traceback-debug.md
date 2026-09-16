# Debug from evidence

Read the actual command, traceback/output and relevant code. State expected versus observed behavior and identify the supported failing layer: environment/import/config, provider/network, parse/schema, source support, retrieval, tool/scope, state or infrastructure.

Choose one experiment that distinguishes the leading hypothesis from a plausible alternative. Do not prescribe provider retries for a local import error or fix a retrieval miss by blindly changing only the answer prompt. A service timeout is not confirmed not-found.

Make the smallest requested correction and verify it. Add regression evidence where useful. Record what the learner diagnosed versus what the assistant supplied; later independent evidence uses a different failure.
