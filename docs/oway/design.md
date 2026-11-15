# Design
Created: 2026-11-15T12:30:00Z · Last edited: 2026-11-15T12:30:00Z

How the UIX team (LeadUIX) designs with you. From CGSpec's design path, the oway-ui-ux skill and CGM's cgm-uix. Design can take days; code is no longer the hard part.

## Principles

1. **Start from the problem, not the look.** LeadProduct has already written who it is for, what job they want done and how we will know it works (in 01-intent). UIX reads it before drawing and never redoes it; a gap goes back to LeadProduct. KeeperUIX watches that design versions and screens don't drift apart.
2. **The AI leads with real references.** It searches far more than you can, and brings up to 6 deliberately different references, each with a caption. You react: "this is mine", "not this", "mix 2 and 4". Sketching on a screenshot beats ranking options.
3. **Real pages, never generated pictures.** References and variations are real pages opened in a browser and screenshotted, and shown to you, not just saved on disk. A lucky AI screen is never polished into the product.
4. **Variations differ in mechanism.** When a direction is open: 2 or 3 versions of the key screen side by side that differ in structure, density or navigation, not in colour or button position. The AI iterates on the winner and throws the rest away.
5. **Show the right artifact for the question:** a journey for moving across screens, a state diagram for rules, a grey wireframe for placement, a side-by-side for direction, a clickable prototype for interaction.
6. **Name what you feel.** If you like an effect without knowing its name, the AI names it or asks for a screen recording.
7. **Classify a request by its effect, not its wording.** "Make this button blue" can be a behaviour change.

## The 8 layers, UX before UI

Each layer has a fixed deliverable and a list of what is deliberately left out.

| Layer | You see | Not yet |
| --- | --- | --- |
| 0 References + words | References, your images, the shared words | Any design of ours |
| 5a Register (locked early) | One paragraph: density, type feel, light or dark, mood, one accent, the signature element, what to avoid | Token values |
| 1 Task map | What each user does | Visuals |
| 2 Screen map + flows | Every screen and how you move between them | Layout |
| 3 Wireframe | Grey boxes with real labels and zone names | Colour, fonts, icons |
| 4 Behaviour | Clickable grey prototype, every state, test IDs | Final look |
| 5b Token sheet | Type scale, colours, spacing, radius, motion, each value with its source | Screens |
| 6 High fidelity | Real frontend screens with tokens applied | Layout changes |
| 7 Motion | Behaviours animated with motion tokens | New behaviours |

- Layers 0 to 4 stay a cheap grey prototype, because screens change many times. From layer 5, design is built in the real frontend, so nothing is rebuilt. The journeys written at layer 4 run unchanged on the real frontend; if it behaves differently, the build fails.
- A tweak inside approved tokens and zones is applied directly. Changing a zone, a flow or a token reopens that layer.

## Being good looking

- **Anti-slop.** The audit flags AI-default looks as warnings: untouched component-library look, unprompted purple, gradient text, neon glows, centred hero + three cards, cards inside cards, fake side stripes, low-contrast text. Usability breakers are errors.
- **Style packs.** The `oway-ui-ux` skill carries 117 tested MIT styles and themes with the anti-slop gates (`style_hub.py`, fetched once per machine); LeadUIX picks from them instead of inventing. The same skill has a light mode for om: references still come first, without the locked layers.
- **A screen is locked only after a different reviewer scores its screenshots** against the critique rubric: no score below 3, mean at least 3.5.
- **Visual proof comes from CI**, tied to the commit; video for scrolling and motion. A hand-attached image is never proof.

## Design systems

The AI may propose an existing design system, but only one it can check with scripts: an installable package with typed components, machine-readable tokens, lint rules if possible, a permissive license. AI agents that re-create a system from its website drift. For a look with no package, the tokens are extracted instead (the getdesign skill). A curated list helps, for example an "awesome design systems" list kept on the Platform.

## Versions

Each version lives in `_oway/design/versions/vN/` with its prototype, screenshots and a short note. A new version is cut only when a layer is locked. Each locked screen keeps a baseline (journeys + screenshots per state); a later difference fails unless you approve a new baseline.
