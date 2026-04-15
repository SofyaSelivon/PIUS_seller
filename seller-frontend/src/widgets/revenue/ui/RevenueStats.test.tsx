import { render, screen } from "@testing-library/react";
import { RevenueStats } from "./RevenueStats";
import { describe, test, expect, vi } from "vitest";

vi.mock("../../../entities/order/api/orderApi", () => ({
  useGetTotalRevenueQuery: vi.fn(),
}));

import { useGetTotalRevenueQuery } from "../../../entities/order/api/orderApi";

describe("RevenueStats", () => {
  test("показывает загрузку", () => {
    (useGetTotalRevenueQuery as any).mockReturnValue({
      isLoading: true,
    });

    render(<RevenueStats />);

    expect(screen.getByText(/загрузка/i)).toBeInTheDocument();
  });

  test("показывает выручку", () => {
    (useGetTotalRevenueQuery as any).mockReturnValue({
      isLoading: false,
      data: { totalRevenue: 5000 },
    });

    render(<RevenueStats />);

    expect(screen.getByText(/общая выручка/i)).toBeInTheDocument();
    expect(screen.getByText(/5000/i)).toBeInTheDocument();
  });

  test("показывает 0 если нет данных", () => {
    (useGetTotalRevenueQuery as any).mockReturnValue({
      isLoading: false,
      data: null,
    });

    render(<RevenueStats />);

    expect(screen.getByText(/0/i)).toBeInTheDocument();
  });
});