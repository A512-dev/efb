import apiClient from "./apiClient";

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

export const createPilotUser = async (userData) => {
  const payload = {
    ...userData,
    password: "SkyDeck@2026!",
  };
  const response = await apiClient.post("/auth/signup", payload);
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await apiClient.get("/users/me");
  return response.data;
};

export const updateProfile = async (profileData) => {
  const response = await apiClient.patch("/users/me/profile", profileData);
  return response.data;
};

export const uploadProfilePicture = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post("/users/me/profile-picture", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const downloadMyProfilePicture = async () => {
  const response = await apiClient.get("/users/me/profile-picture", {
    responseType: "blob",
  });
  return response.data;
};

export const downloadUserProfilePicture = async (userId) => {
  const response = await apiClient.get(`/users/${userId}/profile-picture`, {
    responseType: "blob",
  });
  return response.data;
};

export const fetchManuals = async () => {
  const response = await apiClient.get("/manuals");
  return response.data;
};

export const getManuals = async (params = {}) => {
  const response = await apiClient.get("/manuals", { params });
  return response.data;
};

export const uploadManual = async (file, title, note, categoryId) => {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("file", file);
  formData.append("category_id", Number(categoryId));

  if (note && note.trim() !== "") {
    formData.append("note", note.trim());
  }

  const response = await apiClient.post("/manuals/upload", formData);
  return response.data;
};

export const downloadManual = async (manualId) => {
  const response = await apiClient.get(`/manuals/${manualId}/download`, {
    responseType: "blob",
  });
  return response.data;
};

export const deleteManual = async (manualId, note) => {
  const response = await apiClient.delete(`/manuals/${manualId}`, {
    data: { note },
  });
  return response.data;
};

export const updateManualPdf = async (manualId, file, { title, note } = {}) => {
  const formData = new FormData();
  formData.append("file", file);
  if (title !== undefined && title !== null) formData.append("title", title);
  if (note !== undefined && note !== null) formData.append("note", note);

  const response = await apiClient.post(
    `/manuals/${manualId}/update`,
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    },
  );
  return response.data;
};

export const getManualUpdates = async () => {
  const response = await apiClient.get("/manual-updates", {
    params: { pag: 1, limit: 1000 },
  });
  return response.data;
};

export const getManualCategories = async () => {
  const response = await apiClient.get("/manual-categories/roots");
  return response.data;
};

export const getManualCategoryTree = async () => {
  const response = await apiClient.get("/manual-categories/tree");
  return response.data;
};

export const getCategoryChildren = async (categoryId) => {
  const response = await apiClient.get(
    `/manual-categories/${categoryId}/children`,
  );
  return response.data;
};

export const getCategoryPath = async (categoryId) => {
  const response = await apiClient.get(`/manual-categories/${categoryId}/path`);
  return response.data;
};

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

export const sendMessageWithAttachments = async (payload, files = []) => {
  const formData = new FormData();
  if (payload.subject) formData.append("subject", payload.subject);
  formData.append("body", payload.body);

  if (payload.recipient_ids && Array.isArray(payload.recipient_ids)) {
    payload.recipient_ids.forEach((id) => {
      formData.append("recipient_ids", id.toString());
    });
  }

  files.forEach((file) => {
    formData.append("files", file, file.name);
  });

  const response = await apiClient.post("/messages/with-attachments", formData);
  return response.data;
};

export const markMessageAsRead = async (messageId) => {
  const response = await apiClient.post(`/messages/${messageId}/read`);
  return response.data;
};

export const downloadMessageAttachment = async (messageId, attachmentId) => {
  const response = await apiClient.get(
    `/messages/${messageId}/attachments/${attachmentId}`,
    { responseType: "blob" },
  );
  return response.data;
};

export const fetchForms = async () => {
  const response = await apiClient.get("/forms/active");
  return response.data;
};

export const getActiveForms = async () => {
  const response = await apiClient.get("/forms/active");
  return response.data;
};

export const markManualUpdateRead = async (eventId) => {
  const response = await apiClient.post(`/manual-updates/${eventId}/read`);
  return response.data;
};

export const markAllManualUpdatesRead = async () => {
  const response = await apiClient.post(`/manual-updates/read-all`);
  return response.data;
};
