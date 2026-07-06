from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class Contract:
    entity: str
    tables: tuple[str, ...]
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...] = ()
    production_blocking: bool = True

def c(entity: str, tables: tuple[str, ...], req: tuple[str, ...], opt: tuple[str, ...]=(), blocking: bool=True) -> Contract:
    return Contract(entity, tables, req, opt, blocking)

CONTRACTS = (
    c('tenant', ('Tenant','CommandTenant','Organization','Workspace'), ('id','slug','name')),
    c('business', ('Business','CommandBusiness','Company'), ('id','tenantId','name'), ('clientId',)),
    c('client', ('CommandClient','Client','CustomerAccount'), ('id','name'), ('businessId','status')),
    c('license', ('LicenseAssignment','License','ClientLicense'), ('id','clientId','status'), ('deviceId','expiresAt')),
    c('device', ('ManagedDevice','Device','ClaimedDevice'), ('id','deviceId'), ('clientId','businessId','roleCode','claimedAt')),
    c('store', ('Store','BusinessStore'), ('id','businessId','name')),
    c('terminal', ('Terminal','POSTerminal'), ('id','storeId'), ('deviceId','name')),
    c('cashier_user', ('User','Cashier','StaffUser'), ('id','role'), ('businessId','displayName')),
    c('cash_session', ('CashSession','RegisterSession'), ('id','terminalId','cashierId','openedAt'), ('closedAt',)),
    c('sale', ('Sale','SalesOrder','POSTransaction'), ('id','businessId','storeId','originDeviceId'), ('terminalId','cashSessionId','cashierId','totalCents','createdAt')),
    c('sale_line', ('SaleLine','SalesLine','SaleItem'), ('id','saleId','quantity'), ('productId','totalCents')),
    c('tender', ('SalePaymentTender','Tender','Payment'), ('id','saleId','kind','amountCents')),
    c('outbox', ('OutboxEvent','SyncOutbox','Outbox'), ('id','payloadJson'), ('aggregateId','createdAt','originDeviceId')),
    c('sync_checkpoint', ('SyncCheckpoint','ReplicationCheckpoint'), ('id','deviceId'), ('lastSyncedAt',)),
    c('canonical_projection', ('CanonicalSale','SaleProjection','CanonicalProjection'), ('id','sourceSaleId'), ('businessId','originDeviceId')),
    c('pc_scope', ('PcScope','AdminScope'), ('businessId',), ('storeId','role'), False),
    c('mobile_scope', ('MobileScope','SupervisorScope'), ('businessId',), ('storeId','role'), False),
)

def contracts_as_dicts() -> list[dict[str, Any]]:
    return [asdict(x) for x in CONTRACTS]
