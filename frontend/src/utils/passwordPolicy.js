// src/utils/passwordPolicy.js
export function validatePassword(password) {
  return {
    minLength: password.length >= 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    digit: /\d/.test(password),
    special: /[^\w\s]/.test(password),
  };
}

export function isPasswordValid(result) {
  return Object.values(result).every(Boolean);
}
