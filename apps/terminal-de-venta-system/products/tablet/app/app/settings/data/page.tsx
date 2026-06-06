import { redirect } from "next/navigation";

export default function DeprecatedDataSettingsPage() {
  redirect("/settings/license");
}
