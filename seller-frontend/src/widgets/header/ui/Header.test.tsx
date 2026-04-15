import { render, screen, fireEvent } from "@testing-library/react";
import { Header } from "./Header";
import { describe, test, expect, vi } from "vitest";

const mockNavigate = vi.fn();

vi.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
}));

describe("Header", () => {
  test("отображает имя пользователя", () => {
    render(<Header userName="Анастасия" />);

    expect(screen.getByText("Анастасия")).toBeInTheDocument();
  });

  test("навигация по кнопкам", () => {
    render(<Header userName="User" />);

    fireEvent.click(screen.getByText(/главная/i));
    expect(mockNavigate).toHaveBeenCalledWith("/");

    fireEvent.click(screen.getByText(/заказы/i));
    expect(mockNavigate).toHaveBeenCalledWith("/orders");

    fireEvent.click(screen.getByText(/выручка/i));
    expect(mockNavigate).toHaveBeenCalledWith("/revenue");
  });
});