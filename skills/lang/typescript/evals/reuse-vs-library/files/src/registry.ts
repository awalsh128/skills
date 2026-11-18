const REGISTRY = "https://registry.plugkit.example.com";

export interface Release {
  /** Git tag, e.g. "v1.4.0" or "v2.0.0-beta.3". */
  tag: string;
  /** ISO-8601 timestamp in UTC. */
  publishedAt: string;
}

export async function fetchLatestRelease(): Promise<Release> {
  const res = await fetch(`${REGISTRY}/releases/latest`);
  if (!res.ok) throw new Error(`registry: ${res.status}`);

  return (await res.json()) as Release;
}

/** Returns the latest version per plugin. The API accepts at most 20 names per call. */
export async function fetchPluginVersions(names: string[]): Promise<Record<string, string>> {
  const url = new URL("/plugins/versions", REGISTRY);
  url.searchParams.set("names", names.join(","));
  const res = await fetch(url);
  if (!res.ok) throw new Error(`registry: ${res.status}`);

  return (await res.json()) as Record<string, string>;
}
