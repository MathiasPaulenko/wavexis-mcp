---
name: Feature request
about: Request a new tool or feature for WaveXisMCP
title: "[FEATURE] "
labels: enhancement
assignees: ''
---

## Feature description

A clear and concise description of the feature or tool you'd like.

## Use case

Why is this feature useful? What problem does it solve for LLM-driven browser automation?

## Proposed API

```python
class SomeInput(BaseModel):
    field: str = Field(..., description="...")
```

**Annotations**: `readOnlyHint: ...`, `destructiveHint: ...`, `idempotentHint: ...`, `openWorldHint: ...`

**Returns**: `{"status": "ok", ...}`

## Tier

Which capability tier does this belong to?

- [ ] Core
- [ ] Network
- [ ] Storage
- [ ] Emulation
- [ ] A11y
- [ ] Interactions
- [ ] DevTools
- [ ] Vision
- [ ] Video
- [ ] Testing
- [ ] Workflows
- [ ] Data
- [ ] Experimental

## Additional context

Any other context, references, or examples.
