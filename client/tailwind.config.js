/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          purple:       '#500082',
          'purple-dark': '#38005c',
          'purple-light': '#7a00c2',
          gold:         '#FFBE0A',
          'gold-light': '#FFD452',
          'dark-bg':    '#0d0014',
          'dark-card':  '#2a0050',
        },
      },
      boxShadow: {
        'purple-sm': '0 2px 8px 0 rgba(80,0,130,0.12)',
        'purple-md': '0 4px 24px 0 rgba(80,0,130,0.18)',
        'gold-glow': '0 0 16px 2px rgba(255,190,10,0.35)',
      },
    },
  },
  plugins: [],
}
