import { render, screen } from "@testing-library/react";
import Home from "@/app/page";

describe("Home page (scaffold)", () => {
  it("renders the product name", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: /civicpulse/i })).toBeInTheDocument();
  });

  it("flags itself as a scaffold", () => {
    render(<Home />);
    expect(screen.getByText(/scaffold placeholder/i)).toBeInTheDocument();
  });
});
