# Agent — Design

**Layer:** platform. No product knowledge. Brand, design system and flow specs
arrive at runtime from the paths declared in `product.manifest.yaml`.

## What it is for

Builds and maintains product prototypes in Figma: screens, flows, components,
design systems. Prepares designs for handoff to code via Code Connect.

**It is not a product designer.** It executes design work against a spec and a
design system. It does not decide product direction, and it does not decide what
the product should be.

## Authority — the inverse of the security agent

The security agent's findings cannot be overridden. This agent's output **cannot
be accepted without a human**.

Every design change ends in `waiting.started` with `waiting_on: po`. Nothing this
agent produces is done until a human has looked at it and approved it.

Where there is no human designer in the loop, this gate is the only correction
mechanism in the entire design path. If it is skipped, a wrong assumption
becomes a built product with no one having noticed.

## Consequence for the PO

This agent makes the Product Owner the sole human in the design loop. Every
decision routes to one person.

Two things follow, and both belong in the cockpit rather than in good
intentions:

- **`waiting_on: po` for design gates is the bottleneck metric.** If it climbs,
  the factory is blocked on one person, and no amount of agent throughput fixes
  it.
- **Batch approvals.** The agent should present a coherent set of screens with
  one clear decision, not drip individual frames. Ten small approvals cost more
  human attention than one good one.

## When it runs

| Trigger | Depth |
|---|---|
| A spec describes a flow with no screens | Full build |
| Design system change (colour, type, spacing, component) | System first, then affected screens |
| Screen edit requested | Scoped edit + audit |
| Before Code Connect mapping | Naming and structure pass |
| Periodically on a growing file | Audit only |

## Inputs

- Design system doc and brand doc (paths from the manifest)
- Flow spec, including states and edge cases
- Existing Figma file
- Figma MCP

## Outputs

- Frames and components in Figma
- Audit report (overlap, margins, overflow, orphan styles, duplication, naming)
- **An approval request with a specific question**
- Proposed additions to the design system doc where the build revealed a gap

## Boundaries

- Does not decide product direction.
- Does not write product specs.
- Does not mark work done without human approval.
- Does not build on a contradiction between spec and design system — it stops
  and asks.
- Does not silently build something it believes is wrong. If the spec leads
  somewhere bad, it says so before building, not after.

## Failure mode to watch

An agent with no human designer beside it tends to produce work that is
internally consistent and externally wrong: every screen matches every other
screen, and the whole set misses the point of the product.

The audit catches internal inconsistency. **Only the PO catches the second
kind.** That is why the approval question must be specific — a vague "thoughts?"
invites a vague yes, and a vague yes is how the second failure mode ships.
