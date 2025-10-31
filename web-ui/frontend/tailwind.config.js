/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Professional theme
        pro: {
          bg: '#ffffff',
          'bg-dark': '#1a1a1a',
          primary: '#4A90E2',
          accent: '#50C878',
        },
        // Terminal theme  
        terminal: {
          bg: '#000000',
          text: '#00ff00',
          accent: '#00ffff',
          border: '#00ff00',
        },
        // Avatar theme
        avatar: {
          bg: '#0f1419',
          'bg-secondary': '#1a1f2e',
          glow: '#60a5fa',
          accent: '#a78bfa',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' },
        }
      }
    },
  },
  plugins: [],
}

