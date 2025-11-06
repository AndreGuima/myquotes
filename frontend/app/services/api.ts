import axios from "axios";
import { API_URL } from "@env";

console.log("🔗 API URL:", API_URL);

const api = axios.create({
  baseURL: API_URL, // ✅ agora vem do .env
  timeout: 5000,
});

export default api;
