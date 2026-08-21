# LLM pipelines

Applies to any path where text the product did not author reaches a model:
scraped page metadata, user-submitted content, file contents, third-party API
responses, search results.

## The core rule

**External text is data, never instructions.**

The failure is indirect prompt injection: content fetched from elsewhere
contains text designed to be read as instructions by whatever model processes
it. The page title of a link a user saves is attacker-controlled. So is the
description, the alt text, and the filename.

This is a recognised weakness class, not an exotic one, and it is the primary
attack against retrieval-style pipelines.

## Structural defences, in order of value

### 1. Separate the channels

Never concatenate external text into the instruction portion of a prompt. Put it
in a clearly delimited data section, and state in the system instruction that
content in that section is untrusted and must never be followed as a directive.

Delimiters alone are not sufficient — they can be escaped — but the combination
of delimiting, explicit framing, and constrained output is.

### 2. Constrain the output shape

If the task is classification, require a response conforming to a fixed schema
with an enumerated set of allowed values. Validate the response against the
schema before use, and reject anything outside it.

An injected instruction can only cause harm if it can change what the system
does with the output. A model that can only return one of a fixed set of labels
has a very small blast radius even when successfully injected.

### 3. Give the pipeline no capabilities

The classification path should have no tool access, no network egress, no
database write permission beyond the single field it produces. Injection that
succeeds against a model with no capabilities produces a wrong label, which is a
quality problem, not a security incident.

**This is the highest-value control.** Prefer it over trying to sanitise input.

### 4. Sanitise defensively, not primarily

Strip control characters, normalise unicode, cap length, and remove markup
before the text reaches the model. Treat this as depth, not as the defence —
sanitisation is a filter, and filters are bypassed.

### 5. Never let model output become an instruction

Model output must not be executed, used to build a query, or fed into another
prompt's instruction section. If output feeds a downstream step, validate it
against a schema first.

## Data governance

- Confirm which content is contractually excluded from provider training and
  retention, and verify that exclusion is enforced in the code path, not just
  documented in the spec.
- Data belonging to a person who is not the account holder needs a documented
  legal basis before it reaches any provider.
- Log what was sent and when, in a form that supports a later deletion request.
  Do not log the content itself unless the privacy spec explicitly permits it.

## Testing

Use Garak with the prompt injection, encoding and leak-replay probes against the
deployed configuration, not against a bare model — the guardrails are part of
what is being tested.

Then write your own regression cases from real attack strings against your own
schema, and keep them in the test suite. Garak covers the general classes; only
you can test that your specific classifier still refuses to emit a label outside
its enum when the page title says to.

**Do not treat Garak output as a score to improve.** Probes are added over time,
so numbers move for reasons unrelated to your code. Pin the version and compare
runs against each other.

## Review questions

For any change touching this pipeline:

1. What is the full list of external sources that can reach the model here?
2. Is external text in a data channel, or is it concatenated into instructions?
3. Is the output schema-constrained and validated before use?
4. What can this path do if the model is fully compromised? List the
   capabilities explicitly.
5. Does output flow into any step where it could be read as an instruction?
6. Is any of this content excluded from personalisation or training by the
   privacy spec — and is that exclusion enforced in code?
