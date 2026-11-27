export interface Config {
  server: { host: string; port: number };
  tags: string[];
}

export class ConfigError extends Error {
  constructor(
    readonly field: string,
    message: string
  ) {
    super(message);
    this.name = "ConfigError";
  }
}

export function parseConfig(text: string): Config {
  let raw: any;
  try {
    raw = JSON.parse(text);
  } catch {
    throw new ConfigError("root", "not valid JSON");
  }

  const host = raw?.server?.host ?? "localhost";
  const port = raw?.server?.port ?? 8080;
  if (typeof host !== "string" || host === "") throw new ConfigError("server.host", "host must be text");

  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new ConfigError("server.port", "port out of range");
  }

  const tags: unknown = raw?.tags ?? [];
  if (!Array.isArray(tags)) throw new ConfigError("tags", "tags must be a list");

  return { server: { host, port }, tags: [...new Set(tags.map((tag) => String(tag).trim()))] };
}
