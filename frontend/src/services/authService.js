import api from "./api";

const authService = {
  async login({ email, password }) {
    const res = await api.post("/auth/login", { email, password });
    return res.data;
  },

  async register(payload) {
    const res = await api.post("/auth/register", payload);
    return res.data;
  },

  async forgotPassword(email) {
    const res = await api.post("/auth/forgot-password", { email });
    return res.data;
  },

  async validateResetToken(token) {
    const res = await api.get("/auth/reset-password/validate", {
      params: { token },
    });
    return res.data;
  },

  async resetPassword({ token, new_password }) {
    const res = await api.post("/auth/reset-password", {
      token,
      new_password,
    });
    return res.data;
  },

  async verifyEmail(token) {
    const res = await api.get("/auth/verify-email", {
      params: { token },
    });
    return res.data;
  },
};

export default authService;
