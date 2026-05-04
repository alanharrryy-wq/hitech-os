import { Benefits } from "@/components/prisma/Benefits";
import { CtaBand } from "@/components/prisma/CtaBand";
import { Faq } from "@/components/prisma/Faq";
import { FlowBand } from "@/components/prisma/FlowBand";
import { Footer } from "@/components/prisma/Footer";
import { Hero } from "@/components/prisma/Hero";
import { Nav } from "@/components/prisma/Nav";
import { TriAppModel } from "@/components/prisma/TriAppModel";
import { VerticalCards } from "@/components/prisma/VerticalCards";

export default function HomePage() {
  return (
    <main className="site-shell">
      <Nav />
      <Hero />
      <TriAppModel />
      <VerticalCards />
      <FlowBand />
      <Benefits />
      <Faq />
      <CtaBand />
      <Footer />
    </main>
  );
}
