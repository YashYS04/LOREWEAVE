/**
 * Health service — wraps the backend /health endpoint.
 */
import { apiClient } from "@/lib/api-client";

export interface HealthResponse {
  status: string;
}

export const healthService = {
  check: (): Promise<HealthResponse> => apiClient.get<HealthResponse>("/api/v1/health"),
};
