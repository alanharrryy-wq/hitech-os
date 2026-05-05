import { PrismaMobilePwaInstallPage } from "@/components/prisma-app";

export const metadata = {
  title: "PRISMA App offline | PWA",
  description: "Estado offline de PRISMA App Mobile PWA."
};

export default function PrismaAppOfflinePage() {
  return <PrismaMobilePwaInstallPage mode="offline" />;
}
