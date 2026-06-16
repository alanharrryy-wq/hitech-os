# PC Sales Control branch layout

This change turns `/sales-control` into an executive branch-first sales view.

## Shape

- Header: title, current role, short description, and synchronization CTA.
- Global metrics: gross sales, net sales, tickets, average ticket, branches, tablets.
- Branch sections: one accordion per branch/sucursal.
- Tablet cards inside each branch.
- Ticket rows inside each branch.
- Ticket details are disclosed only when the user clicks a folio.
- Bottom-left `Agregar sucursal nueva` disclosure form prepares the data needed to link a new tablet through Sync.

## Scope

PC only:
- no Tablet POS visual changes
- no Mobile
- no Chart Lab
- no Prisma schema changes
- no process/port/dev-server actions

## Data policy

Sales are grouped by `Terminal.storeId` when possible, falling back to `CashSession.storeId` and then `Sucursal sin asignar`.
The form does not create database rows by itself; it routes to `/sync` with the entered context so linking can happen in the governed sync flow.
