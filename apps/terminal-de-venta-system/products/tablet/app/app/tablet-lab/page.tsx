import { TabletLabAutoStudio } from "./components/TabletLabAutoStudio";
import styles from "./TabletLabCapsule.module.css";

export default function TabletLab() {
  return (
    <main className={styles.immersiveRoute} data-component="TabletLabPage" data-surface="tablet-lab" data-tabctl4="minimal-containers-transparent-zero">
      <TabletLabAutoStudio />
    </main>
  );
}
