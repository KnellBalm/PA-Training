/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 기본 배경/텍스트
        draculaBg: "#1e1e2e",
        draculaSoft: "#303446",
        draculaCard: "#2a2e3f",
        draculaBorder: "#45475a",
        draculaText: "#cdd6f4",

        // 포인트 컬러
        draculaAccent: "#b4befe",
        draculaAccent2: "#cba6f7",
        draculaPink: "#f5c2e7",
        draculaPurple: "#cba6f7",
        draculaCyan: "#89dceb",

        // 보조 텍스트/배경
        draculaComment: "#9399b2",
        draculaSelection: "#313244",
        draculaCurrent: "#25273a",
      },
    },
  },
  plugins: [],
};
