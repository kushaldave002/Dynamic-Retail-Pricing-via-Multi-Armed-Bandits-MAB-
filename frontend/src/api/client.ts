import { buildExperimentFixture, catalogFixture, precomputedFixture } from "./fixtures";
import type {
  DatasetCatalog,
  ExperimentRequest,
  ExperimentResponse,
  PrecomputedResponse,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchDatasets(): Promise<DatasetCatalog> {
  try {
    return await request<DatasetCatalog>("/datasets");
  } catch {
    return catalogFixture;
  }
}

export async function fetchPrecomputed(): Promise<PrecomputedResponse> {
  return request<PrecomputedResponse>("/experiments/precomputed");
}

export async function fetchPrecomputedFixture(): Promise<PrecomputedResponse> {
  return precomputedFixture;
}

export async function runExperiment(payload: ExperimentRequest): Promise<ExperimentResponse> {
  return request<ExperimentResponse>("/experiments/run", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function runExperimentFixture(payload: ExperimentRequest): Promise<ExperimentResponse> {
  return buildExperimentFixture(payload);
}
