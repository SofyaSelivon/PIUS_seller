import { render, screen } from "@testing-library/react";
import { CompletedOrders } from "./CompletedOrders";
import { describe, test, expect, vi } from "vitest";

vi.mock("../../../entities/order/api/orderApi", () => ({
  useGetCompletedOrdersQuery: vi.fn(),
}));

import { useGetCompletedOrdersQuery } from "../../../entities/order/api/orderApi";

describe("CompletedOrders", () => {
  test("загрузка", () => {
    (useGetCompletedOrdersQuery as any).mockReturnValue({
      isLoading: true,
    });

    render(<CompletedOrders />);

    expect(screen.getByText(/загрузка/i)).toBeInTheDocument();
  });

  test("нет заказов", () => {
    (useGetCompletedOrdersQuery as any).mockReturnValue({
      isLoading: false,
      data: [],
    });

    render(<CompletedOrders />);

    expect(
      screen.getByText(/нет завершённых заказов/i)
    ).toBeInTheDocument();
  });

  test("рендер заказов", () => {
    (useGetCompletedOrdersQuery as any).mockReturnValue({
      isLoading: false,
      data: [
        { id: "1", orderNumber: "123", totalAmount: 1000 },
      ],
    });

    render(<CompletedOrders />);

    expect(screen.getByText(/123/i)).toBeInTheDocument();
    expect(screen.getByText(/1000/i)).toBeInTheDocument();
  });
});