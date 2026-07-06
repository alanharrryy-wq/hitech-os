# Customer Setup Journey Map

| step | api | table | service | verifier | status |
| --- | --- | --- | --- | --- | --- |
| setup link | /api/admin/customer-setups/create | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PASS |
| setup code | /api/admin/customer-setups/create | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PASS |
| QR | /api/admin/customer-setups/create | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PASS |
| claim | /api/customer/devices/claim | customer_setup_bundles | claimCustomerDevice | verify:tablet-claim/verify:pc-claim/verify:mobile-claim | PASS |
| activation | /api/admin/customer-setups/create | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PASS |
| slots | /api/admin/customer-setups/create | customer_device_claim_slots | createCustomerSetup | verify:customer-setup-full | PASS |
| portal | /api/customer/portal | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PASS |
| billing | /api/admin/customer-setups/create | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PARCIAL |
| renewal | /api/admin/customer-setups/create | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PARCIAL |
| grace | /api/admin/customer-setups/create | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PARCIAL |
| revoke | /api/admin/customer-setups/create | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PARCIAL |
| device replacement | /api/admin/customer-setups/create | customer_setup_bundles | createCustomerSetup | verify:customer-setup-full | PARCIAL |
| audit | /api/admin/customer-setups/create | audit_events | createCustomerSetup | verify:customer-setup-full | PASS |
