import "./globals.css";
import "./prisma-tablet-light-premium-final.css";
import "./prisma-tablet-background-workbench.css";
import { tabletMessages } from "@/lib/i18n/messages/es";

export const metadata = {
  title: tabletMessages.metadata.title,
  description: tabletMessages.metadata.description
};

export default function RootLayout({ children }: { children: any }) {
  const prismaSkin = process.env.NEXT_PUBLIC_PRISMA_THEME === "prisma-dark" ? "dark" : "light";
  const prismaTheme = prismaSkin === "dark" ? "prisma-dark" : "prisma-light";

  return (
    <html lang="es-MX" data-prisma-skin={prismaSkin} data-prisma-surface="tablet-pos" data-theme={prismaTheme} data-prisma-visual-mode="background-workbench" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var k="prisma.pos.skin";var allowed={light:1,dark:1,system:1};var selected=localStorage.getItem(k);if(!allowed[selected])selected="light";var resolved=selected==="system"?(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"):selected;var root=document.documentElement;root.dataset.prismaSkin=resolved;root.dataset.prismaSurface="tablet-pos";root.dataset.prismaVisualMode="background-workbench";root.dataset.theme=resolved==="dark"?"prisma-dark":"prisma-light";}catch(e){var root=document.documentElement;root.dataset.prismaSkin="light";root.dataset.prismaSurface="tablet-pos";root.dataset.prismaVisualMode="background-workbench";root.dataset.theme="prisma-light";}})();`
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
