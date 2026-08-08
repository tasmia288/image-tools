// Keeps the footer copyright year current on pages that do not load the app.
var yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = String(new Date().getFullYear());
