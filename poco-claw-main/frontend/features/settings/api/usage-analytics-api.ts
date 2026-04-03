"use client";

import { apiClient, API_ENDPOINTS } from "@/services/api-client";
import type { UsageAnalyticsResponse } from "@/features/settings/types";

export interface UsageAnalyticsQuery {
  month?: string;
  day?: string;
  timezone?: string;
}

function buildQuery(params: UsageAnalyticsQuery): string {
  const searchParams = new URLSearchParams();
  if (params.month) searchParams.set("month", params.month);
  if (params.day) searchParams.set("day", params.day);
  if (params.timezone) searchParams.set("timezone", params.timezone);
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

export async function getUsageAnalytics(
  params: UsageAnalyticsQuery,
): Promise<UsageAnalyticsResponse> {
  return apiClient.get<UsageAnalyticsResponse>(
    `${API_ENDPOINTS.usageAnalytics}${buildQuery(params)}`,
  );
}
