import "./globals.css";
import "./suppliers-ux-v08.css";
import "./prisma-visual-os-pc-binding.css";
import "./prisma-atmospheric-background.css";
import { PrismaAtmosphericBackground } from "./components/PrismaAtmosphericBackground";
import { pcMessages } from "@/lib/i18n/messages/es";
import { PrismaSurfFix6LifecycleRuntime } from "./prisma-surf-fix6-lifecycle-runtime";
import { PrismaDevIssueBadgeCleaner } from "./prisma-dev-issue-badge-cleaner";

export const metadata = {
  title: pcMessages.metadata.title,
  description: pcMessages.metadata.description
};

const prismaSkinBootstrap = `
(function () {
  try {
    var root = document.documentElement;
    root.dataset.prismaSkin = "light";
    root.dataset.prismaSurface = "pc-backoffice";
    root.dataset.theme = "prisma-light";
    root.dataset.prismaSkinPreference = "light";
  } catch (error) {
    document.documentElement.dataset.prismaSkin = "light";
    document.documentElement.dataset.prismaSurface = "pc-backoffice";
    document.documentElement.dataset.theme = "prisma-light";
    document.documentElement.dataset.prismaSkinPreference = "light";
  }
})();
`;

export default function RootLayout({ children }: { children: any }) {
  return (
    <html
      lang="es-MX"
      data-theme="prisma-light"
      data-prisma-skin="light"
      data-prisma-skin-preference="light"
      data-prisma-surface="pc-backoffice"
      data-prisma-visual-os="PC_DENSE_ADMIN"
      data-prisma-vos-binding="00J"
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: prismaSkinBootstrap }} />
      </head>
      <body>
        <PrismaDevIssueBadgeCleaner />
        <PrismaSurfFix6LifecycleRuntime />
        <PrismaAtmosphericBackground />
        <div className="prisma-app-content">{children}</div>
      </body>
    </html>
  );
}
