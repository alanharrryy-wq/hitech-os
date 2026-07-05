# ATLAS_MOBILE_OPTIONAL_ADDER_BOUNDARY_ROLLBACK

**Phase:** MOBILE_OPTIONAL_ADDER_BOUNDARY_PHASE_1

This rollback note keeps the optional-adder boundary explicit during Mobile UI reversions.

- Mobile supervisa.
- Tablet Solo vende sola.
- Mobile no es requisito para vender.
- Mobile no bloquea POS.
- PC y Mobile son adders opcionales.
- Cloudflare y soporte remoto son opcionales.
- Internet no es requisito para venta base Tablet Solo.

Rollback scope:

- Revert Mobile visual shell changes only.
- Preserve Tablet independence and POS continuity.
- Preserve real snapshot data flow and existing Mobile verifiers.
- Use the task backup and trash manifest to restore moved legacy visual files only if a rollback is required.
