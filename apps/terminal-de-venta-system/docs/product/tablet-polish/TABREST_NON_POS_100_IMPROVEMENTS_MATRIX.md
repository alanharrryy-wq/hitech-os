# TABREST_NON_POS 100 Improvements Matrix

Date: 2026-07-02

| # | Area | Improvement | Status |
|---:|---|---|---|
| 1 | Cobro | Restored light premium cobro direction after user correction. | Applied |
| 2 | Cobro | Scoped the cobro backdrop through a pure CSS-module local class. | Verified |
| 3 | Cobro | Kept cobro panels clear instead of dark themed. | Applied |
| 4 | Cobro | Preserved blue ready state on final payment button. | Verified |
| 5 | Cobro | Preserved amber insufficient-payment state on final payment button. | Verified |
| 6 | Cobro | Added cobro amount/state verifier with pure-selector coverage. | Applied |
| 7 | Docs | Created required initial status report. | Applied |
| 8 | Docs | Created required owner map JSON. | Applied |
| 9 | Docs | Created required surface plan. | Applied |
| 10 | Docs | Created required preexisting dirty-file ledger. | Applied |
| 11 | Home | Removed runtime panel from first view. | Applied |
| 12 | Home | Reduced first-view action model to six main access cards. | Applied |
| 13 | Home | Removed tool/routing-oriented wording. | Applied |
| 14 | Home | Removed backoffice wording from visible copy. | Applied |
| 15 | Home | Kept sale, inventory, tickets, returns, pending work, and license visible. | Applied |
| 16 | Home | Limited visible alerts to a small, useful set. | Applied |
| 17 | Home | Preserved local-sale autonomy in copy. | Applied |
| 18 | Home | Avoided exposing internal support routes. | Verified |
| 19 | Shell | Changed default kicker to PRISMA Tablet. | Applied |
| 20 | Shell | Changed brand small label to Tablet. | Applied |
| 21 | Shell | Kept topbar contextual rather than a second nav. | Verified |
| 22 | Shell | Kept bottom dock final-route only. | Verified |
| 23 | Nav | Renamed Sync dock label to Pendientes. | Applied |
| 24 | Nav | Kept `/events/outbox` out of final nav. | Verified |
| 25 | Nav | Kept `/prisma-pulse` out of final nav. | Verified |
| 26 | Nav | Kept lab routes out of final nav. | Verified |
| 27 | Nav | Kept `/settings/export` secondary. | Verified |
| 28 | Nav | Kept `/offline` secondary. | Verified |
| 29 | Shift | Replaced tablet-cashier default visible value. | Applied |
| 30 | Shift | Replaced informal caja-rusa copy. | Applied |
| 31 | Shift | Replaced servilleta joke copy. | Applied |
| 32 | Shift | Added active-state marker to open panel. | Applied |
| 33 | Shift | Added active-state marker to close panel. | Applied |
| 34 | Shift | Added active/inactive panel styling. | Applied |
| 35 | Shift | Preserved existing open endpoint. | Verified |
| 36 | Shift | Preserved existing close endpoint. | Verified |
| 37 | Shift | Kept cash math untouched. | Verified |
| 38 | Inventory | Verified stock export remains a closed details menu. | Verified |
| 39 | Inventory | Verified stock export has no default open state. | Verified |
| 40 | Inventory | Kept stock route as final inventory route. | Verified |
| 41 | Inventory | Kept catalog route secondary. | Verified |
| 42 | Inventory | Kept low-stock route secondary. | Verified |
| 43 | Sales | Converted contextual export to details. | Applied |
| 44 | Sales | Hid report actions while export details are closed. | Applied |
| 45 | Sales | Replaced old export card copy. | Applied |
| 46 | Sales | Preserved ticket list behavior. | Verified |
| 47 | Sales | Preserved search toolbar. | Verified |
| 48 | Sales Detail | Renamed technical diagnostic summary. | Applied |
| 49 | Sales Detail | Replaced technical evidence heading. | Applied |
| 50 | Sales Detail | Replaced endpoint/log wording in locked detail. | Applied |
| 51 | Returns | Preserved contextual return route. | Verified |
| 52 | Returns | Kept dynamic return route out of final nav. | Verified |
| 53 | Offline | Renamed route metadata away from outbox wording. | Applied |
| 54 | Offline | Replaced awkward hero opening copy. | Applied |
| 55 | Offline | Changed pending headline to send language. | Applied |
| 56 | Offline | Converted export section to details. | Applied |
| 57 | Offline | Hid export links until details open. | Applied |
| 58 | Offline | Converted diagnostic panel to details. | Applied |
| 59 | Offline | Hid diagnostic chips until details open. | Applied |
| 60 | Offline | Replaced export-evidence wording. | Applied |
| 61 | Sync | Changed success headline to pending language. | Applied |
| 62 | Sync | Changed pending headline to send language. | Applied |
| 63 | Sync | Replaced event-count dispatch copy with pending-count copy. | Applied |
| 64 | Sync | Replaced synchronization result wording with send-result wording. | Applied |
| 65 | Sync | Removed support-tool phrasing from hero. | Applied |
| 66 | Sync | Moved account/device cards behind details. | Applied |
| 67 | Sync | Moved catalog pull behind details. | Applied |
| 68 | Sync | Limited initial queue to 8 items with an explicit Ver todos control. | Verified |
| 69 | Sync | Moved the dock inline on `/sync` to avoid overlaying pending cards. | Verified |
| 70 | Sync | Kept refresh and retry actions available with per-action busy labels. | Verified |
| 71 | Sync | Changed partial PC dispatch from fake success to visible warning. | Verified |
| 72 | Sync | Renamed support details to additional detail. | Applied |
| 73 | Outbox | Replaced ACK visible label. | Applied |
| 74 | Outbox | Replaced Eventos locales panel title. | Applied |
| 75 | Outbox | Replaced raw event topic title with movement label. | Applied |
| 76 | Outbox | Removed aggregate ID from visible row detail. | Applied |
| 77 | Outbox | Replaced raw status with human status label. | Applied |
| 78 | Settings Export | Renamed event export labels to pending export labels. | Applied |
| 79 | Settings Export | Updated metadata description. | Applied |
| 80 | License | Replaced Refresh remoto wording. | Applied |
| 81 | License | Replaced synchronization category label. | Applied |
| 82 | License | Reworded config evidence label. | Applied |
| 83 | License | Reworded license file evidence label. | Applied |
| 84 | License | Verified readonly card marker remains. | Verified |
| 85 | License | Verified readonly refresh marker remains. | Verified |
| 86 | License | Verified no license action buttons are exposed. | Verified |
| 87 | Estado Operativo | Renamed PRISMA Pulse page metadata. | Applied |
| 88 | Estado Operativo | Renamed shell title to Estado operativo. | Applied |
| 89 | Estado Operativo | Replaced Visual OS kicker. | Applied |
| 90 | Estado Operativo | Replaced Pulse report title/status. | Applied |
| 91 | Estado Operativo | Replaced Pulse preview disabled title. | Applied |
| 92 | Estado Operativo | Replaced outbox-local panel copy. | Applied |
| 93 | Estado Operativo | Renamed Sync Outbox chart title. | Applied |
| 94 | Estado Operativo | Renamed Shift Pulse chart title. | Applied |
| 95 | Verifiers | Added non-POS copy verifier. | Applied |
| 96 | Verifiers | Added non-POS navigation verifier. | Applied |
| 97 | Verifiers | Added inventory/export secondary verifier. | Applied |
| 98 | Verifiers | Added sync pending-language, queue-preview, dock, and partial-dispatch verifier. | Applied |
| 99 | Verifiers | Added license human verifier. | Applied |
| 100 | Verifiers | Added interaction verifier and aggregate package script. | Applied |
