/**
 * Timeline API service.
 */
import { apiClient } from "@/lib/api-client";
import type {
  CreateTimelineEventRequest,
  TimelineEvent,
  TimelineEventList,
  UpdateTimelineEventRequest,
} from "@/types/timeline";

const BASE = "/api/v1/timeline/events";

interface Envelope<T> {
  success: boolean;
  message: string;
  data: T;
}

const unwrap = <T>(e: Envelope<T>): T => e.data;

export interface ListTimelineEventsParams {
  universe_id: string;
  skip?: number;
  limit?: number;
  event_type?: string;
  status?: string;
  search?: string;
}

export const timelineService = {
  create: (payload: CreateTimelineEventRequest): Promise<TimelineEvent> =>
    apiClient.post<Envelope<TimelineEvent>>(BASE, payload).then(unwrap),

  list: (params: ListTimelineEventsParams): Promise<TimelineEventList> => {
    const qs = new URLSearchParams();
    qs.set("universe_id", params.universe_id);
    if (params.skip !== undefined) qs.set("skip", String(params.skip));
    if (params.limit !== undefined) qs.set("limit", String(params.limit));
    if (params.event_type) qs.set("event_type", params.event_type);
    if (params.status) qs.set("status", params.status);
    if (params.search) qs.set("search", params.search);
    return apiClient.get<Envelope<TimelineEventList>>(`${BASE}?${qs.toString()}`).then(unwrap);
  },

  getById: (id: string): Promise<TimelineEvent> =>
    apiClient.get<Envelope<TimelineEvent>>(`${BASE}/${id}`).then(unwrap),

  update: (id: string, payload: UpdateTimelineEventRequest): Promise<TimelineEvent> =>
    apiClient.patch<Envelope<TimelineEvent>>(`${BASE}/${id}`, payload).then(unwrap),

  delete: (id: string): Promise<void> =>
    apiClient.delete<Envelope<null>>(`${BASE}/${id}`).then(() => undefined),
};
