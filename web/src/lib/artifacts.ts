import type { Artifact } from '../types';

export type ModelArtifactExtension = 'glb' | 'obj';
export type PreviewableModelArtifact = Artifact & { url: string };

export function modelArtifactExtension(name: string): ModelArtifactExtension | '' {
  const extension = name.toLowerCase().split('.').pop();
  return extension === 'glb' || extension === 'obj' ? extension : '';
}

export function isPreviewableModelArtifact(artifact: Artifact): artifact is PreviewableModelArtifact {
  return Boolean(artifact.url && modelArtifactExtension(artifact.name));
}

export function previewableModelArtifacts(artifacts: Artifact[]): PreviewableModelArtifact[] {
  return artifacts.filter(isPreviewableModelArtifact);
}