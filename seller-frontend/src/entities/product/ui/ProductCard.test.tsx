import { render, screen, fireEvent } from "@testing-library/react";
import { ProductCard } from "./ProductCard";
import { describe, test, expect, vi } from "vitest";

vi.mock("../../../features/product/ui/ProductModal", () => ({
  ProductModal: ({ open }) =>
    open ? <div>Modal</div> : null,
}));

describe("ProductCard", () => {
  const product = {
    id: 1,
    name: "iPhone",
    price: 1000,
    available: 5,
    category: "electronics",
    img: "img.jpg",
  };

  test("рендерит данные товара", () => {
    render(<ProductCard product={product} />);

    expect(screen.getByText("iPhone")).toBeTruthy();
    expect(screen.getByText(/1000/i)).toBeTruthy();
    expect(screen.getByText(/остаток/i)).toBeTruthy();
  });

  test("открывает модалку по клику", () => {
    render(<ProductCard product={product} />);

    fireEvent.click(screen.getByText("iPhone"));

    expect(screen.getByText("Modal")).toBeTruthy();
  });
});