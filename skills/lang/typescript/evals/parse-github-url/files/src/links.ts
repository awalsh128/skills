/** Builds the web URL for a file on a branch of a GitHub repository. */
export function fileUrl(owner: string, repo: string, branch: string, path: string): string {
  return `https://github.com/${owner}/${repo}/blob/${branch}/${path}`;
}
