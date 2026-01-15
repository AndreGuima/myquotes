const ENV = import.meta.env.MODE;

const LEVELS = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
};

const CURRENT_LEVEL = ENV === "production" ? LEVELS.warn : LEVELS.debug;

function shouldLog(level) {
  return LEVELS[level] >= CURRENT_LEVEL;
}

function format(level, message) {
  const ts = new Date().toISOString();
  return `[${ts}] [${level.toUpperCase()}] ${message}`;
}

export const logger = {
  debug(message, meta) {
    if (!shouldLog("debug")) return;
    console.debug(format("debug", message), meta ?? "");
  },

  info(message, meta) {
    if (!shouldLog("info")) return;
    console.info(format("info", message), meta ?? "");
  },

  warn(message, meta) {
    if (!shouldLog("warn")) return;
    console.warn(format("warn", message), meta ?? "");
  },

  error(message, meta) {
    if (!shouldLog("error")) return;
    console.error(format("error", message), meta ?? "");
  },
};
