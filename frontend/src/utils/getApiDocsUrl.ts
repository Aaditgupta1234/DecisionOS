/**
 * Returns the environment-configured API documentation URL or falls back to /docs.
 */
export function getApiDocsUrl(): string {
  return (
    import.meta.env.VITE_API_DOCS_URL ||
    '/docs'
  );
}
