import { render, screen } from "@testing-library/react";
import { RevenueChart } from "./RevenueChart";
import { describe, test, expect, vi } from "vitest";

vi.mock("../../../entities/order/api/orderApi", () => ({
  useGetRevenueQuery: vi.fn(),
}));

// ❗ мок recharts (иначе jsdom падает)
vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  LineChart: ({ children }: any) => <div>{children}</div>,
  Line: () => <div>Line</div>,
  XAxis: () => <div />,
  YAxis: () => <div />,
  Tooltip: () => <div />,
  CartesianGrid: () => <div />,
}));

import { useGetRevenueQuery } from "../../../entities/order/api/orderApi";

describe("RevenueChart", () => {
  test("загрузка", () => {
    (useGetRevenueQuery as any).mockReturnValue({
      isLoading: true,
    });

    render(<RevenueChart />);

    expect(screen.getByText(/загрузка графика/i)).toBeInTheDocument();
  });

  test("нет данных", () => {
    (useGetRevenueQuery as any).mockReturnValue({
      isLoading: false,
      data: [],
    });

    render(<RevenueChart />);

    expect(screen.getByText(/нет данных/i)).toBeInTheDocument();
  });

  test("рендер графика", () => {
    (useGetRevenueQuery as any).mockReturnValue({
      isLoading: false,
      data: [
        { date: "2024-01-01", revenue: 100 },
        { date: "2024-01-02", revenue: 200 },
      ],
    });

    render(<RevenueChart />);

    expect(screen.getByText("Line")).toBeInTheDocument();
  });
});