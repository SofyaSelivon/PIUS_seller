import { render, screen, fireEvent } from "@testing-library/react";
import { Filters } from "./Filters";
import { describe, test, expect, vi } from "vitest";

describe("Filters", () => {
  test("изменяет поиск", () => {
    const setFilters = vi.fn();

    render(
      <Filters
        filters={{ search: "", category: "" }}
        setFilters={setFilters}
      />
    );

    fireEvent.change(screen.getByLabelText(/поиск/i), {
      target: { value: "iphone" },
    });

    expect(setFilters).toHaveBeenCalledWith({
      search: "iphone",
      category: "",
    });
  });

  test("изменяет категорию", () => {
    const setFilters = vi.fn();

    render(
      <Filters
        filters={{ search: "", category: "" }}
        setFilters={setFilters}
      />
    );

    fireEvent.mouseDown(screen.getByLabelText(/категория/i));

    fireEvent.click(screen.getByText(/электроника/i));

    expect(setFilters).toHaveBeenCalled();
  });
});