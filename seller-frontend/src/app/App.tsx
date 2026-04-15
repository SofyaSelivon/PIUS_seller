import { AppRouter } from "./providers/router";
import { MainLayout } from "./layouts/MainLayout";
import { useEffect } from "react";

function App() {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
      localStorage.setItem("token", token);

      window.history.replaceState({}, document.title, "/");
    }
  }, []);

  return (
    <MainLayout>
      <AppRouter />
    </MainLayout>
  );
}

export default App;
