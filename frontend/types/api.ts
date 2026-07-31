/**
 * Shared TypeScript types for the LOREWEAVE frontend.
 */

/** Generic paginated API response envelope. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/** Standard API error shape returned by the backend. */
export interface ApiError {
  detail: string;
}
