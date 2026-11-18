import { useEffect, useState } from "react";

export interface SearchBoxProps {
  /** Called with the trimmed query 300 ms after the user stops typing. */
  onSearch: (query: string) => Promise<string[]>;
  minLength?: number;
}

export function SearchBox({ onSearch, minLength = 2 }: SearchBoxProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<string[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < minLength) {
      setResults(null);
      return;
    }
    const timer = setTimeout(() => {
      onSearch(trimmed)
        .then((r) => { setResults(r); setError(false); })
        .catch(() => setError(true));
    }, 300);
    return () => clearTimeout(timer);
  }, [query, minLength, onSearch]);

  return (
    <div className="search">
      <label htmlFor="q">Search products</label>
      <input id="q" type="search" value={query} onChange={(e) => setQuery(e.target.value)} />
      <button type="button" onClick={() => setQuery("")} disabled={query === ""}>
        Clear
      </button>
      {error && <p role="alert">Search failed, try again.</p>}
      {results && results.length === 0 && <p>No results</p>}
      {results && results.length > 0 && (
        <ul aria-label="Results">
          {results.map((r) => <li key={r}>{r}</li>)}
        </ul>
      )}
    </div>
  );
}
