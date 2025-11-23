// static/js/theme.js
document.addEventListener('DOMContentLoaded', () => {
    const doc = document.documentElement;
    const currentTheme = localStorage.getItem('theme') || 'light';

    // ALWAYS apply the saved theme on page load, regardless of whether switcher exists
    doc.setAttribute('data-theme', currentTheme);

    // Only set up the switcher if it exists on this page
    const themeSwitcher = document.getElementById('theme-switcher');
    if (themeSwitcher) {
        // Set the dropdown to match the current theme
        themeSwitcher.value = currentTheme;

        // Listen for changes on the dropdown
        themeSwitcher.addEventListener('change', (event) => {
            const selectedTheme = event.target.value;
            doc.setAttribute('data-theme', selectedTheme);
            localStorage.setItem('theme', selectedTheme);
        });
    }
});