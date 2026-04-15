import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { OrderCard } from "./OrderCard";
import { describe, test, expect, vi } from "vitest";

const mockUpdate = vi.fn(() => ({
  unwrap: () => Promise.resolve(),
}));

const mockDelete = vi.fn(() => ({
  unwrap: () => Promise.resolve(),
}));

vi.mock("../api/orderApi", () => ({
  useUpdateOrderStatusMutation: () => [mockUpdate],
  useDeleteOrderMutation: () => [mockDelete],
}));

vi.mock("../../../features/order/ui/OrderModal", () => ({
  OrderModal: () => <div>Modal</div>,
}));

describe("OrderCard", () => {
  const order = {
    id: "1",
    orderNumber: "123",
    totalAmount: 1000,
    deliveryAddress: "Москва",
    status: "NEW",
    user: { telegram: "testuser" },
  };

  test("отображает данные заказа", () => {
    render(<OrderCard order={order} />);

    expect(screen.getByText(/123/)).toBeInTheDocument();
    expect(screen.getByText(/1000/)).toBeInTheDocument();
  });

  test("изменение статуса вызывает API", async () => {
    render(<OrderCard order={order} />);

    fireEvent.mouseDown(screen.getByLabelText(/статус/i));
    fireEvent.click(screen.getAllByRole("option")[0]);

    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalled();
    });
  });

  test("удаление заказа", async () => {
    window.confirm = vi.fn(() => true);

    render(<OrderCard order={order} />);

    const buttons = screen.getAllByRole("button");
    const deleteBtn = buttons[1];

    fireEvent.click(deleteBtn);

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith(order.id);
    });
  });

  test("открытие telegram", () => {
    window.open = vi.fn();

    render(<OrderCard order={order} />);

    const buttons = screen.getAllByRole("button");
    fireEvent.click(buttons[0]); // telegram button

    expect(window.open).toHaveBeenCalledWith(
      "https://t.me/testuser",
      "_blank"
    );
  });
});