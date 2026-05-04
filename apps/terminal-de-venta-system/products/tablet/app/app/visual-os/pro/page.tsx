import PrismaStudioProQaClient from "../PrismaStudioProQaClient";
import styles from "../prisma-studio-pro-qa.module.css";

export const metadata = {
  title: "PRISMA Studio Pro Isolated",
  description: "Modo pro aislado del Live Studio para calibración visual avanzada."
};

export default function VisualOsProPage() {
  return (
    <main className={styles.detachedPage} data-prisma-vos="studio-pro-isolated" data-prisma-layer="shell">
      <PrismaStudioProQaClient defaultDetached={true} />
    </main>
  );
}
