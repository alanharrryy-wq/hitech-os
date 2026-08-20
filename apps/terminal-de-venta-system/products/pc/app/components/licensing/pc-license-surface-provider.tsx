"use client";

import { createContext, type ReactNode, useContext } from "react";

const PcLicenseNavigationContext = createContext(false);

export function PcLicenseSurfaceProvider({
  navigationAllowed,
  children
}: {
  navigationAllowed: boolean;
  children: ReactNode;
}) {
  return (
    <PcLicenseNavigationContext.Provider value={navigationAllowed}>
      {children}
    </PcLicenseNavigationContext.Provider>
  );
}

export function PcLicenseNavigationGate({
  children,
  fallback = null
}: {
  children: ReactNode;
  fallback?: ReactNode;
}) {
  const navigationAllowed = useContext(PcLicenseNavigationContext);
  return navigationAllowed ? <>{children}</> : <>{fallback}</>;
}
