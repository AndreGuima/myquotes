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

export function confirm({
  message,
  confirmText = "Confirmar",
  cancelText = "Cancelar",
  onConfirm,
  variant = "danger", // danger | primary
}) {
  toast.custom(
    (t) => (
      <div className="bg-gray-900 text-white rounded-xl shadow-lg p-4 w-80">
        <p className="text-sm mb-4">{message}</p>

        <div className="flex justify-end gap-2">
          <button
            onClick={() => toast.dismiss(t.id)}
            className="px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-sm"
          >
            {cancelText}
          </button>

          <button
            onClick={() => {
              toast.dismiss(t.id);
              onConfirm();
            }}
            className={`px-3 py-1 rounded text-sm text-white ${
              variant === "danger"
                ? "bg-red-600 hover:bg-red-700"
                : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    ),
    {
      duration: Infinity,
      position: "top-center",
    },
  );
}
