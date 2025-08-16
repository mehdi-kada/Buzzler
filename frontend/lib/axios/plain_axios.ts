import axios from "axios";

export const plainAxios = axios.create({
  withCredentials: false,
  // No base URL - we'll use full URLs for external services
  timeout: 300000, 
});

plainAxios.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("External upload error:", error);
    return Promise.reject(error);
  }
);

export default plainAxios;
