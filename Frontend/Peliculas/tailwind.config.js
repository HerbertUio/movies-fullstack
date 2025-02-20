/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#121212', // Color de fondo principal
        'dark-card': '#1E1E1E', // Color de las tarjetas
        // Puedes agregar más colores personalizados si lo deseas
      },
    },
  },
  plugins: [],
};
