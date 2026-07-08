# PRISMA Device Activation Canonical Contract

La activacion de dispositivos usa `shared/licensing/customer-setup-contract.ts`
para Setup Code, Device Claim y slots; usa `shared/runtime/device-identity.ts`
para identidad local.

## Campos minimos

- `deviceId`
- `surface`
- `role`
- `slot`
- `customerId`
- `businessId`
- `storeId`
- `terminalId`
- `licenseId`
- `claimStatus`
- `lastSeenAt`
- `secretsExposed:false`

No se reclama un slot desde soporte si falta Setup Code o si el plan no permite
la superficie.
