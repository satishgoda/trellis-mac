import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { ArtifactPanel } from './ArtifactPanel';
import type { Artifact } from '../types';

describe('ArtifactPanel', () => {
  it('renders served artifacts as download links', () => {
    render(
      <ArtifactPanel
        artifacts={[
          {
            name: 'popeye.glb',
            kind: 'model',
            path: 'assets/dev/session-1/popeye.glb',
            url: '/api/artifacts/assets/dev/session-1/popeye.glb',
            size_bytes: 3
          }
        ]}
      />
    );

    const link = screen.getByRole('link', { name: /popeye\.glb/i });
    expect(link).toHaveAttribute('href', '/api/artifacts/assets/dev/session-1/popeye.glb');
    expect(link).toHaveAttribute('download', 'popeye.glb');
    expect(link).not.toHaveAttribute('target');
  });

  it('does not render placeholder links for artifacts without urls', () => {
    const artifacts: Artifact[] = [
      {
        name: 'orphan.glb',
        kind: 'model',
        path: 'assets/dev/session-1/orphan.glb',
        url: null,
        size_bytes: 3
      }
    ];

    render(<ArtifactPanel artifacts={artifacts} />);

    expect(screen.getByText('orphan.glb')).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /orphan\.glb/i })).not.toBeInTheDocument();
    expect(document.querySelector('a[href="#"]')).not.toBeInTheDocument();
  });
});