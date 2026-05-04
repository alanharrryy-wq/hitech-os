import PrismaRealtimeBridgeClient from "./PrismaRealtimeBridgeClient";
import styles from "../prisma-studio-pro-qa.module.css";

export const metadata = {
  title: "PRISMA Studio Pro Bridge",
  description: "Cliente receptor SSE para validar cambios visuales realtime 00R/00S."
};

export default function RealtimeBridgePage() {
  return (
    <main className={styles.bridgePage} data-prisma-vos="studio-pro-bridge" data-prisma-layer="shell">
      <PrismaRealtimeBridgeClient />
    </main>
  );
}
