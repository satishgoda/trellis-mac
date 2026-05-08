import { Download, FileBox, Image as ImageIcon } from 'lucide-react';

import type { Artifact } from '../types';
import { formatBytes } from '../lib/workflow';

type Props = {
  artifacts: Artifact[];
};

export function ArtifactPanel({ artifacts }: Props) {
  return (
    <section className="panel artifact-panel" aria-label="Generated artifacts">
      <div className="panel-heading">
        <h2>Artifacts</h2>
        <span>{artifacts.length} files</span>
      </div>
      {artifacts.length === 0 ? (
        <div className="empty-state">Generated files will appear here.</div>
      ) : (
        <div className="artifact-list">
          {artifacts.map((artifact) => {
            const content = <ArtifactRowContent artifact={artifact} />;
            return artifact.url ? (
              <a key={artifact.path} href={artifact.url} className="artifact-row" download={artifact.name}>
                {content}
              </a>
            ) : (
              <div key={artifact.path} className="artifact-row artifact-row-disabled" aria-disabled="true">
                {content}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

function ArtifactRowContent({ artifact }: { artifact: Artifact }) {
  return (
    <>
      <span className="artifact-icon" aria-hidden="true">
        {artifact.kind === 'image' || artifact.kind === 'texture' ? <ImageIcon size={18} /> : <FileBox size={18} />}
      </span>
      <span>
        <strong>{artifact.name}</strong>
        <small>{artifact.path} - {formatBytes(artifact.size_bytes)}</small>
      </span>
      <Download size={16} />
    </>
  );
}
