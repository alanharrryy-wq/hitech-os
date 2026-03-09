import type { ReactNode } from "react";
import { DevConsoleProvider } from "../../components/dev-console/DevConsoleContext";

export default function DevLayout({ children }: { children: ReactNode }) {
  return <DevConsoleProvider>{children}</DevConsoleProvider>;
}
