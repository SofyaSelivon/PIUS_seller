import { render, screen } from "@testing-library/react";
import { ProductList } from "./ProductList";
import { describe, test, expect, vi } from "vitest";

vi.mock("../../../entities/product/api/productApi", () => ({
  useGetMyProductsQuery: () => ({
    data: {
      items: [
        {
          id: 1,
          name: "iPhone",
          price: 1000,
          available: 5,
          category: "electronics",
          img: "img.jpg",
        },
      ],
    },
  }),
}));

vi.mock("../../../entities/product/ui/ProductCard", () => ({
  ProductCard: ({ product }) => <div>{product.name}</div>,
}));

describe("ProductList", () => {
  test("рендерит товары", () => {
    render(
      <ProductList
        filters={{ page: 1, limit: 12, search: "", category: "" }}
      />
    );

    expect(screen.getByText("iPhone")).toBeTruthy();
  });
});