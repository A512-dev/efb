import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api/v1",
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers["Authorization"] = "Bearer " + token;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refresh_token = localStorage.getItem("refresh_token");

      if (!refresh_token) {
        isRefreshing = false;
        return Promise.reject(error);
      }

      try {
        const response = await axios.post("/api/v1/auth/refresh", {
          refresh_token,
        });

        const newAccess = response.data.access_token;
        localStorage.setItem("access_token", newAccess);

        apiClient.defaults.headers.common["Authorization"] =
          "Bearer " + newAccess;
        processQueue(null, newAccess);
        return apiClient(originalRequest);
      } catch (err) {
        processQueue(err, null);
        localStorage.clear();
        window.location = "/";
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  },
);

export default apiClient;
