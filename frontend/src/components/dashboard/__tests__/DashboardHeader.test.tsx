import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { DashboardHeader } from "../DashboardHeader";
import { useAnalyticsStore } from "@/stores/analyticsStore";

vi.mock("@/stores/analyticsStore");

const mockUseAnalyticsStore = vi.mocked(useAnalyticsStore);

function setupStore(overview: unknown = null, isLoading = false) {
  const storeState = {
    overview,
    isLoading,
    errors: {
      overview: null,
      byType: null,
      byFuel: null,
      byTransmission: null,
      byYear: null,
      priceDistribution: null,
      brandRanking: null,
    },
  };
  mockUseAnalyticsStore.mockImplementation(
    ((selector: (s: typeof storeState) => unknown) => selector(storeState)) as typeof useAnalyticsStore,
  );
}

describe("DashboardHeader", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders greeting and date", () => {
    setupStore({
      vehicles: { total_vehicles: 100, avg_price: 25000, total_brands: 10, total_models: 50 },
      conversations: { total_conversations: 5, total_messages: 20, avg_messages_per_conversation: 4 },
    });

    render(<DashboardHeader />);

    const hour = new Date().getHours();
    const expectedGreeting = hour < 12 ? "Buenos dias" : hour < 19 ? "Buenas tardes" : "Buenas noches";
    expect(screen.getByText(new RegExp(expectedGreeting))).toBeDefined();
    expect(screen.getByText("Administrador")).toBeDefined();
  });

  it("renders four StatCards when overview is loaded", () => {
    setupStore({
      vehicles: { total_vehicles: 47030, avg_price: 18500, total_brands: 40, total_models: 200 },
      conversations: { total_conversations: 12, total_messages: 48, avg_messages_per_conversation: 4 },
    });

    render(<DashboardHeader />);

    expect(screen.getByText("Total Vehiculos")).toBeDefined();
    expect(screen.getByText((47030).toLocaleString())).toBeDefined();
    expect(screen.getByText("Conversaciones")).toBeDefined();
    expect(screen.getByText("12")).toBeDefined();
    expect(screen.getByText("Marcas")).toBeDefined();
    expect(screen.getByText("40")).toBeDefined();
    expect(screen.getByText("Precio Promedio")).toBeDefined();
  });

  it("renders skeleton when isLoading and no overview", () => {
    setupStore(null, true);

    const { container } = render(<DashboardHeader />);
    const skeletons = container.querySelectorAll(".animate-ax-shimmer");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("shows N/A for null avg_price", () => {
    setupStore({
      vehicles: { total_vehicles: 100, avg_price: null, total_brands: 5, total_models: 10 },
      conversations: { total_conversations: 0, total_messages: 0, avg_messages_per_conversation: 0 },
    });

    render(<DashboardHeader />);
    expect(screen.getByText("N/A")).toBeDefined();
  });

  it("has tabIndex=-1 on header for focus management", () => {
    setupStore({
      vehicles: { total_vehicles: 100, avg_price: 1000, total_brands: 5, total_models: 10 },
      conversations: { total_conversations: 0, total_messages: 0, avg_messages_per_conversation: 0 },
    });

    render(<DashboardHeader />);
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading.getAttribute("tabindex")).toBe("-1");
  });
});
