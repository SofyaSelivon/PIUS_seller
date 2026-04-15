import { render, screen, fireEvent } from "@testing-library/react";
import { OrdersFilters } from "./OrdersFilters";
import { describe, test, expect, vi } from "vitest";

describe("OrdersFilters", () => {
  test("меняет статус фильтра", () => {
    const setFilters = vi.fn();

    render(
      <OrdersFilters
        filters={{ status: "", page: 1, limit: 10 }}
        setFilters={setFilters}
      />
    );

    fireEvent.mouseDown(screen.getByLabelText(/статус/i));
    const option = screen.getAllByRole("option")[1];

    fireEvent.click(option);

    expect(setFilters).toHaveBeenCalled();
  });
});