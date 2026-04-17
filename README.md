# JarvisX: Desktop E2E Computer Control Assistant

JarvisX is a desktop-first Python AI assistant designed to combine:

- conversational chat UX (floating widget + popup chat window),
- backend/chat orchestration,
- and end-to-end computer control modules.

This repository has been intentionally refocused to keep the desktop E2E-control product path and remove non-core stacks.

## Project Goal

The primary goal of this build is to let a user issue natural language instructions (for example, creating or initializing a project workflow) and route those instructions through JarvisX orchestration modules that can execute actions in a computer-control context.

In short:

- user asks in chat,
- JarvisX interprets intent,
- JarvisX routes to the right control/automation path,
- response and status are shown in the desktop widget.

## High-Level Architecture

```text
Desktop Widget UI
  -> Chatbot Adapter
    -> Local API backend (preferred)
       OR
    -> Cloud LLM fallback
  -> Core Orchestrator + Tool Router
    -> Computer/automation/system modules
```

## Core Runtime Components

### 1) Desktop Entry and Application Bootstrap

- `desktop/src/main.py`
  - application entrypoint,
  - creates `QApplication`,
  - boots `JarvisApp`.

- `desktop/src/app.py`
  - wires together widget button + chat popup,
  - sets tray integration (toggle chat, show button, quit),
  - handles popup lifecycle and placement.

### 2) Desktop UI Layer

- `desktop/src/widget_ui/widget_button.py`
  - floating draggable launcher button.

- `desktop/src/widget_ui/chatbot_popup.py`
  - modern glass-style popup UI,
  - streaming response rendering via worker thread,
  - markdown-like formatting for assistant output,
  - input composer + send flow.

### 3) Chat Routing / Adapter Layer

- `desktop/src/backend/chatbot_adapter.py`
  - first tries local backend API request via `APIClient`,
  - falls back to cloud LLM client if backend is unavailable,
  - returns normalized text response to the chat UI.

- `desktop/src/services/api_client.py`
  - handles API base URL, auth header support, and request calls.

### 4) Intelligence + Execution Layer

- `core/`
  - orchestration, routing, planning, and action extraction modules.
  - key examples include orchestrator/route/execution files such as:
    - `core/unified_orchestrator.py`
    - `core/tool_router.py`
    - `core/computer_access.py`
    - `core/hybrid_brain.py`

- `automation/`
  - automation-related execution helpers and workflows.

- `system_monitor/`
  - system-level monitoring and diagnostics execution surfaces.

- `speech/`
  - speech-related utilities (STT/TTS pipeline pieces) for voice-capable paths.

### 5) Backend and Model Connectivity

- `backend/`
  - local API/backend services for chat and related integrations.

- `cloud_llm_client.py`
  - cloud inference client fallback path.

- `models/jarvis-llm-brain-final/`
  - retained active model assets path.

## Request/Response Flow (Desktop Chat)

1. User opens popup and submits a prompt.
2. `chatbot_popup.py` starts a background response worker.
3. Worker calls `ChatbotAdapter.get_response()`.
4. Adapter attempts local API first (`APIClient.post("/chat", ...)`).
5. If local API is unavailable, adapter tries cloud fallback.
6. Response is streamed back into the popup and rendered.

## Repository Layout (Current Focused Build)

```text
JarvisX/
  desktop/
    src/
      main.py
      app.py
      widget_ui/
      backend/
      services/
  core/
  automation/
  system_monitor/
  speech/
  backend/
  models/jarvis-llm-brain-final/
  cloud_llm_client.py
  requirements.txt
```

## Prerequisites

- Python 3.11 recommended
- macOS/Linux/Windows environment with GUI support for PyQt
- Optional: running local backend API for best response path
- Optional: cloud model URL configured for fallback mode

## Installation

From repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r desktop/requirements.txt
```

## Run the Desktop App

```bash
cd desktop/src
python3.11 main.py
```

## Configuration Notes

- Local API endpoint defaults are managed by `desktop/src/services/api_client.py` config flow.
- Cloud fallback uses `cloud_llm_client.py` and related environment configuration.
- Existing local `.db` files are retained for state/history continuity.

## Validation Checklist

After setup, validate:

- floating button appears and is draggable,
- popup opens/closes correctly,
- prompt submission works,
- streamed response rendering appears in chat,
- backend path works (or cloud fallback path works if backend unavailable).

## Extending JarvisX

Recommended extension points:

- Add new task domains in `core/tool_router.py`.
- Add execution handlers in `automation/` or `system_monitor/`.
- Extend popup UI behaviors in `desktop/src/widget_ui/chatbot_popup.py`.
- Add adapter-level routing logic in `desktop/src/backend/chatbot_adapter.py`.

## Important Scope Note

This repository version is intentionally narrowed to the desktop E2E-control product path. If you plan to reintroduce additional stacks later (mobile/web/training/deployment pipelines), do so as separate modules or repositories to keep the runtime core maintainable.

