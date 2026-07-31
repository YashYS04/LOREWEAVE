/**
 * Global application store — Zustand.
 *
 * This is the root store file. Slice the store into separate files as the
 * application grows (e.g., store/ui.ts, store/user.ts) and compose them here.
 */
import { create } from "zustand";
import { devtools } from "zustand/middleware";

interface AppState {
  // ── UI ─────────────────────────────────────────────────────────────────────
  isSidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    (set) => ({
      isSidebarOpen: true,
      setSidebarOpen: (open) => set({ isSidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
    }),
    { name: "loreweave-app-store" }
  )
);
