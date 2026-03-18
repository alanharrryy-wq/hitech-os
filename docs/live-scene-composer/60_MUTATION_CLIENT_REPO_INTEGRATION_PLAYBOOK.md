# 60_MUTATION_CLIENT_REPO_INTEGRATION_PLAYBOOK

## Suggested landing zone
- docs -> `docs/live-scene-composer/`
- reference seam -> `tools/live-scene-composer/mutation-client-bridge-preview-commit-pack-v1/`
- optional mirrored source -> composer src root under `mutation-client/`

## Integration rhythm
1. stage docs and seam
2. review contracts
3. wire source builders into real surface handlers
4. point runtime-facing operations toward actual bridge entrypoints
5. add repo-local tests around allowed mutation types
6. validate no direct runtime mutation shortcuts reappear
