# eval.md — self-check before returning a report

Run every check. Any FAIL means fix the report before returning it.

## Coverage

- [ ] Every surface the change touches was identified, and its reference loaded.
- [ ] Scanners for those surfaces were actually run, with versions recorded.
- [ ] A "Not reviewed" section exists and is honest, including scanner failures.
- [ ] For new surfaces, a STRIDE pass exists with a line per category.

## Finding quality

- [ ] Every finding is labelled verified or hypothesis. No blurring.
- [ ] Every finding names a file and line, or explains why it cannot.
- [ ] Every finding states blast radius in terms of who loses what.
- [ ] Every finding has a proposed fix and a way to verify it.
- [ ] Findings that share a root cause are grouped, not repeated.
- [ ] Searched for siblings of each finding before reporting it.

## Triage discipline

- [ ] No raw scanner output pasted in. Everything triaged for reachability.
- [ ] Unreachable findings suppressed with a written reason and an owner, not
      silently dropped.
- [ ] Existing suppressions reviewed and still valid.

## Severity

- [ ] Severity reflects blast radius, not technical interest.
- [ ] Every hard-rule violation from SKILL.md is CRITICAL or HIGH.
- [ ] Where severity was uncertain, the higher level was chosen and said so.
- [ ] Verdict matches the findings: any CRITICAL or HIGH means BLOCK.

## Boundaries

- [ ] No fixes applied directly. Reported and proposed only.
- [ ] No exploit code beyond the minimum needed to prove a finding.
- [ ] Nothing tested that the product does not own.
- [ ] No production credentials used or requested.
- [ ] No finding softened for schedule reasons.

## Usefulness

- [ ] A competent implementer could act on this without asking a question.
- [ ] The report is short enough to be read in full.
- [ ] If the change is clean, it says PASS plainly rather than manufacturing a
      finding.

## Learning

- [ ] For each finding a scanner could have caught but did not, a rule was
      proposed for `.semgrep/`.
- [ ] If a human had to catch something this skill missed, an entry was proposed
      for the intervention log.
