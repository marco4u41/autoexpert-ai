import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChartDataTable } from "../ChartDataTable";

const sampleData = [
  { label: "SUV", value: 50 },
  { label: "Sedan", value: 30 },
];

describe("ChartDataTable", () => {
  it("shows 'Ver datos' button initially", () => {
    render(<ChartDataTable data={sampleData} caption="Test table" />);
    expect(screen.getByText("Ver datos")).toBeDefined();
  });

  it("toggles table visibility on button click", async () => {
    const user = userEvent.setup();
    render(<ChartDataTable data={sampleData} caption="Test table" />);

    const btn = screen.getByText("Ver datos");
    expect(btn.getAttribute("aria-expanded")).toBe("false");

    await user.click(btn);

    expect(screen.getByText("Ocultar datos")).toBeDefined();
    expect(screen.getByRole("table")).toBeDefined();
    expect(screen.getByText("SUV")).toBeDefined();
    expect(screen.getByText("50")).toBeDefined();
  });

  it("hides table on second click", async () => {
    const user = userEvent.setup();
    render(<ChartDataTable data={sampleData} caption="Test table" />);

    await user.click(screen.getByText("Ver datos"));
    await user.click(screen.getByText("Ocultar datos"));

    expect(screen.getByText("Ver datos")).toBeDefined();
  });

  it("renders secondary column when secondaryLabel is provided", async () => {
    const user = userEvent.setup();
    const dataWithSecondary = [
      { label: "SUV", value: 50, secondaryValue: 45000 },
    ];

    render(
      <ChartDataTable
        data={dataWithSecondary}
        caption="Test"
        secondaryLabel="Precio"
      />,
    );

    await user.click(screen.getByText("Ver datos"));
    expect(screen.getByText("Precio")).toBeDefined();
    expect(screen.getByText((45000).toLocaleString())).toBeDefined();
  });

  it("has caption for screen readers", async () => {
    const user = userEvent.setup();
    render(<ChartDataTable data={sampleData} caption="Accesibilidad" />);

    await user.click(screen.getByText("Ver datos"));
    expect(screen.getByText("Accesibilidad")).toBeDefined();
  });
});
