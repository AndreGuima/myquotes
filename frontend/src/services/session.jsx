export function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}
