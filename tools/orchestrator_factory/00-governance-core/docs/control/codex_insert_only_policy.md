# Insert-Only and Wiring-Only Policy

## Intent
Execution agents should behave like precision operators. They may insert approved content and wire approved extension points. They may not redesign the machine because the redesign felt convenient in the moment.

## Insert-only examples
- add a section to an owned package document
- add a manifest entry already specified by the active run
- add a new contract file when that file is already named in the package deliverables or work packet

## Wiring-only examples
- register an approved route or screen into an already-defined map
- wire an approved service call into an already-defined client surface
- connect an approved environment variable into an already-defined configuration adapter

## Not allowed even if technically easy
- refactor unrelated areas for aesthetic cleanliness
- rename files or folders because a new pattern looks nicer
- move responsibilities across package boundaries
- introduce helper abstractions that alter architectural responsibility
- patch around constitutional ambiguity instead of escalating it
