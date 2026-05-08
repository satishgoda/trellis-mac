import { describe, expect, it } from 'vitest';

import { modelArtifactExtension, previewableModelArtifacts } from './artifacts';
import type { Artifact } from '../types';

describe('artifact helpers', () => {
  it('detects supported model extensions case-insensitively', () => {
    expect(modelArtifactExtension('shoe.GLB')).toBe('glb');
    expect(modelArtifactExtension('shoe.obj')).toBe('obj');
    expect(modelArtifactExtension('shoe.png')).toBe('');
  });

  it('keeps only served GLB and OBJ artifacts for preview', () => {
    const artifacts: Artifact[] = [
      { name: 'shoe.glb', kind: 'model', path: 'outputs/session/shoe.glb', url: '/outputs/session/shoe.glb' },
      { name: 'shoe.obj', kind: 'mesh', path: 'outputs/session/shoe.obj', url: '/outputs/session/shoe.obj' },
      { name: 'shoe-local.glb', kind: 'model', path: 'docs/assets/shoe-local.glb', url: null },
      { name: 'shoe_basecolor.png', kind: 'texture', path: 'outputs/session/shoe_basecolor.png', url: '/outputs/session/shoe_basecolor.png' }
    ];

    expect(previewableModelArtifacts(artifacts).map((artifact) => artifact.name)).toEqual(['shoe.glb', 'shoe.obj']);
  });
});