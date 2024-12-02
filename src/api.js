//write an interceptor: intercept requests and auto-add correct header
import axios from "axios";
import { ACCESS_TOKEN } from "./constants";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error response status is 401
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Prevent infinite loop

      const refreshToken = localStorage.getItem(REFRESH_TOKEN);

      if (refreshToken) {
        try {
          const response = await axios.post(
            `${import.meta.env.VITE_API_URL}/api/token/refresh/`,
            { refresh: refreshToken }
          );

          // Save new tokens
          localStorage.setItem(ACCESS_TOKEN, response.data.access);
          localStorage.setItem(REFRESH_TOKEN, response.data.refresh);

          // Update the authorization header
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

          // Retry the original request with the new token
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh token expired or invalid
          redirectToLogin();
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available
        redirectToLogin();
      }
    }

    return Promise.reject(error);
  }
);

function redirectToLogin() {
  localStorage.removeItem(ACCESS_TOKEN);
  localStorage.removeItem(REFRESH_TOKEN);
  window.location.href = "/login";
}


export default api;