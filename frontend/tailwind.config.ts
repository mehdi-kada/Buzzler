import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    "./*.html"
  ],
  theme: {
    extend: {
      colors: {
        // Buzzler Brand Colors
        'buzzler': {
          'pink': '#dc2667',
          'orange': '#f97316',
          'pink-dark': '#be185d',
          'orange-dark': '#ea580c',
        },
        // Custom grays with better contrast
        'gray-850': '#1f2937',
        'gray-950': '#0f172a',
      },
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      backdropBlur: {
        'xs': '2px',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(220, 38, 103, 0.3)',
        'glow-lg': '0 0 40px rgba(220, 38, 103, 0.4)',
        'inner-glow': 'inset 0 0 20px rgba(220, 38, 103, 0.1)',
      },
      gradientColorStops: {
        'buzzler-start': '#dc2667',
        'buzzler-end': '#f97316',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    // Custom plugin for Buzzler utilities
    function({ addUtilities }: { addUtilities: (utilities: Record<string, any>) => void }) {
      const newUtilities = {
        '.text-gradient-buzzler': {
          'background': 'linear-gradient(90deg, #dc2667, #f97316)',
          '-webkit-background-clip': 'text',
          'background-clip': 'text',
          'color': 'transparent',
        },
        '.bg-gradient-buzzler': {
          'background': 'linear-gradient(135deg, #dc2667, #f97316)',
        },
        '.border-gradient-buzzler': {
          'border-image': 'linear-gradient(90deg, #dc2667, #f97316) 1',
        },
        '.glass-panel': {
          'background': 'rgba(255, 255, 255, 0.05)',
          'backdrop-filter': 'blur(10px)',
          'border': '1px solid rgba(255, 255, 255, 0.1)',
        },
        '.glass-card': {
          'background': 'rgba(255, 255, 255, 0.05)',
          'backdrop-filter': 'blur(10px)',
          'border': '1px solid rgba(255, 255, 255, 0.1)',
          'transition': 'all 0.3s ease-in-out',
        },
        '.glass-card:hover': {
          'border-color': 'rgba(220, 38, 103, 0.3)',
          'background': 'rgba(220, 38, 103, 0.05)',
        }
      }
      addUtilities(newUtilities)
    }
  ],
}

export default config
