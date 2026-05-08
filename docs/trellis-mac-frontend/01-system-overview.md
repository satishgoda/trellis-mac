# 01. System Overview

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-OVR-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| System | TRELLIS Workflow UI and API Server |
| Prepared on | 2026-05-07 |

## Executive Summary

The TRELLIS Workflow frontend system is a local web application that lets a user configure, observe, and execute the TRELLIS image-to-3D pipeline step by step. It replaces a single terminal-driven command with a managed workflow console. The browser UI collects tunable parameters and presents pipeline status, while the Python API server executes the existing TRELLIS codebase and stores transient workflow runtime state.

## System Objectives

- Make the TRELLIS generation pipeline understandable and controllable by exposing each stage as a user-runnable step.
- Preserve the existing command-line generation path while adding a professional UI/API workflow layer.
- Provide clear operational visibility through status, logs, metrics, and generated artifact links.
- Keep heavyweight model state on the Python server to avoid reloading pipeline objects for every action.
- Create documentation and test artifacts that support defined-process delivery expectations.

## Scope

### In Scope

- React single-page app built with Vite.
- FastAPI server for workflow definitions, sessions, step execution, status polling, and artifact serving.
- Configurable workflow parameters including input image, model id, device, seed, pipeline type, texture controls, sampler steps, token limits, and decimation target.
- Step-by-step execution of the TRELLIS pipeline:
  - Load Pipeline
  - Load Image
  - Preprocess Image
  - Build Conditioning
  - Sample Sparse Structure
  - Sample Shape SLat
  - Sample Texture SLat
  - Decode Mesh
  - Export Model
- Generated artifact visibility for GLB, OBJ, preprocessed image, and texture files when available.
- Local development operation using `127.0.0.1`.

### Out of Scope

- Remote multi-tenant deployment.
- Authentication and authorization.
- Persistent database-backed workflow storage.
- Distributed job queues.
- Browser-side 3D model preview.
- External CMM/CMMI certification.

## Stakeholders

| Role | Interest |
|---|---|
| End user | Configure and run a TRELLIS model generation workflow without relying on terminal logs alone |
| ML/graphics engineer | Inspect pipeline stages, parameters, runtime failures, and generated artifacts |
| Frontend engineer | Maintain React components, state handling, API integration, and responsive layout |
| Backend engineer | Maintain FastAPI endpoints, workflow orchestration, runtime session state, and artifact export |
| QA engineer | Verify requirements, API contracts, UI behavior, and workflow acceptance criteria |
| Release owner | Control baselines, dependencies, test evidence, and change approval |

## System Context

![TRELLIS Workflow system context diagram](diagrams/01-system-context.svg)

| Element | Responsibility |
|---|---|
| Browser | Hosts the React workflow console |
| React app | Renders parameters, step list, step details, logs, and artifacts |
| FastAPI server | Exposes workflow and session APIs |
| WorkflowRunner | Owns session records, step ordering, background execution, and logs |
| TRELLIS.2 pipeline | Performs model loading, image conditioning, sampling, latent decoding, and mesh generation |
| Exporter | Produces GLB/OBJ artifacts and optional textures |
| File system | Stores generated artifacts under `outputs/<session-id>/` |

## High-Level Workflow

1. User starts the Python API server.
2. User starts the React development server.
3. UI loads the default workflow definition from the API.
4. User edits parameters and creates a session.
5. API stores a `WorkflowState` plus an in-memory `RuntimeContext`.
6. User runs the next step, a specific step, or the remaining workflow.
7. API executes steps sequentially, captures logs, and updates step state.
8. UI polls the session while work is running.
9. Export step writes artifacts and exposes URLs to the UI.

## Operational Assumptions

- The application is run locally on macOS for Apple Silicon workflows.
- The Python virtual environment has TRELLIS dependencies installed.
- Hugging Face model access is already configured where gated models are required.
- The UI runs on `http://127.0.0.1:5173` and the API runs on `http://127.0.0.1:8000` during development.
- Workflow sessions are in memory and are lost when the API process exits.

## Constraints

- Model loading and sampling can be long-running and memory-intensive.
- Only one worker is configured by default to avoid overloading local GPU and memory resources.
- Artifact serving is file-system based.
- The current CORS policy is intended for local development origins.
- Step execution order is enforced by the backend.

## CMM/CMMI Level 3 Process Alignment

This system uses a defined process baseline for requirements, design, verification, validation, configuration management, and risk management. The documents in this folder provide repeatable artifacts suitable for internal quality review and appraisal preparation.

## Approval Checklist

| Item | Status |
|---|---|
| Product scope documented | Complete |
| Stakeholders documented | Complete |
| Operational assumptions documented | Complete |
| Major constraints documented | Complete |
| CMM/CMMI alignment position documented | Complete |
