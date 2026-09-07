import { useAuthStore } from "@/stores/authStore";
import { useChatStore } from "@/stores/chatStore";
import { useGarageStore } from "@/stores/garageStore";
import { apiClient } from "@/api/client";

interface HeaderProps {
  view: "chat" | "dashboard";
  onToggleSidebar?: () => void;
}

export function Header({ view, onToggleSidebar }: HeaderProps) {
  const { user, logout } = useAuthStore();
  const { clearMessages } = useChatStore();
  const { clearGarage } = useGarageStore();

  async function handleLogout() {
    try {
      await apiClient.post("/auth/logout", {});
    } catch {
      // ignore — clear local state regardless
    }
    clearMessages();
    clearGarage();
    logout();
  }

  return (
    <header className="flex-shrink-0 flex items-center justify-between px-5 py-3 border-b border-white/[0.06]">
      <div className="flex items-center gap-3 min-w-0">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            className="lg:hidden flex items-center justify-center w-8 h-8 rounded-lg text-ax-text-muted hover:text-ax-text-primary hover:bg-white/[0.04] transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ax-accent-primary/40"
            aria-label="Abrir menu de navegacion"
          >
            <svg className="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          </button>
        )}

        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-ax-accent-success animate-ax-glow-pulse" aria-hidden="true" />
            <h1 className="ax-text-heading text-sm text-ax-text-primary truncate">
              {view === "chat" ? "AutoExpert AI" : "Dashboard"}
            </h1>
          </div>
          <p className="ax-text-label text-ax-text-subtle mt-0.5 hidden sm:block">
            {view === "chat"
              ? "Comparacion - Diagnostico - Recomendacion"
              : "Panel de control y metricas"}
          </p>
        </div>
      </div>

      {user && (
        <div className="flex items-center gap-3">
          <span className="ax-text-label text-ax-text-subtle text-xs hidden sm:block truncate max-w-[140px]">
            {user.email}
          </span>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-ax-text-muted hover:text-ax-text-primary hover:bg-white/[0.04] transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ax-accent-primary/40"
            aria-label="Cerrar sesion"
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9" />
            </svg>
            <span className="hidden sm:inline">Salir</span>
          </button>
        </div>
      )}
    </header>
  );
}
