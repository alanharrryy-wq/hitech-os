# 74_BRIDGE_INTEGRATION_ACCEPTANCE

The integration is acceptable only if the following remain true:

- composer-originated writes still route through `runtime-mutation-bridge`
- preview and commit stay semantically distinct
- rejection paths are explicit
- mutation targets stay typed and scoped
- the pack does not reclassify debug tooling as authoring authority
- verification evidence is available after installation
