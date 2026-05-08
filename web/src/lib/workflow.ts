import type { StepState, StepStatus, WorkflowConfig } from '../types';

export const defaultConfig: WorkflowConfig = {
  image_path: 'assets/shoe_input.png',
  output_name: null,
  output_dir: 'outputs',
  model_id: 'microsoft/TRELLIS.2-4B',
  device: 'mps',
  seed: 42,
  pipeline_type: '512',
  texture_size: 1024,
  no_texture: false,
  sampler_steps: null,
  num_samples: 1,
  max_num_tokens: 49152,
  preprocess_image: true,
  texture_backend: 'auto',
  decimation_target: 200000
};

export function nextRunnableStep(steps: StepState[]): StepState | undefined {
  return steps.find((step) => step.status !== 'completed' && step.status !== 'skipped');
}

export function statusLabel(status: StepStatus): string {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

export function statusTone(status: StepStatus): string {
  return {
    pending: 'tone-pending',
    running: 'tone-running',
    completed: 'tone-completed',
    skipped: 'tone-skipped',
    failed: 'tone-failed'
  }[status];
}

export function formatBytes(bytes?: number | null): string {
  if (!bytes) {
    return '0 B';
  }
  const units = ['B', 'KB', 'MB', 'GB'];
  let value = bytes;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }
  const precision = value >= 10 || unitIndex === 0 || Number.isInteger(value) ? 0 : 1;
  return `${value.toFixed(precision)} ${units[unitIndex]}`;
}

export function formatDuration(seconds?: number | null): string {
  if (seconds == null) {
    return '';
  }
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const rest = Math.round(seconds % 60);
  return `${minutes}m ${rest}s`;
}
