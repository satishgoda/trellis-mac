import { describe, expect, it } from 'vitest';

import { defaultConfig, formatBytes, nextRunnableStep } from './workflow';
import type { StepState } from '../types';

describe('workflow helpers', () => {
  it('finds the first step that still needs execution', () => {
    const steps: StepState[] = [
      { id: 'load_pipeline', title: 'Load Pipeline', status: 'completed', metrics: {} },
      { id: 'load_image', title: 'Load Image', status: 'skipped', metrics: {} },
      { id: 'sample_sparse_structure', title: 'Sample Sparse Structure', status: 'pending', metrics: {} }
    ];

    expect(nextRunnableStep(steps)?.id).toBe('sample_sparse_structure');
  });

  it('formats artifact sizes for compact display', () => {
    expect(formatBytes(9 * 1024 * 1024)).toBe('9 MB');
  });

  it('uses the sample image as the default input', () => {
    expect(defaultConfig.image_path).toBe('assets/shoe_input.png');
  });
});
