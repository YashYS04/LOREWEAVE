/**
 * TanStack Query client configuration.
 */
import { QueryClient } from "@tanstack/react-query";

export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Keep data fresh for 60 seconds before refetching.
        staleTime: 60 * 1000,
        // Do not retry on 4xx errors — only on network failures.
        retry: (failureCount, error) => {
          if (error instanceof Error && error.message.match(/API error 4\d\d/)) {
            return false;
          }
          return failureCount < 2;
        },
      },
    },
  });
}
