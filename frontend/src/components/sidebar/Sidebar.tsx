import { useEffect, useState } from "react";
import { useChatStore } from "@/stores/chatStore";
import { useConversationStore } from "@/stores/conversationStore";
import { useAuthStore } from "@/stores/authStore";
import { GlassButton } from "@/components/design-system";
import { cn } from "@/utils/cn";

interface SidebarProps {
  view: "chat" | "dashboard";
  onNavigate: (view: "chat" | "dashboard") => void;
  isMobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function Sidebar({
  view,
  onNavigate,
  isMobileOpen = false,
  onMobileClose,
}: SidebarProps) {
  const { conversations, activeId, isLoading, loadConversations, setActive } =
    useConversationStore();
  const { clearMessages, loadMessages } = useChatStore();
  const { user } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);
  const isAdmin = user?.is_admin ?? false;

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  function handleNewChat() {
    clearMessages();
    setActive(null);
    onNavigate("chat");
    onMobileClose?.();
  }

  function handleNavigate(target: "chat" | "dashboard") {
    onNavigate(target);
    onMobileClose?.();
  }

  return (
    <>
      {/* Mobile backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden animate-ax-fade-in"
          onClick={onMobileClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          "flex-shrink-0 flex flex-col",
          "ax-glass border-r border-white/[0.06]",
          "transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]",
          collapsed ? "w-[4.5rem]" : "w-72",
          /* Mobile: overlay */
          "fixed inset-y-0 left-0 z-50 lg:relative",
          isMobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
        aria-label="Navegacion principal"
      >
        {/* ── Brand Header ── */}
        <div className={cn("flex-shrink-0 border-b border-white/[0.06]", collapsed ? "p-3" : "p-4")}>
          <div className={cn("flex items-center", collapsed ? "justify-center" : "gap-3 mb-4")}>
            <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-ax-accent-primary/20 to-ax-gold/10 flex items-center justify-center border border-ax-accent-primary/20">
              <svg className="h-5 w-5 text-ax-accent-primary/80" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM3.75 20.105V4.875A1.875 1.875 0 0 1 5.625 3h12.75A1.875 1.875 0 0 1 20.25 4.875v10.5A1.875 1.875 0 0 1 18.375 17.25H8.655l-3.46 2.595A.75.75 0 0 1 4 19.256Z" />
              </svg>
            </div>
            {!collapsed && (
              <div className="min-w-0 animate-ax-fade-in">
                <h1 className="ax-text-heading text-sm text-ax-text-primary truncate">AutoExpert AI</h1>
                <p className="ax-text-label text-ax-text-subtle text-[10px]">
                  Asistente Automotriz
                </p>
              </div>
            )}
          </div>

          {!collapsed && (
            <div className="space-y-2 animate-ax-fade-in">
              <GlassButton
                variant="primary"
                size="sm"
                className="w-full"
                onClick={handleNewChat}
                leftIcon={
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                  </svg>
                }
              >
                Nueva conversacion
              </GlassButton>

              {isAdmin && (
                <GlassButton
                  variant={view === "dashboard" ? "premium" : "ghost"}
                  size="sm"
                  className="w-full"
                  onClick={() => handleNavigate(view === "chat" ? "dashboard" : "chat")}
                  aria-pressed={view === "dashboard"}
                  aria-label={view === "chat" ? "Ir al Dashboard" : "Volver al Chat"}
                  leftIcon={
                    view === "chat" ? (
                      <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 0 0 6 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0 1 18 16.5h-2.25m-7.5 0h7.5m-7.5 0-1 3m8.5-3 1 3m0 0 .5 1.5m-.5-1.5h-9.5m0 0-.5 1.5" />
                      </svg>
                    ) : (
                      <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM3.75 20.105V4.875A1.875 1.875 0 0 1 5.625 3h12.75A1.875 1.875 0 0 1 20.25 4.875v10.5A1.875 1.875 0 0 1 18.375 17.25H8.655l-3.46 2.595A.75.75 0 0 1 4 19.256Z" />
                      </svg>
                    )
                  }
                >
                  {view === "chat" ? "Dashboard" : "Chat"}
                </GlassButton>
              )}
            </div>
          )}
        </div>

        {/* ── Conversations ── */}
        <nav
          className="flex-1 overflow-y-auto p-2 ax-scrollbar"
          aria-label="Conversaciones"
        >
          {isLoading ? (
            <div className="space-y-2 p-2">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-14 rounded-xl bg-white/[0.03] animate-ax-shimmer"
                />
              ))}
            </div>
          ) : conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 px-4">
              {!collapsed && (
                <>
                  <div className="w-10 h-10 rounded-xl bg-ax-surface-light flex items-center justify-center mb-3 border border-white/[0.04]">
                    <svg className="h-5 w-5 text-ax-text-subtle" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 0 1-.825-.242m9.345-8.334a2.126 2.126 0 0 0-.476-.095 48.64 48.64 0 0 0-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0 0 11.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
                    </svg>
                  </div>
                  <p className="ax-text-label text-ax-text-subtle text-xs text-center leading-relaxed">
                    Inicia una conversacion para comenzar
                  </p>
                </>
              )}
            </div>
          ) : (
            <ul className="space-y-0.5" role="list">
              {conversations.map((conversation) => (
                <li key={conversation.id}>
                  <button
                    onClick={() => {
                      setActive(conversation.id);
                      loadMessages(conversation.id);
                      onNavigate("chat");
                      onMobileClose?.();
                    }}
                    className={cn(
                      "w-full text-left rounded-xl px-3 py-2.5",
                      "transition-all duration-200 ease-out",
                      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ax-accent-primary/40 focus-visible:ring-offset-1 focus-visible:ring-offset-ax-bg-deep",
                      activeId === conversation.id
                        ? "bg-ax-accent-primary/[0.08] border border-ax-accent-primary/15 text-ax-text-primary"
                        : "border border-transparent text-ax-text-secondary hover:text-ax-text-primary hover:bg-white/[0.03]",
                    )}
                  >
                    {collapsed ? (
                      <span className="flex items-center justify-center">
                        <span className="w-2 h-2 rounded-full bg-ax-text-subtle shrink-0" />
                      </span>
                    ) : (
                      <>
                        <span className="block truncate text-sm font-medium font-ax-sans">
                          {conversation.title}
                        </span>
                        <span className="block truncate text-[10px] text-ax-text-subtle font-ax-mono mt-0.5">
                          {conversation.message_count} mensajes
                        </span>
                      </>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </nav>

        {/* ── Collapse Toggle (desktop) ── */}
        <div className="hidden lg:flex flex-shrink-0 border-t border-white/[0.06] p-2">
          <button
            onClick={() => setCollapsed((c) => !c)}
            className={cn(
              "flex items-center gap-2 w-full rounded-xl px-3 py-2",
              "text-ax-text-subtle hover:text-ax-text-secondary",
              "transition-all duration-200",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ax-accent-primary/40",
              collapsed && "justify-center",
            )}
            aria-label={collapsed ? "Expandir barra lateral" : "Colapsar barra lateral"}
          >
            <svg
              className={cn("h-4 w-4 transition-transform duration-300", collapsed && "rotate-180")}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 6l-6 6 6 6" />
            </svg>
            {!collapsed && (
              <span className="ax-text-label text-[10px] animate-ax-fade-in">Colapsar</span>
            )}
          </button>
        </div>
      </aside>
    </>
  );
}
