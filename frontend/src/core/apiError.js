// frontend/src/core/apiError.js

/**
 * Traduz erros HTTP / Axios em mensagens amigáveis para o usuário
 */
export function getApiErrorMessage(error, fallback = "Erro inesperado") {
  // Erro sem response (offline, timeout, DNS, etc)
  if (!error?.response) {
    return "Não foi possível conectar ao servidor. Verifique sua internet.";
  }

  const { status, data } = error.response;

  // Mensagem vinda direto da API (prioridade máxima)
  if (typeof data?.message === "string" && data.message.trim() !== "") {
    return data.message;
  }

  if (typeof data?.detail === "string" && data.detail.trim() !== "") {
    return data.detail;
  }

  // Fallback por status HTTP
  switch (status) {
    case 400:
      return "Requisição inválida. Verifique os dados enviados.";

    case 401:
      return "Sua sessão expirou. Faça login novamente.";

    case 403:
      return "Você não tem permissão para executar esta ação.";

    case 404:
      return "Recurso não encontrado.";

    case 409:
      return "Conflito de dados. Esse registro já existe.";

    case 422:
      return "Dados inválidos. Verifique os campos preenchidos.";

    case 429:
      return "Muitas tentativas. Aguarde alguns instantes.";

    case 500:
      return "Erro interno no servidor. Tente novamente mais tarde.";

    case 502:
    case 503:
    case 504:
      return "Servidor temporariamente indisponível.";

    default:
      return fallback;
  }
}
