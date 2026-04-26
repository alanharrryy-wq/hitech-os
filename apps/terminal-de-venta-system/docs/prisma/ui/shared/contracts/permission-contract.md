# Permission Contract

## Purpose

This contract defines how PRISMA models permissions across PC, Tablet, core modules, and plugins.

Permissions must be explicit, auditable, and mapped to user intent. No screen, plugin, or workflow may invent private permission rules outside this contract.

## Core rule

If an action can affect money, inventory, customer debt, fiscal state, production state, access, configuration, sync, or audit history, it requires an explicit permission.

## Permission naming pattern

Use this shape:

```text
domain.resource.action
```

Examples:

```text
sales.ticket.create
sales.ticket.cancel
sales.discount.manual
cash.session.open
cash.session.close
inventory.count.create
inventory.adjustment.approve
customer.credit.approve
customer.debt.override
membership.access.override
production.order.advance
plugin.activate
plugin.configure
sync.conflict.resolve
fiscal.stamp.retry
hardware.device.configure
```

## Permission families

| Family | Purpose |
|---|---|
| sales.* | Sales, tickets, returns, discounts |
| cash.* | Cash sessions, cash movements, cash cuts |
| inventory.* | Counts, adjustments, transfers, reservations |
| customer.* | Customer profile, debt, credit, portfolio |
| procurement.* | Suppliers, purchase orders, reception |
| order.* | Orders, quotes, service orders |
| membership.* | Memberships, access, renewals |
| production.* | Production orders, stages, material consumption |
| route.* | Field sales, delivery, route settlement |
| plugin.* | Plugin activation, configuration, lifecycle |
| sync.* | Queues, conflicts, retries |
| fiscal.* | Invoicing, stamping, fiscal retries |
| hardware.* | Devices, printers, scales, readers |
| admin.* | System configuration and governance |

## Required metadata per permission

| Field | Required | Description |
|---|---:|---|
| permission_id | Yes | Stable permission key |
| family | Yes | Permission family |
| description | Yes | Human explanation |
| risk_level | Yes | low, medium, high, critical |
| allowed_apps | Yes | pc, tablet, or both |
| audit_required | Yes | Whether audit is mandatory |
| offline_allowed | Yes | Whether action may run offline |
| override_allowed | Yes | Whether another role may authorize |
| owning_module | Yes | Canonical module owner |
| plugin_source | If plugin-owned | Plugin that introduced it |

## Risk levels

| Level | Meaning | Example |
|---|---|---|
| low | Read-only or harmless action | View product list |
| medium | Operational action with reversible impact | Create order draft |
| high | Affects money, inventory, customer balance, or workflow state | Cancel sale |
| critical | Affects fiscal, sync conflict, admin settings, plugin lifecycle, or irreversible action | Resolve sync conflict |

## Screen behavior

A screen must not simply hide danger. It must:

1. Hide actions the user cannot use.
2. Disable actions blocked by state.
3. Explain why a blocked action is blocked.
4. Show who can authorize it when applicable.
5. Emit an audit event when override is requested or granted.

## PC vs Tablet rules

| Surface | Responsibility |
|---|---|
| PC | Configure roles, permission bundles, plugin permissions, and audit policies |
| Tablet | Execute permitted operational actions and request overrides |

## Permission bundle examples

### Cashier

```text
sales.ticket.create
sales.ticket.read
cash.session.read
customer.read
inventory.stock.read
```

### Supervisor

```text
sales.ticket.cancel
sales.discount.manual
cash.session.open
cash.session.close
inventory.adjustment.request
customer.debt.override
```

### Admin

```text
plugin.configure
user.role.assign
sync.conflict.resolve
hardware.device.configure
fiscal.stamp.retry
```

## Plugin rule

A plugin can request permissions, but it cannot create an isolated permission universe.

Every plugin permission must either:

1. Map to an existing permission family.
2. Declare a new family through governance.
3. Provide migration notes if it replaces an older permission.

## Offline rule

A permission must explicitly declare whether it can operate offline.

Offline permission is not inherited. If a user can perform an action online, that does not automatically mean the action is allowed offline.

## Audit rule

Audit is mandatory for:

- manual discounts
- cancellations
- refunds
- inventory adjustments
- cash open and close
- credit approval
- debt override
- membership access override
- production order close
- plugin activation
- plugin deactivation
- sync conflict resolution
- fiscal retry
- hardware configuration
- role and permission changes

## Non-negotiables

- No free-text permission names.
- No plugin-only hidden permissions.
- No critical action without audit.
- No offline override unless the policy explicitly allows it.
- No role should bypass audit.
- No screen should hardcode business power outside this contract.

## Acceptance checklist

A new permission is accepted only if it declares:

- stable ID
- owning module
- risk level
- allowed app surfaces
- offline behavior
- audit requirement
- override behavior
- plugin origin if applicable
- migration impact if replacing another permission
