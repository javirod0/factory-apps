# Tooling

Six tools. All open source. All emit SARIF or JSON so findings land in the
GitHub Security tab without an Advanced Security licence.

| Tool | Layer | Where it runs |
|---|---|---|
| Gitleaks | Secrets — broad and fast | pre-commit, every PR, weekly full history |
| TruffleHog | Secrets — verifies which are live | CI |
| Semgrep CE | SAST | every PR |
| Trivy | Dependencies, containers, IaC | every PR + nightly |
| mobsfscan | Mobile-specific SAST | every PR touching mobile |
| Garak | LLM weakness probing | scheduled + when prompts change |

## Why two secret scanners

They do different jobs. Gitleaks is cheap enough to run on every commit before
it exists; TruffleHog authenticates against providers to tell you whether a
found secret is actually live, which is what decides whether you are rotating
credentials at 2am or filing a ticket.

Volume matters more than usual on an agent-driven project: throughput of code
per hour is much higher than a human-only team, and secrets reaching git scale
with the number of changes, not with carefulness.

## Gitleaks

```bash
# Pre-commit hook — must stay under a second
gitleaks protect --staged --redact

# CI, current diff
gitleaks detect --source . --log-opts="origin/main..HEAD" --redact \
  --report-format sarif --report-path gitleaks.sarif

# Weekly, whole history
gitleaks detect --source . --redact --report-format sarif \
  --report-path gitleaks-history.sarif
```

A hit in history is not resolved by deleting the line. The credential is
compromised: **rotate first, then clean history.** Report it as CRITICAL until
rotation is confirmed.

## TruffleHog

```bash
trufflehog git file://. --since-commit main --only-verified --json
```

`--only-verified` is the point of using it. Verified findings are CRITICAL and
require immediate rotation. Unverified findings still get reviewed, but they
belong in the Gitleaks triage flow.

## Semgrep CE

```bash
semgrep --config=auto --sarif --output=semgrep.sarif
semgrep --config=p/secrets --config=p/owasp-top-ten --sarif --output=semgrep-sec.sarif
```

Write project rules for the classes of bug that matter in this codebase and put
them in `.semgrep/`. Every time you find a bug by hand that a rule could have
caught, write the rule. That is how the agent gets stronger over time instead of
repeating the same review.

## Trivy

```bash
trivy fs --scanners vuln,secret,misconfig --format sarif --output trivy.sarif .
trivy fs --severity HIGH,CRITICAL --exit-code 1 .
```

Fail the build only on HIGH and CRITICAL. Failing on everything trains people to
ignore the gate, which is worse than not having one.

## mobsfscan

Use **mobsfscan**, not the full MobSF server, in CI. It is a lightweight CLI
over Java, Kotlin, Swift and Objective-C source, built on semgrep and pattern
matching, and it emits SARIF.

```bash
mobsfscan --sarif -o mobsfscan.sarif ./apps/mobile
```

The full MobSF server is a separate, occasional pre-release step — see
`mobile-native.md`.

## Garak

```bash
garak --target_type openai_compatible --target_name <model> \
      --probes promptinject,encoding,leakreplay --config fast
```

Garak probes for prompt injection, data leakage, jailbreaks and related
weaknesses. Its indirect prompt injection probes are the ones that matter for
any pipeline that ingests external text.

**Do not treat Garak scores as a benchmark or a KPI.** The project adds and
improves probes continuously, so scores drift downward over time independently
of your code. Use it to detect regressions between runs on the same version,
pinned.

## Suppressions

Every suppression carries a reason and an owner in the same commit:

```
# nosemgrep: rule-id — unreachable: input is an enum validated at the boundary (see X). @owner
```

An unexplained suppression is itself a HIGH finding. Audit all suppressions
before each release.

## Gate configuration

- CRITICAL or HIGH from any tool → build fails.
- MEDIUM → recorded, does not fail.
- Agents never hold production credentials. Scanners run against source and
  build artifacts, never against production.
- SARIF from every tool uploads to the GitHub Security tab so findings appear
  where the team already looks.
