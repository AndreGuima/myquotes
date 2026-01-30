import api from "./api";

const authService = {
  async login({ email, password }) {
    return api.post("/auth/login", { email, password });
  },

  async register(payload) {
    return api.post("/auth/register", payload);
  },

  async forgotPassword(email) {
    return api.post("/auth/forgot-password", { email });
  },

  async validateResetToken(token) {
    return api.get("/auth/reset-password/validate", {
      params: { token },
    });
  },

  async resetPassword({ token, new_password }) {
    return api.post("/auth/reset-password", {
      token,
      new_password,
    });
  },

  async verifyEmail(token) {
    return api.get("/auth/verify-email", {
      params: { token },
    });
  },
};

export default authService;
