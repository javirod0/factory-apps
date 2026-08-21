# Report format

Keep it short. A long report is an unread report.

```markdown
## Security review — <scope>

**Verdict:** BLOCK | PASS WITH FINDINGS | PASS
**Scanners run:** gitleaks 8.x, semgrep 1.x (auto, owasp-top-ten), trivy 0.x
**Surfaces reviewed:** mobile / api / data-access / llm-pipeline

### CRITICAL
#### C1 — <one-line title>
- **Where:** path/to/file.ts:42
- **What:** what is wrong, in one or two sentences
- **Proof:** reproduction steps, or a failing test, or "hypothesis — not verified"
- **Blast radius:** who is affected and what they lose
- **Fix:** the specific change proposed
- **Verify:** how to confirm the fix worked

### HIGH
...

### MEDIUM
...

### LOW
...

### Threat model delta
Only for new surfaces. One line per STRIDE category.

### Not reviewed
Anything in scope that was not covered, and why.
```

## Rules

- **Ordered by severity.** Never by file, never by tool.
- **Every finding says whether it is verified or a hypothesis.** Do not blur
  this. An unverified finding presented as fact costs you credibility on the
  next one, and credibility is the only thing that makes a blocking verdict work.
- **"Not reviewed" is a required section.** Silence about a gap reads as
  coverage. If time ran out, the extension was flaky, or a scanner failed, say so.
- **No finding without a proposed fix.** If you cannot propose one, say what you
  would need in order to.
- **PASS is a real verdict.** Say it plainly when the change is clean. An agent
  that always finds something teaches people to discount it.
