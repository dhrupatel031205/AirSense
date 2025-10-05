/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./*/templates/**/*.html",
    "./static/**/*.js",
    "./*/static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        // Air Quality Index Colors
        'aqi-good': '#00e400',
        'aqi-moderate': '#ffff00',
        'aqi-unhealthy-sensitive': '#ff7e00',
        'aqi-unhealthy': '#ff0000',
        'aqi-very-unhealthy': '#8f3f97',
        'aqi-hazardous': '#7e0023',
        
        // Custom brand colors
        'primary': {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        'secondary': {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'Noto Sans', 'sans-serif'],
        'mono': ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'air-quality-pattern': "url('data:image/svg+xml,%3Csvg width=\"60\" height=\"60\" viewBox=\"0 0 60 60\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cg fill=\"none\" fill-rule=\"evenodd\"%3E%3Cg fill=\"%23f0f0f0\" fill-opacity=\"0.1\"%3E%3Ccircle cx=\"30\" cy=\"30\" r=\"2\"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')",
      },
      screens: {
        'xs': '475px',
      },
      boxShadow: {
        'air-card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'air-card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
    
    // Custom plugins for air quality specific styling
    function({ addUtilities, addComponents, theme }) {
      const newUtilities = {
        '.text-aqi-good': {
          color: theme('colors.aqi-good'),
        },
        '.text-aqi-moderate': {
          color: theme('colors.aqi-moderate'),
        },
        '.text-aqi-unhealthy-sensitive': {
          color: theme('colors.aqi-unhealthy-sensitive'),
        },
        '.text-aqi-unhealthy': {
          color: theme('colors.aqi-unhealthy'),
        },
        '.text-aqi-very-unhealthy': {
          color: theme('colors.aqi-very-unhealthy'),
        },
        '.text-aqi-hazardous': {
          color: theme('colors.aqi-hazardous'),
        },
        '.bg-aqi-good': {
          backgroundColor: theme('colors.aqi-good'),
        },
        '.bg-aqi-moderate': {
          backgroundColor: theme('colors.aqi-moderate'),
        },
        '.bg-aqi-unhealthy-sensitive': {
          backgroundColor: theme('colors.aqi-unhealthy-sensitive'),
        },
        '.bg-aqi-unhealthy': {
          backgroundColor: theme('colors.aqi-unhealthy'),
        },
        '.bg-aqi-very-unhealthy': {
          backgroundColor: theme('colors.aqi-very-unhealthy'),
        },
        '.bg-aqi-hazardous': {
          backgroundColor: theme('colors.aqi-hazardous'),
        },
      }
      
      const newComponents = {
        '.air-card': {
          backgroundColor: theme('colors.white'),
          borderRadius: theme('borderRadius.lg'),
          padding: theme('spacing.6'),
          boxShadow: theme('boxShadow.air-card'),
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: theme('boxShadow.air-card-hover'),
            transform: 'translateY(-2px)',
          },
        },
        '.aqi-badge': {
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: theme('spacing.2') + ' ' + theme('spacing.3'),
          borderRadius: theme('borderRadius.full'),
          fontSize: theme('fontSize.sm'),
          fontWeight: theme('fontWeight.medium'),
          color: theme('colors.white'),
        },
        '.btn-primary': {
          backgroundColor: theme('colors.primary.600'),
          color: theme('colors.white'),
          padding: theme('spacing.2') + ' ' + theme('spacing.4'),
          borderRadius: theme('borderRadius.md'),
          fontSize: theme('fontSize.sm'),
          fontWeight: theme('fontWeight.medium'),
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: theme('colors.primary.700'),
            transform: 'translateY(-1px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        '.btn-secondary': {
          backgroundColor: theme('colors.secondary.600'),
          color: theme('colors.white'),
          padding: theme('spacing.2') + ' ' + theme('spacing.4'),
          borderRadius: theme('borderRadius.md'),
          fontSize: theme('fontSize.sm'),
          fontWeight: theme('fontWeight.medium'),
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: theme('colors.secondary.700'),
            transform: 'translateY(-1px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        '.air-quality-meter': {
          width: '100%',
          height: theme('spacing.6'),
          backgroundColor: theme('colors.gray.200'),
          borderRadius: theme('borderRadius.full'),
          overflow: 'hidden',
          position: 'relative',
        },
        '.air-quality-meter-fill': {
          height: '100%',
          transition: 'width 0.5s ease-in-out',
          borderRadius: theme('borderRadius.full'),
        },
      }

      addUtilities(newUtilities)
      addComponents(newComponents)
    }
  ],
  
  // Safelist important classes that might be generated dynamically
  safelist: [
    'text-aqi-good',
    'text-aqi-moderate',
    'text-aqi-unhealthy-sensitive',
    'text-aqi-unhealthy',
    'text-aqi-very-unhealthy',
    'text-aqi-hazardous',
    'bg-aqi-good',
    'bg-aqi-moderate',
    'bg-aqi-unhealthy-sensitive',
    'bg-aqi-unhealthy',
    'bg-aqi-very-unhealthy',
    'bg-aqi-hazardous',
    'bg-green-100',
    'bg-yellow-100',
    'bg-orange-100',
    'bg-red-100',
    'bg-purple-100',
    'text-green-600',
    'text-yellow-600',
    'text-orange-600',
    'text-red-600',
    'text-purple-600',
    'text-red-900',
  ],
}