/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#165DFF',
        secondary: '#6B7280',
        success: '#00B42A',
        warning: '#FF7D00',
        danger: '#F53F3F',
        info: '#86909C',
        light: '#F2F3F5',
        dark: '#1D2129',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      screens: {
        'touch': {'raw': '(hover: none) and (pointer: coarse)'},
      },
    },
  },
  plugins: [],
}