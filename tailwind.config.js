/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')

module.exports = {
  content: [
    "./src/templates/**/*.{html,js}",
    "./src/django_r2/upload.js/**/*.{jsx,js}"
  ],
  theme: {
    extend: {
        colors: {
          primary: {
            "50":"#eff6ff",
            "100":"#dbeafe",
            "200":"#bfdbfe",
            "300":"#93c5fd",
            "400":"#60a5fa",
            "500":"#3b82f6",
            "600":"#2563eb",
            "700":"#1d4ed8",
            "800":"#1e40af",
            "900":"#1e3a8a",
            "950":"#172554"
          }
        },
        animation: {
          'loading': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        },
        keyframes: {
          pulse: {
            '0%, 100%': { opacity: '1' },
            '50%': { opacity: '0.5' },
          },
        },
      },
      fontFamily: {
        'body': [
      'Inter', 
      'ui-sans-serif', 
      'system-ui', 
      '-apple-system', 
      'system-ui', 
      'Segoe UI', 
      'Roboto', 
      'Helvetica Neue', 
      'Arial', 
      'Noto Sans', 
      'sans-serif', 
      'Apple Color Emoji', 
      'Segoe UI Emoji', 
      'Segoe UI Symbol', 
      'Noto Color Emoji'
    ],
        'sans': [
      'Inter', 
      'ui-sans-serif', 
      'system-ui', 
      '-apple-system', 
      'system-ui', 
      'Segoe UI', 
      'Roboto', 
      'Helvetica Neue', 
      'Arial', 
      'Noto Sans', 
      'sans-serif', 
      'Apple Color Emoji', 
      'Segoe UI Emoji', 
      'Segoe UI Symbol', 
      'Noto Color Emoji'
    ]
      }
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}