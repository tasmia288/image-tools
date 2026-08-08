/**
 * Light/dark toggle.
 *
 * The page already follows the operating system by default via
 * prefers-color-scheme; this only records an explicit override. The chosen
 * value is applied by a tiny inline script in <head> so there is no flash of
 * the wrong theme before this module loads.
 *
 * Storage key "theme" holds "light" or "dark". Nothing else is stored, and it
 * is a preference, not an identifier — see the privacy policy.
 */

const STORAGE_KEY = 'theme';
const root = document.documentElement;

function currentTheme() {
  if (root.dataset.theme === 'light' || root.dataset.theme === 'dark') return root.dataset.theme;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme, button) {
  root.dataset.theme = theme;
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    /* Private browsing can block storage; the toggle still works for this visit. */
  }
  if (button) {
    button.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    button.setAttribute('aria-pressed', String(theme === 'dark'));
  }
}

const button = document.getElementById('theme-toggle');
if (button) {
  applyTheme(currentTheme(), button);
  button.addEventListener('click', () => {
    applyTheme(currentTheme() === 'dark' ? 'light' : 'dark', button);
  });
}
