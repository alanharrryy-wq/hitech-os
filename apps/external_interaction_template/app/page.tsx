import { Benefits } from "@/components/prisma/Benefits";
import { CtaBand } from "@/components/prisma/CtaBand";
import { EcosystemHub } from "@/components/prisma/EcosystemHub";
import { Faq } from "@/components/prisma/Faq";
import { FlowBand } from "@/components/prisma/FlowBand";
import { Footer } from "@/components/prisma/Footer";
import { Hero } from "@/components/prisma/Hero";
import { Nav } from "@/components/prisma/Nav";

export default function HomePage() {
  return (
    <main className="site-shell">
      <Nav />
      <Hero />
      <EcosystemHub />
      <FlowBand />
      <Benefits />
      <Faq />
      <CtaBand />
      <Footer />
    </main>
  );
}
