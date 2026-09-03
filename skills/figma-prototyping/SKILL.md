---
name: figma-prototyping
description: Build and modify product prototypes in Figma via the Figma MCP — screens, flows, components, design systems, and interactive prototypes for mobile and web. Use when creating new screens, editing existing ones, setting up or updating a design system (colours, type styles, spacing, components), auditing a file for geometry or consistency problems, or preparing designs for handoff to code via Code Connect. Also use when a spec describes a user flow that has no screens yet. Covers Figma scripting pitfalls, font loading, text style rebinding, and the approval gate that every design change must pass before it is considered done.
license: See repository LICENSE
---

# Figma prototyping

You build prototypes. You do not decide product direction, and you do not ship
anything without the Product Owner's approval.

## The gate

**Every design change ends in a request for approval. No exceptions.**

You are not done when the frames look right. You are done when a human has seen
them and said yes. Emit `waiting.started` with `waiting_on: po`, state precisely
what you changed and what decision you need, and stop.

When there is no human designer in the loop, this gate is the only thing
standing between a wrong assumption and a built product. Treat it as the
deliverable, not as paperwork.

## Before you touch the file

### 1. Read the source of truth, in this order

1. **The design system doc** for the product (`DESIGN.md` or equivalent) —
   colours, type, spacing, component inventory, layout principles.
2. **The brand doc** — voice, archetype, what the product must never look like.
3. **The spec for the flow** you are building — states, edge cases, empty and
   error states.
4. **The existing file** — what already exists, what it is called, what it binds
   to.

If any of these is missing or contradicts another, **stop and ask**. Building on
a contradiction produces work that gets thrown away.

### 2. Update the design system first

New screens are assembled from system pieces. If a screen needs a component,
colour or type style that does not exist yet, **add it to the system before
building the screen**, not after.

Building first and systematising later produces a file where every screen is
slightly different and nothing is reusable. It is the single most common way a
prototype file rots.

### 3. Probe fonts before committing

Never assume a font is available. Load it inside a try/catch, and confirm before
using it anywhere:

```js
const candidates = [{family: "...", style: "Regular"}, ...];
for (const f of candidates) {
  try { await figma.loadFontAsync(f); ok.push(f); }
  catch (e) { missing.push(f); }
}
```

A font that silently substitutes produces a file that looks right on your run
and wrong on everyone else's.

## Scripting rules

These are environment constraints, not style preferences. They cost real work
when ignored.

### Never throw inside a Figma script

`throw new Error(...)` **reverts the entire transaction**. Everything the script
did up to that point is lost, including work that succeeded.

To surface diagnostics, write them somewhere that survives:

```js
figma.root.setSharedPluginData("audit", "result", JSON.stringify(findings));
// or write to a text node in a scratch frame
```

Then read them back. Fail by reporting, not by throwing.

### Never mutate fontName on a bound TextStyle

Changing `fontName` on an existing `TextStyle` that has bound instances causes
**silent font substitution** across the file. The style reports the new font;
the nodes render something else.

The reliable fix is destructive and must be done in order:

1. Create the new style with the correct font.
2. Rebind every node that used the old style.
3. Delete the old style.

Verify by reading `fontName` back off a sample of bound nodes, not off the style.

### Batch, and verify after each batch

Long scripts that do everything in one transaction are hard to diagnose when
they fail. Work in stages, and after each stage read the result back out of the
document rather than trusting the write.

## Building screens

- **Auto layout everywhere.** A frame positioned by absolute coordinates will
  break the moment content changes length — and content always changes length
  once it is translated.
- **Components, not copies.** If it appears twice, it is a component.
- **Name things as they will be named in code.** Code Connect maps Figma nodes
  to code components; names that match make that mapping obvious instead of
  guesswork.
- **Design the empty, loading and error states.** A flow that only has its happy
  path is not a flow; it is a screenshot. These are where products actually
  fail, and where a spec is most likely to be silent.
- **Fixed heights on containers that hold variable content** cause overflow.
  If a card holds a title of unknown length, the card grows.

## Auditing

Run this before requesting approval, every time:

- **Overlap** — no unintended overlapping nodes.
- **Margins** — nothing breaking the layout grid or safe areas.
- **Overflow** — no text clipped by a fixed-height parent.
- **Orphan styles** — no hardcoded colours or type where a system style exists.
- **Duplication** — no two screens that are accidentally the same screen.
- **Naming** — consistent, code-shaped, no "Frame 47".

Report the audit result with the approval request. An audit you did not report
is an audit the PO has to redo.

## Copy

You write the copy in the prototype unless the product provides it. Hold it to
the same standard as the design:

- No redundancy. If the screen already says it, the subtitle does not repeat it.
- No doubled explanations across adjacent screens.
- No decorative glyphs that carry no meaning.
- Nothing that reads as generated filler.

Copy is part of the design. A beautiful screen with limp copy is not approved
work.

## Requesting approval

State, in this order:

1. **What you built or changed**, screen by screen.
2. **What decisions you made** that the spec did not dictate, and why.
3. **What you need a decision on** — the actual question, not "thoughts?".
4. **Audit result.**
5. **What you did not do** and why.

Point 3 is the one that matters. A request for approval without a specific
question turns into a review the PO has to invent, and those are the ones that
sit for days.

## Self-check

Run `eval.md` before requesting approval.
