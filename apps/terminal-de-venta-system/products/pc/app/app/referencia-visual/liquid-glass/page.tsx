import { redirect } from "next/navigation";

export const dynamic = "force-static";

export default function LiquidGlassRedirectPage() {
  redirect("/laboratorio-pc/referencia-visual/liquid-glass");
}
