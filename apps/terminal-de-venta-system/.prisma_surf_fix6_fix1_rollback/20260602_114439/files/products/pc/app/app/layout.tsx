import "./globals.css";
import "./suppliers-ux-v08.css";
import "./prisma-visual-os-pc-binding.css";
import "./prisma-atmospheric-background.css";
import { PrismaAtmosphericBackground } from "./components/PrismaAtmosphericBackground";
import { pcMessages } from "@/lib/i18n/messages/es";

export const metadata = {
  title: pcMessages.metadata.title,
  description: pcMessages.metadata.description
};

const prismaSkinBootstrap = `
(function () {
  try {
    var key = "prisma.pc.skin";
    var value = window.localStorage.getItem(key);
    var preference = value === "light" || value === "dark" || value === "system" ? value : "light";
    var resolved = preference;
    if (preference === "system") {
      resolved = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    if (resolved !== "dark") resolved = "light";
    var root = document.documentElement;
    root.dataset.prismaSkin = resolved;
    root.dataset.prismaSurface = "pc-backoffice";
    root.dataset.theme = resolved === "light" ? "prisma-light" : "prisma-dark";
    root.dataset.prismaSkinPreference = preference;
  } catch (error) {
    document.documentElement.dataset.prismaSkin = "light";
    document.documentElement.dataset.prismaSurface = "pc-backoffice";
    document.documentElement.dataset.theme = "prisma-light";
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
        <PrismaAtmosphericBackground />
        <div className="prisma-app-content">{children}</div>
      </body>
    </html>
  );
}
