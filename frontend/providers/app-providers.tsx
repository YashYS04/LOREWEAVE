"use client";

import { QueryProvider } from "./query-provider";

interface AppProvidersProps {
  children: React.ReactNode;
}

/**
 * Root provider composition layer.
 *
 * All application-level providers are composed here in a single wrapper so
 * the root layout stays clean. Add new providers inside this component.
 */
export function AppProviders({ children }: AppProvidersProps) {
  return <QueryProvider>{children}</QueryProvider>;
}
