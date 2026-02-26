/**
 * Theme Toggle Manager
 * Handles dark/light mode switching with localStorage persistence
 */

class ThemeManager {
  constructor() {
    this.html = document.documentElement;
    this.toggle = document.getElementById('theme-toggle');
    this.init();
  }

  init() {
    // Load saved theme on page load
    this.loadTheme();

    // Add click handler to toggle button
    if (this.toggle) {
      this.toggle.addEventListener('click', () => this.toggleTheme());
    }

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      const saved = localStorage.getItem('theme');
      if (!saved) {
        this.setTheme(e.matches);
      }
    });
  }

  loadTheme() {
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Prevent flash by adding no-transition class
    this.html.classList.add('no-transition');

    // Determine theme
    const isDarkMode = saved ? saved === 'dark' : prefersDark;
    this.setTheme(isDarkMode);

    // Remove no-transition class
    setTimeout(() => this.html.classList.remove('no-transition'), 100);
  }

  setTheme(isDark) {
    if (isDark) {
      this.html.classList.add('dark-mode');
    } else {
      this.html.classList.remove('dark-mode');
    }
  }

  toggleTheme() {
    const isDarkMode = this.html.classList.contains('dark-mode');
    const newTheme = !isDarkMode;
    this.setTheme(newTheme);
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
    console.log('Theme switched to:', newTheme ? 'dark' : 'light');
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new ThemeManager();
});
