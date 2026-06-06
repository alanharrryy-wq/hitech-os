import { redirect } from "next/navigation";

export const dynamic = "force-static";

export default function ChartLabRedirectPage() {
  redirect("/laboratorio-pc/chart-lab?preview=charts");
}
