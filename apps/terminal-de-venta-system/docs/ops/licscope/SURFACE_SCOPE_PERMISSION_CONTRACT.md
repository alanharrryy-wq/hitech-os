# Surface Scope Permission Contract

| surface | canRead | canWrite | canCreateSales | canManageLicenses | canManageDevices | canClaimDevice | canAdminInventory | canViewCustomerData | canViewTenantData | canViewSales | canViewAudit | forbiddenWrites | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tablet POS | sales,catalog,inventory,cash | YES scoped | true | false | true | false | false | true | true | true | license,device,business | sales,outbox,cash |  |
| PC/Admin | canonical,sales,inventory,licensing | YES scoped | false | true | true | true | true | true | true | true | tenant,business,admin | admin/licensing/sync |  |
| Mobile | snapshot,sales,stock,alerts | NO by default | false | false | false | false | true | true | true | false | tenant,business,supervisor | none by default |  |
| Chart Lab | runtime visual data | NO by default | false | false | false | false | false | false | false | false | runtime-readonly | none by default |  |
| Customer Portal | setup/license status | YES scoped | false | false | true | false | true | true | false | false | setupCode,deviceId | device claim/license refresh |  |
| 3160 / control plane | ops/licensing | YES scoped | false | true | true | false | true | true | true | true | admin | customer/license/device admin |  |
| Cloud licensing worker | licensing/setup/device | YES scoped | false | true | true | false | true | true | false | true | admin/customer setup | licensing/setup/device |  |
