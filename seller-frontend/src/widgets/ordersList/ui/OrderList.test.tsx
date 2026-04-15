import { render, screen } from "@testing-library/react";
import { OrdersList } from "./OrdersList";
import { describe, test, expect, vi } from "vitest";

const mockOrders = [
  {
    id: "1",
    orderNumber: "123",
    totalAmount: 1000,
    deliveryAddress: "Москва",
    status: "NEW",
  },
];

vi.mock("../../../entities/order/api/orderApi", () => ({
  useGetOrdersQuery: () => ({
    data: { orders: mockOrders },
  }),
}));

vi.mock("../../../entities/order/ui/OrderCard", () => ({
  OrderCard: ({ order }: any) => <div>Order {order.orderNumber}</div>,
}));

describe("OrdersList", () => {
  test("отображает список заказов", () => {
    render(<OrdersList filters={{}} />);

    expect(screen.getByText(/Order 123/i)).toBeInTheDocument();
  });
});