import type { WorkflowConfig, WorkflowDefinition, WorkflowState } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // Keep the HTTP status text.
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const workflowApi = {
  getDefinition: () => request<WorkflowDefinition>('/api/workflows/default'),
  createSession: (config: WorkflowConfig) =>
    request<WorkflowState>('/api/sessions', {
      method: 'POST',
      body: JSON.stringify(config)
    }),
  getSession: (sessionId: string) => request<WorkflowState>(`/api/sessions/${sessionId}`),
  runStep: (sessionId: string, stepId: string) =>
    request<WorkflowState>(`/api/sessions/${sessionId}/steps/${stepId}/run`, { method: 'POST' }),
  runNext: (sessionId: string) => request<WorkflowState>(`/api/sessions/${sessionId}/run-next`, { method: 'POST' }),
  runAll: (sessionId: string) => request<WorkflowState>(`/api/sessions/${sessionId}/run-all`, { method: 'POST' })
};
