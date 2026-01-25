import { useId, useState } from "react";
import { Eye, EyeOff } from "lucide-react";

export default function PasswordInput({
  label,
  value,
  onChange,
  placeholder = "••••••••",
  required = true,
  name = "password",
  id,
}) {
  const autoId = useId();
  const inputId = id ?? autoId;

  const [show, setShow] = useState(false);

  return (
    <div>
      {label && (
        <label htmlFor={inputId} className="block font-medium mb-1">
          {label}
        </label>
      )}

      <div className="relative">
        <input
          id={inputId}
          type={show ? "text" : "password"}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          required={required}
          className="w-full border p-2 rounded pr-10"
        />

        <button
          type="button"
          aria-label={show ? "Ocultar senha" : "Mostrar senha"}
          onClick={() => setShow((v) => !v)}
          className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 hover:text-gray-700"
          tabIndex={-1}
        >
          {show ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
    </div>
  );
}
