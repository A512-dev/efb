// // import apiClient from "./apiClient";

// // //access token
// // export const login = async (email, password) => {
// //   const res = await apiClient.post("/auth/login", {
// //     email,
// //     password,
// //   });

// //   localStorage.setItem("access_token", res.data.access_token);
// //   localStorage.setItem("refresh_token", res.data.refresh_token);
// //   localStorage.setItem("user", JSON.stringify(res.data.user));

// //   return res.data;
// // };

// // // refresh token
// // export const refreshToken = async () => {
// //   const refreshToken = localStorage.getItem("refresh_token");
// //   if (!refreshToken) return null;

// //   const params = new URLSearchParams();
// //   params.append("refresh_token", refreshToken);

// //   const res = await apiClient.post("/auth/refresh", params, {
// //     headers: {
// //       "Content-Type": "application/x-www-form-urlencoded",
// //     },
// //   });

// //   const newAccess = res.data.access_token;
// //   localStorage.setItem("access_token", newAccess);

// //   return newAccess;
// // };

// import apiClient from "./apiClient";

// // export const signupUser = async () => {
// //   const response = await apiClient.post("/auth/signup", payload);
// //   return response.data;
// // };

// export const createPilotUser = async () => {
//   const randomId = Math.floor(1000 + Math.random() * 9000);
//   const email = `pilot${randomId}@skywest-air.com`;
//   const payload = {
//     name: `Pilot ${randomId}`,
//     email: email,
//     password: "SkyDeck@2026!",
//     role: "pilot",
//   };

//   const response = await apiClient.post("/auth/signup", payload);
//   return {
//     ...response.data,
//     email: email,
//   };
// };

// export const loginUser = async (email, password) => {
//   const response = await apiClient.post("/auth/login", {
//     email,
//     password,
//     device_info: { platform: "Web" },
//   });

//   return response.data;
// };

// export const logoutUser = async (refreshToken) => {
//   return apiClient.post("/auth/logout", {
//     refresh_token: refreshToken,
//   });
// };

// export const fetchManuals = async () => {
//   const response = await apiClient.get("/manuals");
//   return response.data;
// };

// export const fetchForms = async () => {
//   const response = await apiClient.get("/forms/active");
//   return response.data;
// };

// export const getCurrentUser = async () => {
//   const response = await apiClient.get("/users/me");
//   return response.data;
// };

// export const uploadManual = async (file, title) => {
//   const formData = new FormData();

//   formData.append("title", title);
//   formData.append("file", file);

//   const response = await apiClient.post("/manuals/upload", formData);

//   return response.data;
// };

// export const getManuals = async () => {
//   const response = await apiClient.get("/manuals");
//   return response.data;
// };
// export const downloadManual = async (manualId) => {
//   const response = await apiClient.get(`/manuals/${manualId}/download`, {
//     responseType: "blob",
//   });

//   return response.data;
// };
// export const deleteManual = async (manualId) => {
//   const response = await apiClient.delete(`/manuals/${manualId}`);
//   return response.data;
// };
// export const getActiveForms = async () => {
//   const response = await apiClient.get("/forms/active");
//   return response.data;
// };

// export const listMessages = async ({
//   box = "inbox",
//   page = 1,
//   limit = 20,
// } = {}) => {
//   const response = await apiClient.get("/messages", {
//     params: { box, page, limit },
//   });
//   return response.data;
// };

// export const sendMessage = async (payload) => {
//   const response = await apiClient.post("/messages", payload);
//   return response.data;
// };

// export const markMessageAsRead = async (messageId) => {
//   const response = await apiClient.post(`/messages/${messageId}/read`);
//   return response.data;
// };

import apiClient from "./apiClient";

// Auth
export const loginUser = async (email, password) => {
  const response = await apiClient.post("/auth/login", {
    email,
    password,
    device_info: { platform: "Web" },
  });

  return response.data;
};

export const logoutUser = async (refreshToken) => {
  return apiClient.post("/auth/logout", {
    refresh_token: refreshToken,
  });
};

export const createPilotUser = async () => {
  const randomId = Math.floor(1000 + Math.random() * 9000);
  const email = `pilot${randomId}@skywest-air.com`;
  const payload = {
    name: `Pilot ${randomId}`,
    email: email,
    password: "SkyDeck@2026!",
    role: "pilot",
  };

  const response = await apiClient.post("/auth/signup", payload);
  return {
    ...response.data,
    email: email,
  };
};

// Users
export const getCurrentUser = async () => {
  const response = await apiClient.get("/users/me");
  return response.data;
};

// Manuals
export const fetchManuals = async () => {
  const response = await apiClient.get("/manuals");
  return response.data;
};

export const getManuals = async () => {
  const response = await apiClient.get("/manuals");
  return response.data;
};

export const uploadManual = async (file, title) => {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("file", file);

  const response = await apiClient.post("/manuals/upload", formData);
  return response.data;
};

export const downloadManual = async (manualId) => {
  const response = await apiClient.get(`/manuals/${manualId}/download`, {
    responseType: "blob",
  });

  return response.data;
};

export const deleteManual = async (manualId) => {
  const response = await apiClient.delete(`/manuals/${manualId}`);
  return response.data;
};

// Forms
export const fetchForms = async () => {
  const response = await apiClient.get("/forms/active");
  return response.data;
};

export const getActiveForms = async () => {
  const response = await apiClient.get("/forms/active");
  return response.data;
};

// Messages
export const listMessages = async ({
  box = "inbox",
  page = 1,
  limit = 20,
} = {}) => {
  const response = await apiClient.get("/messages", {
    params: { box, page, limit },
  });
  return response.data;
};

export const sendMessage = async (payload) => {
  const response = await apiClient.post("/messages", payload);
  return response.data;
};

export const markMessageAsRead = async (messageId) => {
  const response = await apiClient.post(`/messages/${messageId}/read`);
  return response.data;
};
<<<<<<< HEAD
//updates

export const updateManualPdf = async (manualId, file, { title, note } = {}) => {
  const formData = new FormData();
  formData.append("file", file);

  if (title !== undefined && title !== null) formData.append("title", title);
  if (note !== undefined && note !== null) formData.append("note", note);

  const response = await apiClient.post(
    `/manuals/${manualId}/update`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );

  return response.data;
};

export const getManualUpdates = async () => {
  const response = await apiClient.get("/manual-updates", {
    params: { pag: 1, limit: 1000 },
  });
  return response.data;
};
=======
>>>>>>> origin/main
