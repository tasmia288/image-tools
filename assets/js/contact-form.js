/**
 * Contact form submission.
 *
 * Works with either FormSubmit or Web3Forms — the page supplies both endpoints,
 * and the field names are identical. The form also works with JavaScript off:
 * it is a plain POST to `action`, which lands on the provider's own
 * confirmation page. This script only upgrades that to an inline result, so the
 * visitor never leaves the site.
 *
 * This is the one place on the site that talks to a third party, and only when
 * someone actually presses Send. No provider script is loaded, and the
 * converters never touch it.
 */

const form = document.getElementById('contact-form');
const status = document.getElementById('form-status');

if (form && status) {
  const submitButton = form.querySelector('button[type="submit"]');
  const originalLabel = submitButton.textContent;

  const setStatus = (message, tone) => {
    status.textContent = message;
    status.className = tone ? `form-status is-${tone}` : 'form-status';
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) return;

    submitButton.disabled = true;
    submitButton.textContent = 'Sending…';
    setStatus('Sending your message…');

    try {
      // FormSubmit needs its /ajax/ endpoint to answer with JSON rather than
      // redirect; Web3Forms uses the same URL for both.
      const endpoint = form.dataset.ajaxAction || form.action;
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      const result = await response.json().catch(() => ({}));

      // Web3Forms reports success as a boolean, FormSubmit as the string "true".
      const succeeded = result.success === true || result.success === 'true';

      if (response.ok && succeeded) {
        form.reset();
        setStatus('Thanks — your message has been sent. We usually reply within a few days.', 'done');
      } else {
        setStatus(
          result.message
            ? `Your message could not be sent: ${result.message}`
            : 'Your message could not be sent. Please try again in a moment.',
          'error'
        );
      }
    } catch {
      // Offline, blocked by an extension, or the endpoint is unreachable.
      setStatus(
        'Your message could not be sent — check your connection and try again.',
        'error'
      );
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = originalLabel;
    }
  });
}
