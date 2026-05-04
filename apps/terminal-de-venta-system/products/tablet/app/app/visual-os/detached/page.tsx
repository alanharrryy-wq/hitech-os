import PrismaStudioProQaClient from "../PrismaStudioProQaClient";
import styles from "../prisma-studio-pro-qa.module.css";

export const metadata = {
  title: "PRISMA Studio Pro Detached",
  description: "Ventana separada del PRISMA Studio Pro QA 00R/00S."
};

export default function DetachedVisualOsPage() {
  return (
    <main className={styles.detachedPage} data-prisma-vos="studio-pro-detached" data-prisma-layer="shell">
      <PrismaStudioProQaClient defaultDetached={true} />
    </main>
  );
}
