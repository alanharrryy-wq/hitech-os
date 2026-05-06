import type { Metadata } from "next";
import { Footer } from "@/components/prisma/Footer";
import { Nav } from "@/components/prisma/Nav";
import { VerticalPage } from "@/components/prisma/VerticalPage";
import { seo } from "@/content/seo";

export const metadata: Metadata = seo.field;

export default function Page() {
  return (
    <main className="site-shell">
      <Nav />
      <VerticalPage slug="field" />
      <Footer />
    </main>
  );
}
