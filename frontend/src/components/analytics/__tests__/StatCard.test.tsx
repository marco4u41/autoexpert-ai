import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatCard } from "../StatCard";

function MockIcon() {
  return <span data-testid="icon">X</span>;
}

describe("StatCard", () => {
  it("renders label and value", () => {
    render(<StatCard label="Vehiculos" value={1500} icon={<MockIcon />} />);
    expect(screen.getByText("Vehiculos")).toBeDefined();
    expect(screen.getByText((1500).toLocaleString())).toBeDefined();
  });

  it("renders string value without locale formatting", () => {
    render(<StatCard label="Estado" value="Online" icon={<MockIcon />} />);
    expect(screen.getByText("Online")).toBeDefined();
  });

  it("has role=status with aria-label", () => {
    render(<StatCard label="Vehiculos" value={42} icon={<MockIcon />} />);
    const el = screen.getByRole("status");
    expect(el.getAttribute("aria-label")).toBe("Vehiculos: 42");
  });

  it("renders subtitle when provided", () => {
    render(
      <StatCard
        label="Total"
        value={100}
        icon={<MockIcon />}
        subtitle="ultimos 30 dias"
      />,
    );
    expect(screen.getByText("ultimos 30 dias")).toBeDefined();
  });

  it("does not render subtitle when not provided", () => {
    const { container } = render(
      <StatCard label="Total" value={100} icon={<MockIcon />} />,
    );
    expect(container.querySelectorAll("p").length).toBe(2);
  });

  it("renders loading state with skeletons", () => {
    const { container } = render(
      <StatCard label="Loading" value={0} icon={<MockIcon />} isLoading />,
    );
    expect(container.querySelectorAll("div").length).toBeGreaterThan(1);
    expect(screen.queryByText("Loading")).toBeNull();
  });

  it("applies color-specific classes", () => {
    const { container } = render(
      <StatCard label="Test" value={1} icon={<MockIcon />} color="orange" />,
    );
    const outer = container.firstChild as HTMLElement;
    expect(outer.className).toContain("border-ax-accent-warning/20");
  });
});
