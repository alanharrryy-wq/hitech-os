# 57_MUTATION_CLIENT_TEST_PLAN

## Test categories
1. contract and builder tests
2. source / target validation tests
3. mode policy tests
4. preview session lifecycle tests
5. preview diff determinism tests
6. commit/discard/revert orchestration tests
7. adapter routing tests
8. rejection-path tests
9. history / diagnostics tests
10. no-bypass architecture assertions where feasible

## Minimum smoke checks
- preview-only widget style update stays preview-only until commit
- rejected advanced-only mutation in safe mode preserves preview session integrity
- discard clears staged preview state without touching baseline
- revert plan only touches declared target scope
