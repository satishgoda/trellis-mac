import { Box, ExternalLink } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';

import { modelArtifactExtension, previewableModelArtifacts } from '../lib/artifacts';
import type { Artifact } from '../types';

type LoadStatus = 'empty' | 'loading' | 'ready' | 'error';

type Props = {
  artifacts: Artifact[];
};

export function ModelPreview({ artifacts }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedPath, setSelectedPath] = useState('');
  const [loadStatus, setLoadStatus] = useState<LoadStatus>('empty');
  const [loadError, setLoadError] = useState<string | null>(null);

  const previewArtifacts = useMemo(() => previewableModelArtifacts(artifacts), [artifacts]);
  const selectedArtifact = previewArtifacts.find((artifact) => artifact.path === selectedPath) ?? previewArtifacts[0];

  useEffect(() => {
    if (previewArtifacts.length === 0) {
      setSelectedPath('');
      setLoadStatus('empty');
      setLoadError(null);
      return;
    }
    if (!previewArtifacts.some((artifact) => artifact.path === selectedPath)) {
      setSelectedPath(previewArtifacts[0].path);
    }
  }, [previewArtifacts, selectedPath]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || !selectedArtifact) {
      return undefined;
    }

    let disposed = false;
    let frameId = 0;
    let activeModel: THREE.Object3D | null = null;
    setLoadStatus('loading');
    setLoadError(null);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8fafc);

    const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 1000);
    camera.position.set(2.5, 1.8, 2.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.domElement.className = 'model-canvas';
    renderer.domElement.setAttribute('aria-label', '3D model preview canvas');
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.6;
    controls.target.set(0, 0, 0);

    const ambientLight = new THREE.HemisphereLight(0xffffff, 0xd4dae3, 2.4);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 2.8);
    keyLight.position.set(3, 4, 5);
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xbfd7ff, 1.2);
    fillLight.position.set(-4, 2, -3);
    scene.add(fillLight);

    const grid = new THREE.GridHelper(3.2, 16, 0xcbd5e1, 0xe2e8f0);
    grid.position.y = -1.05;
    scene.add(grid);

    const resizeObserver = new ResizeObserver(() => resizeRenderer(container, renderer, camera));
    resizeObserver.observe(container);
    resizeRenderer(container, renderer, camera);

    const mountModel = (model: THREE.Object3D) => {
      if (disposed) {
        disposeObject(model);
        return;
      }
      activeModel = model;
      prepareModel(model, selectedArtifact.name);
      scene.add(model);
      fitCameraToObject(camera, controls, model);
      setLoadStatus('ready');
    };

    const handleError = (error: unknown) => {
      if (disposed) {
        return;
      }
      setLoadStatus('error');
      setLoadError(modelLoadErrorMessage(error));
    };

    const extension = modelArtifactExtension(selectedArtifact.name);
    if (extension === 'glb') {
      new GLTFLoader().load(selectedArtifact.url, (gltf) => mountModel(gltf.scene), undefined, handleError);
    } else {
      new OBJLoader().load(selectedArtifact.url, mountModel, undefined, handleError);
    }

    const animate = () => {
      controls.update();
      renderer.render(scene, camera);
      frameId = window.requestAnimationFrame(animate);
    };
    animate();

    return () => {
      disposed = true;
      window.cancelAnimationFrame(frameId);
      resizeObserver.disconnect();
      controls.dispose();
      if (activeModel) {
        disposeObject(activeModel);
      }
      scene.clear();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [selectedArtifact]);

  return (
    <section className="panel model-preview-panel" aria-label="Model preview">
      <div className="panel-heading model-preview-heading">
        <h2>Preview</h2>
        {previewArtifacts.length > 0 && selectedArtifact ? (
          <div className="model-preview-controls">
            <select
              className="model-select"
              aria-label="Preview model artifact"
              value={selectedArtifact.path}
              onChange={(event) => setSelectedPath(event.currentTarget.value)}
            >
              {previewArtifacts.map((artifact) => (
                <option key={artifact.path} value={artifact.path}>
                  {artifact.name}
                </option>
              ))}
            </select>
            <a
              className="icon-link"
              href={selectedArtifact.url}
              target="_blank"
              rel="noreferrer"
              title="Open model artifact"
              aria-label={`Open ${selectedArtifact.name}`}
            >
              <ExternalLink size={16} />
            </a>
          </div>
        ) : (
          <span>No model</span>
        )}
      </div>
      {previewArtifacts.length === 0 ? (
        <div className="empty-state model-empty-state">
          <Box size={18} />
          <span>Generated GLB and OBJ files will appear here.</span>
        </div>
      ) : (
        <div className="model-viewer" ref={containerRef} data-load-status={loadStatus}>
          {loadStatus === 'loading' && <div className="model-status">Loading model...</div>}
          {loadStatus === 'error' && <div className="model-status model-status-error">{loadError}</div>}
        </div>
      )}
    </section>
  );
}

function resizeRenderer(container: HTMLElement, renderer: THREE.WebGLRenderer, camera: THREE.PerspectiveCamera) {
  const width = Math.max(container.clientWidth, 1);
  const height = Math.max(container.clientHeight, 1);
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

function prepareModel(model: THREE.Object3D, fileName: string) {
  const isObj = modelArtifactExtension(fileName) === 'obj';

  model.traverse((child) => {
    if (!(child instanceof THREE.Mesh)) {
      return;
    }
    child.castShadow = true;
    child.receiveShadow = true;
    if (isObj || !child.material) {
      child.material = new THREE.MeshStandardMaterial({
        color: 0x8da6bf,
        metalness: 0.05,
        roughness: 0.72
      });
    }
  });

  const box = new THREE.Box3().setFromObject(model);
  if (box.isEmpty()) {
    return;
  }
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDimension = Math.max(size.x, size.y, size.z, 1);
  model.position.sub(center);
  model.scale.setScalar(2.1 / maxDimension);
}

function fitCameraToObject(camera: THREE.PerspectiveCamera, controls: OrbitControls, model: THREE.Object3D) {
  const box = new THREE.Box3().setFromObject(model);
  const sphere = box.getBoundingSphere(new THREE.Sphere());
  const radius = Math.max(sphere.radius, 0.7);
  const distance = radius * 3.1;

  camera.near = Math.max(radius / 100, 0.01);
  camera.far = radius * 100;
  camera.position.set(distance, distance * 0.72, distance);
  camera.lookAt(sphere.center);
  camera.updateProjectionMatrix();

  controls.target.copy(sphere.center);
  controls.minDistance = radius * 0.55;
  controls.maxDistance = radius * 8;
  controls.update();
}

function modelLoadErrorMessage(error: unknown): string {
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return 'Unable to load this model artifact.';
}

function disposeObject(object: THREE.Object3D) {
  object.traverse((child) => {
    if (!(child instanceof THREE.Mesh)) {
      return;
    }
    child.geometry.dispose();
    disposeMaterial(child.material);
  });
}

function disposeMaterial(material: THREE.Material | THREE.Material[]) {
  if (Array.isArray(material)) {
    material.forEach(disposeMaterial);
    return;
  }
  for (const value of Object.values(material as unknown as Record<string, unknown>)) {
    if (value instanceof THREE.Texture) {
      value.dispose();
    }
  }
  material.dispose();
}