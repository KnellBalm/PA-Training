import axios from "axios";

export const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  console.error("❌ NEXT_PUBLIC_API_URL is not defined");
}

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("API Error:", err?.response?.data || err.message);
    return Promise.reject(err);
  }
);

export default api;
