/**
 * Core API HTTP Client for DecisionOS Frontend
 */

const BASE_URL = '/api/v1';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('decisionos_token');

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // If body is FormData (file upload), remove Content-Type to let browser set boundary
  if (options.body instanceof FormData) {
    delete headers['Content-Type'];
  }

  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  let responseData: any = null;
  try {
    const text = await response.text();
    responseData = text ? JSON.parse(text) : null;
  } catch (e) {
    // Non-JSON response
  }

  if (!response.ok) {
    let errorMsg = 'Intelligence Service Temporarily Unavailable';
    if (typeof responseData?.detail === 'string') {
      errorMsg = responseData.detail;
    } else if (responseData?.detail && typeof responseData.detail === 'object') {
      if (Array.isArray(responseData.detail)) {
        const msgs = responseData.detail.map((d: any) => (typeof d === 'string' ? d : d?.msg || d?.message || JSON.stringify(d))).filter(Boolean);
        if (msgs.length > 0) errorMsg = msgs.join('; ');
      } else {
        errorMsg = responseData.detail.message || responseData.detail.msg || responseData.detail.error || 'Dataset validation failed.';
      }
    } else if (typeof responseData?.message === 'string') {
      errorMsg = responseData.message;
    } else if (typeof responseData?.error === 'string') {
      errorMsg = responseData.error;
    } else if (response.status) {
      errorMsg = `Intelligence Service Temporarily Unavailable (Status ${response.status})`;
    }
    throw new ApiError(response.status, errorMsg, responseData);
  }

  // Unwrap standardized backend SuccessResponse envelope if present
  if (responseData && typeof responseData === 'object' && 'data' in responseData) {
    return responseData.data as T;
  }

  return responseData as T;
}
