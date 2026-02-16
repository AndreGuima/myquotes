export const AVAILABLE_THEMES = ["light", "dark", "ocean"];

const DEFAULT_THEME = "light";
const THEME_STORAGE_KEY = "app_theme";

function normalizeTheme(theme) {
  return AVAILABLE_THEMES.includes(theme) ? theme : DEFAULT_THEME;
}

export function applyTheme(theme) {
  const normalized = normalizeTheme(theme);

  document.body.classList.remove(
    ...AVAILABLE_THEMES.map((name) => `theme-${name}`),
  );
  document.body.classList.add(`theme-${normalized}`);

  return normalized;
}

export function initializeTheme() {
  const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
  const normalized = applyTheme(storedTheme);
  localStorage.setItem(THEME_STORAGE_KEY, normalized);
  return normalized;
}

export function saveThemeLocally(theme) {
  const normalized = applyTheme(theme);
  localStorage.setItem(THEME_STORAGE_KEY, normalized);
  return normalized;
}

export function getLocalTheme() {
  return normalizeTheme(localStorage.getItem(THEME_STORAGE_KEY));
}
