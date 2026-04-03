"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { useT } from "@/lib/i18n/client";
import { memoriesApi } from "@/features/memories/api/memories-api";
import type {
  MemoryCreateInput,
  MemoryListItem,
  MemorySearchInput,
  MemoryUpdateInput,
} from "@/features/memories/types";

const MEMORY_CREATE_POLL_INTERVAL_MS = 1000;
const MEMORY_CREATE_POLL_MAX_ATTEMPTS = 60;

interface MemoryCreateJobState {
  jobId: string | null;
  status: string | null;
  progress: number;
  error: string | null;
}

const DEFAULT_CREATE_JOB_STATE: MemoryCreateJobState = {
  jobId: null,
  status: null,
  progress: 0,
  error: null,
};

function toRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  return value as Record<string, unknown>;
}

function asString(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function extractItems(payload: unknown): unknown[] {
  if (Array.isArray(payload)) return payload;
  const obj = toRecord(payload);
  if (!obj) return [];

  const candidates = [
    obj.items,
    obj.memories,
    obj.results,
    obj.data,
    obj.entries,
  ];

  for (const candidate of candidates) {
    if (Array.isArray(candidate)) return candidate;
  }

  return [];
}

function normalizeMemoryItems(payload: unknown): MemoryListItem[] {
  const items = extractItems(payload);
  return items
    .map((item, index) => {
      const raw = toRecord(item);
      if (!raw) return null;

      const id =
        asString(raw.id) ??
        asString(raw.memory_id) ??
        asString(raw.memoryId) ??
        `row-${index}`;
      const text =
        asString(raw.memory) ??
        asString(raw.text) ??
        asString(raw.content) ??
        asString(raw.value) ??
        JSON.stringify(raw, null, 2);
      const createdAt =
        asString(raw.created_at) ??
        asString(raw.createdAt) ??
        asString(raw.timestamp);
      const updatedAt = asString(raw.updated_at) ?? asString(raw.updatedAt);

      return {
        id,
        text,
        createdAt,
        updatedAt,
        raw,
      };
    })
    .filter((item): item is MemoryListItem => item !== null);
}

function sleep(milliseconds: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}

export function useMemoriesStore() {
  const { t } = useT("translation");
  const [items, setItems] = useState<MemoryListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);
  const [lastPayload, setLastPayload] = useState<unknown>(null);
  const [mode, setMode] = useState<"list" | "search">("list");
  const [createJob, setCreateJob] = useState<MemoryCreateJobState>(
    DEFAULT_CREATE_JOB_STATE,
  );
  const createJobPollingIdRef = useRef<string | null>(null);

  const resetCreateJob = useCallback(() => {
    createJobPollingIdRef.current = null;
    setCreateJob(DEFAULT_CREATE_JOB_STATE);
  }, []);

  const refresh = useCallback(
    async ({ silent = false }: { silent?: boolean } = {}) => {
      if (!silent) setIsLoading(true);
      try {
        const payload = await memoriesApi.list();
        setItems(normalizeMemoryItems(payload));
        setLastPayload(payload);
        setMode("list");
      } catch (error) {
        console.error("[Memories] list failed", error);
        toast.error(t("memories.toasts.error", "Operation failed"));
      } finally {
        setIsLoading(false);
      }
    },
    [t],
  );

  useEffect(() => {
    refresh();
  }, [refresh]);

  const search = useCallback(
    async (input: MemorySearchInput) => {
      setIsMutating(true);
      try {
        const payload = await memoriesApi.search(input);
        setItems(normalizeMemoryItems(payload));
        setLastPayload(payload);
        setMode("search");
      } catch (error) {
        console.error("[Memories] search failed", error);
        toast.error(t("memories.toasts.error", "Operation failed"));
      } finally {
        setIsMutating(false);
      }
    },
    [t],
  );

  const waitForCreateJob = useCallback(
    async (jobId: string) => {
      if (createJobPollingIdRef.current === jobId) return true;
      createJobPollingIdRef.current = jobId;

      setCreateJob((prev) => ({
        ...prev,
        jobId,
      }));

      try {
        for (
          let attempt = 0;
          attempt < MEMORY_CREATE_POLL_MAX_ATTEMPTS;
          attempt += 1
        ) {
          if (createJobPollingIdRef.current !== jobId) return false;

          const payload = await memoriesApi.getCreateJob(jobId);
          setLastPayload(payload);

          const raw = toRecord(payload);
          const status = asString(raw?.status)?.toLowerCase();
          const progress =
            typeof raw?.progress === "number"
              ? Math.max(0, Math.min(100, raw.progress))
              : null;
          const errorMessage = asString(raw?.error);

          setCreateJob({
            jobId,
            status: status ?? "running",
            progress:
              progress ??
              (status === "success" ? 100 : status === "queued" ? 0 : 0),
            error: errorMessage,
          });

          if (status === "success") {
            toast.success(t("memories.toasts.created", "Memory created"));
            await refresh({ silent: true });
            return true;
          }
          if (status === "failed") {
            console.error("[Memories] create job failed", raw);
            toast.error(
              errorMessage || t("memories.toasts.error", "Operation failed"),
            );
            return false;
          }

          await sleep(MEMORY_CREATE_POLL_INTERVAL_MS);
        }

        console.error("[Memories] create job polling timeout", { jobId });
        setCreateJob({
          jobId,
          status: "failed",
          progress: 0,
          error: t("memories.toasts.timeout", "Create timed out"),
        });
        toast.error(t("memories.toasts.timeout", "Create timed out"));
        return false;
      } catch (error) {
        console.error("[Memories] create job polling failed", error);
        setCreateJob({
          jobId,
          status: "failed",
          progress: 0,
          error: t("memories.toasts.error", "Operation failed"),
        });
        toast.error(t("memories.toasts.error", "Operation failed"));
        return false;
      } finally {
        if (createJobPollingIdRef.current === jobId) {
          createJobPollingIdRef.current = null;
        }
      }
    },
    [refresh, t],
  );

  const resumeActiveCreateJob = useCallback(async () => {
    try {
      const payload = await memoriesApi.getActiveCreateJob();
      if (!payload) {
        setCreateJob(DEFAULT_CREATE_JOB_STATE);
        return;
      }

      setLastPayload(payload);
      const raw = toRecord(payload);
      const jobId = asString(raw?.job_id) ?? asString(raw?.jobId);
      const status = asString(raw?.status)?.toLowerCase() ?? "running";
      const progress =
        typeof raw?.progress === "number"
          ? Math.max(0, Math.min(100, raw.progress))
          : status === "success"
            ? 100
            : 0;
      const errorMessage = asString(raw?.error);

      if (!jobId) {
        setCreateJob(DEFAULT_CREATE_JOB_STATE);
        return;
      }

      setCreateJob({
        jobId,
        status,
        progress,
        error: errorMessage,
      });

      if (status === "queued" || status === "running") {
        void waitForCreateJob(jobId);
      }
    } catch (error) {
      console.error("[Memories] load active create job failed", error);
    }
  }, [waitForCreateJob]);

  useEffect(() => {
    void resumeActiveCreateJob();
  }, [resumeActiveCreateJob]);

  const create = useCallback(
    async (input: MemoryCreateInput) => {
      setIsMutating(true);
      resetCreateJob();
      try {
        const payload = await memoriesApi.create(input);
        setLastPayload(payload);

        const raw = toRecord(payload);
        const jobId = asString(raw?.job_id) ?? asString(raw?.jobId);
        const status = asString(raw?.status)?.toLowerCase() ?? "queued";
        if (jobId) {
          setCreateJob({
            jobId,
            status,
            progress: status === "success" ? 100 : 0,
            error: null,
          });
          void waitForCreateJob(jobId);
          return true;
        }

        toast.success(t("memories.toasts.created", "Memory created"));
        await refresh({ silent: true });
        return true;
      } catch (error) {
        console.error("[Memories] create failed", error);
        toast.error(t("memories.toasts.error", "Operation failed"));
        setCreateJob({
          jobId: null,
          status: "failed",
          progress: 0,
          error: t("memories.toasts.error", "Operation failed"),
        });
        return false;
      } finally {
        setIsMutating(false);
      }
    },
    [refresh, resetCreateJob, t, waitForCreateJob],
  );

  const getById = useCallback(
    async (memoryId: string) => {
      setIsMutating(true);
      try {
        const payload = await memoriesApi.get(memoryId);
        setLastPayload(payload);
      } catch (error) {
        console.error("[Memories] get failed", error);
        toast.error(t("memories.toasts.error", "Operation failed"));
      } finally {
        setIsMutating(false);
      }
    },
    [t],
  );

  const getHistory = useCallback(
    async (memoryId: string) => {
      setIsMutating(true);
      try {
        const payload = await memoriesApi.getHistory(memoryId);
        setLastPayload(payload);
      } catch (error) {
        console.error("[Memories] history failed", error);
        toast.error(t("memories.toasts.error", "Operation failed"));
      } finally {
        setIsMutating(false);
      }
    },
    [t],
  );

  const update = useCallback(
    async (memoryId: string, input: MemoryUpdateInput) => {
      setIsMutating(true);
      try {
        const payload = await memoriesApi.update(memoryId, input);
        setLastPayload(payload);
        toast.success(t("memories.toasts.updated", "Memory updated"));
        await refresh({ silent: true });
      } catch (error) {
        console.error("[Memories] update failed", error);
        toast.error(t("memories.toasts.error", "Operation failed"));
      } finally {
        setIsMutating(false);
      }
    },
    [refresh, t],
  );

  const remove = useCallback(
    async (memoryId: string) => {
      setIsMutating(true);
      try {
        const payload = await memoriesApi.remove(memoryId);
        setLastPayload(payload);
        toast.success(t("memories.toasts.deleted", "Memory deleted"));
        await refresh({ silent: true });
      } catch (error) {
        console.error("[Memories] remove failed", error);
        toast.error(t("memories.toasts.error", "Operation failed"));
      } finally {
        setIsMutating(false);
      }
    },
    [refresh, t],
  );

  const clearAll = useCallback(async () => {
    setIsMutating(true);
    try {
      const payload = await memoriesApi.clearAll();
      setLastPayload(payload);
      toast.success(t("memories.toasts.cleared", "All memories cleared"));
      await refresh({ silent: true });
    } catch (error) {
      console.error("[Memories] clear all failed", error);
      toast.error(t("memories.toasts.error", "Operation failed"));
    } finally {
      setIsMutating(false);
    }
  }, [refresh, t]);

  return {
    items,
    isLoading,
    isMutating,
    createJob,
    lastPayload,
    mode,
    refresh,
    search,
    create,
    resetCreateJob,
    getById,
    getHistory,
    update,
    remove,
    clearAll,
  };
}
