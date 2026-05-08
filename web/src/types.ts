export type StepStatus = 'pending' | 'running' | 'completed' | 'skipped' | 'failed';
export type ParameterControl = 'text' | 'number' | 'select' | 'checkbox';

export interface ParameterDefinition {
  key: keyof WorkflowConfig;
  label: string;
  control: ParameterControl;
  step_id: string;
  description: string;
  default: unknown;
  options?: string[] | null;
  minimum?: number | null;
  maximum?: number | null;
}

export interface StepDefinition {
  id: string;
  title: string;
  description: string;
  parameter_keys: string[];
}

export interface WorkflowDefinition {
  steps: StepDefinition[];
  parameters: ParameterDefinition[];
}

export interface WorkflowConfig {
  image_path: string;
  output_name: string | null;
  output_dir: string;
  model_id: string;
  device: 'mps' | 'cpu';
  seed: number;
  pipeline_type: '512' | '1024' | '1024_cascade';
  texture_size: 512 | 1024 | 2048;
  no_texture: boolean;
  sampler_steps: number | null;
  num_samples: number;
  max_num_tokens: number;
  preprocess_image: boolean;
  texture_backend: 'auto' | 'metal' | 'kdtree' | 'none';
  decimation_target: number;
}

export interface StepState {
  id: string;
  title: string;
  status: StepStatus;
  started_at?: string | null;
  finished_at?: string | null;
  duration_seconds?: number | null;
  summary?: string | null;
  error?: string | null;
  metrics: Record<string, unknown>;
}

export interface LogEntry {
  timestamp: string;
  step_id?: string | null;
  level: 'info' | 'warning' | 'error';
  message: string;
}

export interface Artifact {
  name: string;
  kind: 'image' | 'model' | 'mesh' | 'texture' | 'other';
  path: string;
  url?: string | null;
  size_bytes?: number | null;
}

export interface WorkflowState {
  session_id: string;
  config: WorkflowConfig;
  steps: StepState[];
  logs: LogEntry[];
  artifacts: Artifact[];
  busy: boolean;
  active_step_id?: string | null;
  created_at: string;
  updated_at: string;
}
