const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

// Token storage helper
export const getStoredToken = () => {
  return localStorage.getItem("solvesphere_token");
};

export const setStoredToken = (token) => {
  if (token) {
    localStorage.setItem("solvesphere_token", token);
  } else {
    localStorage.removeItem("solvesphere_token");
  }
};

export const getStoredUser = () => {
  try {
    const raw = localStorage.getItem("solvesphere_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const setStoredUser = (user) => {
  if (user) {
    localStorage.setItem("solvesphere_user", JSON.stringify(user));
  } else {
    localStorage.removeItem("solvesphere_user");
  }
};

// Generic fetch wrapper with auth header injection and error handling
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    Accept: "application/json",
    ...options.headers,
  };

  const token = getStoredToken();
  if (token && !headers["Authorization"] && !options.skipAuth) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Handle JSON body
  if (options.body && typeof options.body === "object" && !(options.body instanceof URLSearchParams) && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 204) {
      return null;
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      let errorMsg = data?.detail || `Request failed with status ${response.status}`;
      if (Array.isArray(errorMsg)) {
        errorMsg = errorMsg.map(e => e.msg || JSON.stringify(e)).join(", ");
      } else if (typeof errorMsg === "object") {
        errorMsg = JSON.stringify(errorMsg);
      }
      throw new Error(errorMsg);
    }

    return data;
  } catch (err) {
    // If backend is unreachable or network fetch fails
    if (err.name === "TypeError" && (err.message.includes("fetch") || err.message.includes("NetworkError") || err.message.includes("Failed"))) {
      throw new Error("Unable to connect to SolveSphere backend (127.0.0.1:8001). Please ensure the backend is running.");
    }
    throw err;
  }
}

export const api = {
  // Auth
  auth: {
    login: async (email, password) => {
      // Clear any previous stale session
      setStoredToken(null);
      setStoredUser(null);

      // Backend uses OAuth2PasswordRequestForm (form-urlencoded username & password)
      const formBody = new URLSearchParams();
      formBody.append("username", email.trim().toLowerCase());
      formBody.append("password", password);

      const res = await request("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formBody,
        skipAuth: true,
      });

      if (res.access_token) {
        setStoredToken(res.access_token);
        // Fetch user profile immediately
        const userProfile = await api.auth.getMe();
        setStoredUser(userProfile);
        return { token: res.access_token, user: userProfile };
      }
      return res;
    },

    register: async (payload) => {
      const res = await request("/api/auth/register", {
        method: "POST",
        body: payload,
        skipAuth: true,
      });
      return res;
    },

    getMe: async () => {
      return await request("/api/auth/me");
    },
  },

  // Challenges
  challenges: {
    list: async ({ page = 1, pageSize = 12, status = "", category = "", district = "" } = {}) => {
      const params = new URLSearchParams();
      params.append("page", page);
      params.append("page_size", pageSize);
      if (status) params.append("status", status);
      if (category) params.append("category", category);
      if (district) params.append("district", district);

      return await request(`/api/challenges?${params.toString()}`);
    },

    getById: async (id) => {
      return await request(`/api/challenges/${id}`);
    },

    create: async (challengeData) => {
      return await request("/api/challenges", {
        method: "POST",
        body: challengeData,
      });
    },

    update: async (id, updateData) => {
      return await request(`/api/challenges/${id}`, {
        method: "PATCH",
        body: updateData,
      });
    },

    // AI Analysis
    analyze: async (id) => {
      return await request(`/api/challenges/${id}/analyze`, {
        method: "POST",
      });
    },

    getAnalysis: async (id) => {
      return await request(`/api/challenges/${id}/ai-analysis`);
    },

    // Institution Matching
    match: async (id) => {
      return await request(`/api/challenges/${id}/match`, {
        method: "POST",
      });
    },

    getMatches: async (id) => {
      return await request(`/api/challenges/${id}/matches`);
    },
  },

  // Institutions
  institutions: {
    list: async ({ district = "", institutionType = "", page = 1, pageSize = 20 } = {}) => {
      const params = new URLSearchParams();
      params.append("page", page);
      params.append("page_size", pageSize);
      if (district) params.append("district", district);
      if (institutionType) params.append("institution_type", institutionType);

      return await request(`/api/institutions?${params.toString()}`);
    },

    getById: async (id) => {
      return await request(`/api/institutions/${id}`);
    },

    getExpertise: async (id) => {
      return await request(`/api/institutions/${id}/expertise`);
    },

    create: async (data) => {
      return await request("/api/institutions", {
        method: "POST",
        body: data,
      });
    },

    addExpertise: async (institutionId, data) => {
      return await request(`/api/institutions/${institutionId}/expertise`, {
        method: "POST",
        body: data,
      });
    },
  },

  // Dynamic Translation
  translate: {
    batch: async (texts, targetLanguage, sourceLanguage = "en") => {
      if (!texts || texts.length === 0 || targetLanguage === "en" || targetLanguage === sourceLanguage) {
        return { translations: texts, target_language: targetLanguage };
      }
      return await request("/api/translate", {
        method: "POST",
        body: {
          texts,
          target_language: targetLanguage,
          source_language: sourceLanguage,
        },
      });
    },
  },
};
