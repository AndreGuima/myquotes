import toast from "react-hot-toast";

const baseStyle = {
  borderRadius: "12px",
  background: "#111827", // gray-900
  color: "#F9FAFB", // gray-50
  padding: "12px 16px",
  fontSize: "14px",
};

export const notify = {
  success(message, options = {}) {
    return toast.success(message, {
      duration: 3000,
      style: baseStyle,
      iconTheme: {
        primary: "#22C55E", // green-500
        secondary: "#ECFDF5",
      },
      ...options,
    });
  },

  error(message, options = {}) {
    return toast.error(message, {
      duration: 4000,
      style: baseStyle,
      iconTheme: {
        primary: "#EF4444", // red-500
        secondary: "#FEF2F2",
      },
      ...options,
    });
  },

  info(message, options = {}) {
    return toast(message, {
      duration: 3000,
      icon: "ℹ️",
      style: baseStyle,
      ...options,
    });
  },

  loading(message, options = {}) {
    return toast.loading(message, {
      style: baseStyle,
      ...options,
    });
  },

  dismiss(id) {
    toast.dismiss(id);
  },
};
