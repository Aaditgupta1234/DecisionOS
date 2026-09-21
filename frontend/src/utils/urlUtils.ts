/**
 * Utility functions for resolving dynamic backend endpoints, documentation URLs, and asset links.
 */

export function getApiDocsUrl(): string {
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_DOCS_URL) {
    return import.meta.env.VITE_API_DOCS_URL;
  }
  return '/docs';
}

export function getApiBaseUrl(): string {
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  return '/api/v1';
}
