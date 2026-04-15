import { render, screen } from "@testing-library/react";
import { SellerRevenuePage } from "./SellerRevenuePage";
import { describe, test, expect, vi } from "vitest";

vi.mock("../../widgets/revenue/ui/RevenueStats", () => ({
  RevenueStats: () => <div>Stats</div>,
}));

vi.mock("../../widgets/revenue/ui/RevenueChart", () => ({
  RevenueChart: () => <div>Chart</div>,
}));

vi.mock("../../widgets/revenue/ui/CompletedOrders", () => ({
  CompletedOrders: () => <div>Orders</div>,
}));

describe("SellerRevenuePage", () => {
  test("рендерит страницу аналитики", () => {
    render(<SellerRevenuePage />);

    expect(screen.getByText(/аналитика и выручка/i)).toBeInTheDocument();
    expect(screen.getByText("Stats")).toBeInTheDocument();
    expect(screen.getByText("Chart")).toBeInTheDocument();
    expect(screen.getByText("Orders")).toBeInTheDocument();
  });
});