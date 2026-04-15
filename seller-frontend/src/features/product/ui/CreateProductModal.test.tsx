import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { CreateProductModal } from "./CreateProductModal";
import { describe, test, expect, vi } from "vitest";

const mockCreate = vi.fn();

vi.mock("../../../entities/product/api/productApi", () => ({
  useCreateProductMutation: () => [mockCreate],
}));

describe("CreateProductModal", () => {
  test("валидация обязательных полей", async () => {
    window.alert = vi.fn();

    render(<CreateProductModal open={true} onClose={() => {}} />);

    fireEvent.click(screen.getByText(/создать/i));

    expect(window.alert).toHaveBeenCalledWith(
      "Заполни обязательные поля"
    );
  });

  test("успешное создание товара", async () => {
    const onClose = vi.fn();

    render(<CreateProductModal open={true} onClose={onClose} />);

    fireEvent.change(screen.getByLabelText(/название/i), {
      target: { value: "iPhone" },
    });

    fireEvent.change(screen.getByLabelText(/цена/i), {
      target: { value: "1000" },
    });

    fireEvent.change(screen.getByLabelText(/количество/i), {
      target: { value: "5" },
    });

    fireEvent.mouseDown(screen.getByLabelText(/категория/i));
    fireEvent.click(screen.getAllByRole("option")[0]);

    fireEvent.click(screen.getByText(/создать/i));

    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });
});