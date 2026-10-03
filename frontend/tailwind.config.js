/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./admin.html",
    "./assets/js/**/*.js",
    "./js/**/*.js",
    "./**/*.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Original brand colors
        'primary-red': '#D62828',
        'primary-blue': '#1E4A8B',          // ORIGINAL - vratio sam
        'secondary-blue': '#003366',         // ORIGINAL - dark blue
        'secondary-silver': '#C0C0C0',
        'secondary-gold': '#FFD700',
        'neutral-light': '#F8FAFC',
        'neutral-dark': '#1A365D',
        // Semantic colors (za notifikacije i status)
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'info': '#3B82F6',
        'red-dark': '#B22222',
        'blue-dark': '#001F3F',
      },
      fontFamily: {
        'sans': ['Montserrat', 'Inter', 'sans-serif'],
      },
      keyframes: {
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'slide-in': {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
      animation: {
        'scale-in': 'scale-in 0.2s ease-out',
        'slide-in': 'slide-in 0.3s ease-out',
      },
    },
  },
  plugins: [],
}