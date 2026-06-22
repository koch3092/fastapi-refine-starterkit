import dataProviderFactory, { axiosInstance } from "@refinedev/simple-rest";
import { API_URL, TOKEN_KEY } from "@/providers/constants";

axiosInstance.defaults.baseURL = API_URL;

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

export const apiClient = axiosInstance;
export const dataProvider = dataProviderFactory(API_URL, axiosInstance);
