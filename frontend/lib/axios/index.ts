import axios from "axios";
import { useAuthStore } from "../store/authStore";

const api = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true,
});

const getCsrfTokenFromCookie = (): string | null => {
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? match[1] : null;
};

// Request Interceptor used to automatically add both the access token and csrf token
api.interceptors.request.use(
  async (config) => {
    const { accessToken } = useAuthStore.getState();
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    if (
      config.method &&
      !["get", "head", "options"].includes(config.method.toLowerCase())
    ) {
      let csrfToken = getCsrfTokenFromCookie();

      if (!csrfToken) {
        try {
          const response = await axios.post(
            "http://localhost:8000/auth/csrf-token"
          );
          csrfToken = response.data.csrf_token;
        } catch (error) {
          console.error("Failed to fetch CSRF token", error);
          return Promise.reject(error);
        }
      }

      if (csrfToken) {
        config.headers["X-CSRF-Token"] = csrfToken;
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refreshing
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle CSRF errors
    if (
      error.response?.status === 403 &&
      error.response?.data?.detail?.includes("CSRF")
    ) {
      // Clear invalid CSRF token and retry
      document.cookie =
        "csrf_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      if (!originalRequest._csrf_retry) {
        originalRequest._csrf_retry = true;
        return api(originalRequest);
      }
    }

    // Handle token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const { data } = await api.post("/auth/refresh");
        useAuthStore.getState().setAccessToken(data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        // Only redirect if not already on login page
        if (!window.location.pathname.includes("/auth/login")) {
          window.location.href = "/auth/login";
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
