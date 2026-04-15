import { render, screen, fireEvent } from "@testing-library/react";
import { SellerDashboardPage } from "./SellerDashboardPage";
import { describe, test, expect, vi } from "vitest";

vi.mock("../../../widgets/filters/ui/Filters", () => ({
  Filters: () => <div>Filters</div>,
}));

vi.mock("../../../widgets/poductList/ui/ProductList", () => ({
  ProductList: () => <div>ProductList</div>,
}));

vi.mock("../../../features/product/ui/CreateProductModal", () => ({
  CreateProductModal: ({ open }) =>
    open ? <div>Modal Open</div> : null,
}));

describe("SellerDashboardPage", () => {
  test("рендерит основные блоки", () => {
    render(<SellerDashboardPage />);

    expect(screen.getByText("Filters")).toBeTruthy();
    expect(screen.getByText("ProductList")).toBeTruthy();
  });

  test("открывает модалку создания товара", () => {
    render(<SellerDashboardPage />);

    fireEvent.click(screen.getByText(/\+ добавить товар/i));

    expect(screen.getByText(/modal open/i)).toBeTruthy();
  });
});