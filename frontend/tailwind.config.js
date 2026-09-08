/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        oil: {
          dark: '#0B0F17',
          darker: '#06090E',
          card: '#121824',
          border: '#1E293B',
          muted: '#64748B',
          accent: '#0284C7',
          accentGlow: '#38BDF8',
          gold: '#F59E0B',
          green: '#10B981',
          red: '#EF4444',
          orange: '#F97316'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}
