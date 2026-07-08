# Next Best Actions

1. Keep Cloudflare/D1/OAuth evidence current with the project-local Wrangler verifier.
2. Run admin HTTP mutation certification only when that separate gate is explicitly needed.
3. Do not rotate or print PRISMA_ADMIN_TOKEN unless an admin operation requires it.
4. Re-run local runtime surface readiness after port/app changes.
