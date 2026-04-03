import { apiClient, API_ENDPOINTS } from "@/services/api-client";
import type {
  SlashCommand,
  SlashCommandCreateInput,
  SlashCommandSuggestion,
  SlashCommandUpdateInput,
} from "@/features/capabilities/slash-commands/types";
import {
  markSlashCommandSuggestionsInvalidated,
  SLASH_COMMAND_SUGGESTIONS_INVALIDATED_EVENT,
} from "@/features/capabilities/slash-commands/api/suggestions-state";

export { SLASH_COMMAND_SUGGESTIONS_INVALIDATED_EVENT };

export const slashCommandsService = {
  list: async (options?: { revalidate?: number }): Promise<SlashCommand[]> => {
    return apiClient.get<SlashCommand[]>(API_ENDPOINTS.slashCommands, {
      next: { revalidate: options?.revalidate },
    });
  },

  listSuggestions: async (options?: {
    revalidate?: number;
    cacheBust?: string | number;
  }): Promise<SlashCommandSuggestion[]> => {
    const endpoint =
      options?.cacheBust !== undefined && options?.cacheBust !== null
        ? `${API_ENDPOINTS.slashCommandSuggestions}?_t=${encodeURIComponent(String(options.cacheBust))}`
        : API_ENDPOINTS.slashCommandSuggestions;
    return apiClient.get<SlashCommandSuggestion[]>(endpoint, {
      cache: "no-store",
      next: { revalidate: options?.revalidate },
    });
  },

  get: async (
    commandId: number,
    options?: { revalidate?: number },
  ): Promise<SlashCommand> => {
    return apiClient.get<SlashCommand>(API_ENDPOINTS.slashCommand(commandId), {
      next: { revalidate: options?.revalidate },
    });
  },

  create: async (input: SlashCommandCreateInput): Promise<SlashCommand> => {
    const created = await apiClient.post<SlashCommand>(
      API_ENDPOINTS.slashCommands,
      input,
    );
    markSlashCommandSuggestionsInvalidated();
    return created;
  },

  update: async (
    commandId: number,
    input: SlashCommandUpdateInput,
  ): Promise<SlashCommand> => {
    const updated = await apiClient.patch<SlashCommand>(
      API_ENDPOINTS.slashCommand(commandId),
      input,
    );
    markSlashCommandSuggestionsInvalidated();
    return updated;
  },

  remove: async (commandId: number): Promise<Record<string, unknown>> => {
    const removed = await apiClient.delete<Record<string, unknown>>(
      API_ENDPOINTS.slashCommand(commandId),
    );
    markSlashCommandSuggestionsInvalidated();
    return removed;
  },
};
