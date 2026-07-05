import { PrismaMobilePwaInstallPage } from "@/components/prisma-app";

type SearchParams = Promise<{ code?: string; setupCode?: string }> | { code?: string; setupCode?: string };

export const metadata = {
  title: "Instala PRISMA | Android o iPhone desde WhatsApp",
  description:
    "Landing premium de instalación PRISMA App para usuarios que abren el enlace desde WhatsApp en Android o iPhone."
};

export default async function PrismaAppInstallPage({ searchParams }: { searchParams?: SearchParams }) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  return <PrismaMobilePwaInstallPage setupCode={resolvedSearchParams.code || resolvedSearchParams.setupCode || ""} />;
}
