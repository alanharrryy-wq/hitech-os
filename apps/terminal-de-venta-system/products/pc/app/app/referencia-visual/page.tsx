import { redirect } from "next/navigation";

export const dynamic = "force-static";

export default function ReferenciaVisualRedirectPage() {
  redirect("/laboratorio-pc/referencia-visual");
}
