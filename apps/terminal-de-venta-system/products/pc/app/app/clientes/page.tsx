import { CustomerWorkspace } from "@components/customers/customer-workspace";
import { getCustomerWorkspace } from "@/server/services/customer.service";

export const dynamic = "force-dynamic";

export default async function CustomersPage() {
  const workspace = await getCustomerWorkspace();
  return <CustomerWorkspace initialWorkspace={workspace} />;
}
