import { useEffect, useMemo, useState } from "react";
import preferencesService from "../services/preferencesService";
import { getLocalTheme, saveThemeLocally } from "../core/theme";
import { ThemeContext } from "./ThemeContext";

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(getLocalTheme);

  useEffect(() => {
    async function loadThemeFromPreferences() {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        const data = await preferencesService.get("theme");
        const serverTheme = data?.preferences?.theme;

        if (serverTheme) {
          const normalized = saveThemeLocally(serverTheme);
          setThemeState(normalized);
        }
      } catch {
        // Silently fall back to local theme.
      }
    }

    loadThemeFromPreferences();
  }, []);

  function setTheme(themeName) {
    const normalized = saveThemeLocally(themeName);
    setThemeState(normalized);
    return normalized;
  }

  const value = useMemo(() => ({ theme, setTheme }), [theme]);

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}
