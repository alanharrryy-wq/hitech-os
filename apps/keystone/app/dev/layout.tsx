import type { ReactNode } from "react";
import { DevConsoleProvider } from "../../components/dev-console/DevConsoleContext";
import { DevConsole } from "../../components/dev-console/DevConsole";

export default function DevLayout({ children }: { children: ReactNode }) {
  return (
    <DevConsoleProvider>
      {children}
      <DevConsole />
    </DevConsoleProvider>
  );
}
