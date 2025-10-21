# Technical Specification: Terminal Assistant UI

**Version:** 1.0
**Created:** 2025-10-21
**Status:** Draft
**Author:** TechSpecExpert

---

## 1. Executive Summary

This specification outlines the design and implementation of a web-based user interface that surfaces real-time terminal interactions with an AI assistant. The solution integrates into the existing `content-gen` application architecture, adding a new feature alongside the existing video generation capabilities.

### Key Objectives
- Real-time streaming of terminal session input/output to web UI
- Bidirectional communication between terminal and browser
- Minimal disruption to existing codebase
- Scalable WebSocket-based architecture

---

## 2. Filesystem Location & Integration Strategy

### 2.1 Current Project Structure Analysis

The existing project follows a monorepo pattern within `/Users/chris/big-3-super-agent/apps/content-gen/`:

```
apps/content-gen/
├── backend/              # FastAPI backend (port 4444)
│   └── src/content_gen_backend/
│       ├── main.py       # FastAPI app with CORS
│       ├── routers/      # API route modules
│       ├── services/     # Business logic
│       └── models/       # Pydantic models
├── frontend/             # Existing Vue 3 + Vite app (port 3333)
│   ├── src/
│   ├── vite.config.ts
│   └── package.json
├── specs/                # Documentation
├── agents/               # Agent working directory
└── ai_docs/              # AI documentation
```

### 2.2 Recommended Location for Terminal UI

**OPTION A: Integrate into Existing Frontend (RECOMMENDED)**

Create a new route/view within the existing Vue 3 application:

```
apps/content-gen/frontend/src/
├── views/
│   ├── VideoGeneration.vue  # Existing video UI
│   └── TerminalAssistant.vue # NEW: Terminal UI
├── components/
│   └── terminal/             # NEW: Terminal components
│       ├── TerminalOutput.vue
│       ├── TerminalInput.vue
│       └── MessageBubble.vue
├── composables/
│   └── useTerminalSession.ts # NEW: WebSocket logic
└── types/
    └── terminal.ts           # NEW: TypeScript types
```

**Rationale:**
- Reuses existing Vite build pipeline
- Shares CORS configuration
- Unified deployment
- Single port for all features (3333)
- Consistent styling and component library

**OPTION B: Separate Vite Application**

If isolation is required, create a parallel frontend:

```
apps/content-gen/
├── backend/              # Shared backend
├── frontend/             # Existing video UI
└── terminal-ui/          # NEW: Separate Vite app (port 3334)
    ├── src/
    │   ├── App.vue
    │   ├── components/
    │   └── composables/
    ├── vite.config.ts
    └── package.json
```

**Use this when:**
- Terminal UI requires completely different tech stack
- Deployment needs differ significantly
- Team separation necessitates independent repos

**For this spec, we proceed with OPTION A (integrated approach).**

---

## 3. Architecture Overview

### 3.1 System Components

```
┌─────────────────┐     WebSocket      ┌──────────────────┐
│   Browser UI    │◄──────────────────►│  FastAPI Backend │
│  (Vue 3 + Vite) │     wss://...      │   (Port 4444)    │
└─────────────────┘                    └──────────────────┘
                                              │
                                              │ PTY/Process
                                              ▼
                                       ┌──────────────────┐
                                       │  Terminal Session│
                                       │  (pty or exec)   │
                                       └──────────────────┘
```

### 3.2 Technology Stack

**Frontend:**
- **Framework:** Vue 3 (Composition API)
- **Build Tool:** Vite
- **Language:** TypeScript
- **WebSocket Client:** Native WebSocket API or `socket.io-client`
- **Styling:** CSS Modules or existing UI framework

**Backend:**
- **Framework:** FastAPI (Python)
- **WebSocket:** `fastapi.websockets` or `python-socketio`
- **Terminal Emulation:** `ptyprocess` or `subprocess`
- **Session Management:** In-memory dict or Redis

---

## 4. Backend Implementation

### 4.1 New Backend Components

**File Structure:**
```
backend/src/content_gen_backend/
├── routers/
│   └── terminal.py          # NEW: WebSocket endpoint
├── services/
│   ├── terminal_service.py  # NEW: PTY management
│   └── session_manager.py   # NEW: Session lifecycle
└── models/
    └── terminal_models.py   # NEW: Message schemas
```

### 4.2 API Endpoints

#### WebSocket Endpoint: `/ws/terminal/{session_id}`

**Protocol:** WebSocket
**Purpose:** Bidirectional streaming of terminal I/O

**Message Format (JSON):**

```json
// Client → Server (Input)
{
  "type": "input",
  "data": "ls -la\n",
  "session_id": "abc123",
  "timestamp": "2025-10-21T12:00:00Z"
}

// Server → Client (Output)
{
  "type": "output",
  "data": "total 32\ndrwxr-xr-x  12 chris  staff   384 Oct 17 01:27 .\n",
  "session_id": "abc123",
  "timestamp": "2025-10-21T12:00:01Z"
}

// Server → Client (Status)
{
  "type": "status",
  "status": "connected" | "disconnected" | "error",
  "message": "Terminal session established",
  "session_id": "abc123"
}
```

#### REST Endpoint: `POST /api/v1/terminal/sessions`

**Purpose:** Create new terminal session

**Request:**
```json
{
  "shell": "/bin/bash",  // optional, defaults to system shell
  "cwd": "/Users/chris/big-3-super-agent/apps/content-gen",
  "env": {}  // optional environment variables
}
```

**Response:**
```json
{
  "session_id": "abc123",
  "websocket_url": "/ws/terminal/abc123",
  "created_at": "2025-10-21T12:00:00Z",
  "status": "active"
}
```

#### REST Endpoint: `DELETE /api/v1/terminal/sessions/{session_id}`

**Purpose:** Terminate terminal session

**Response:**
```json
{
  "session_id": "abc123",
  "status": "terminated",
  "terminated_at": "2025-10-21T12:05:00Z"
}
```

### 4.3 Backend Service Implementation

**File:** `backend/src/content_gen_backend/services/terminal_service.py`

**Key Responsibilities:**
- Spawn PTY (pseudo-terminal) processes
- Read from PTY stdout/stderr → send to WebSocket
- Receive from WebSocket → write to PTY stdin
- Handle process lifecycle (start, stop, cleanup)

**Core Logic:**
```python
import ptyprocess
import asyncio
from typing import Dict, Optional

class TerminalService:
    def __init__(self):
        self.sessions: Dict[str, ptyprocess.PtyProcess] = {}

    async def create_session(self, session_id: str, shell: str = "/bin/bash", cwd: str = "."):
        """Spawn a new PTY process"""
        process = ptyprocess.PtyProcess.spawn([shell], cwd=cwd)
        self.sessions[session_id] = process
        return process

    async def read_output(self, session_id: str) -> Optional[str]:
        """Non-blocking read from PTY"""
        process = self.sessions.get(session_id)
        if not process:
            return None
        try:
            data = process.read(1024)
            return data.decode('utf-8', errors='replace')
        except EOFError:
            return None

    async def write_input(self, session_id: str, data: str):
        """Write to PTY stdin"""
        process = self.sessions.get(session_id)
        if process:
            process.write(data.encode('utf-8'))

    def terminate_session(self, session_id: str):
        """Kill PTY process"""
        process = self.sessions.pop(session_id, None)
        if process:
            process.terminate()
```

**File:** `backend/src/content_gen_backend/routers/terminal.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from ..services.terminal_service import TerminalService
from ..models.terminal_models import CreateSessionRequest, CreateSessionResponse
import uuid
import asyncio

router = APIRouter(prefix="/api/v1/terminal", tags=["terminal"])
terminal_service = TerminalService()

@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    session_id = str(uuid.uuid4())
    await terminal_service.create_session(
        session_id=session_id,
        shell=request.shell or "/bin/bash",
        cwd=request.cwd or "."
    )
    return CreateSessionResponse(
        session_id=session_id,
        websocket_url=f"/ws/terminal/{session_id}",
        status="active"
    )

@router.websocket("/ws/{session_id}")
async def websocket_terminal(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Send connection confirmation
    await websocket.send_json({"type": "status", "status": "connected", "session_id": session_id})

    async def read_from_pty():
        """Background task: Read PTY output → send to WebSocket"""
        while True:
            output = await terminal_service.read_output(session_id)
            if output:
                await websocket.send_json({
                    "type": "output",
                    "data": output,
                    "session_id": session_id
                })
            await asyncio.sleep(0.01)  # Small delay to prevent busy loop

    # Start background reader
    reader_task = asyncio.create_task(read_from_pty())

    try:
        while True:
            # Receive input from WebSocket
            message = await websocket.receive_json()
            if message["type"] == "input":
                await terminal_service.write_input(session_id, message["data"])
    except WebSocketDisconnect:
        reader_task.cancel()
        terminal_service.terminate_session(session_id)

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    terminal_service.terminate_session(session_id)
    return {"session_id": session_id, "status": "terminated"}
```

### 4.4 Integration into Main App

**File:** `backend/src/content_gen_backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import videos, terminal  # Add terminal import

app = FastAPI(title="Content Gen Backend")

# Update CORS for WebSocket
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3333", "http://localhost:3334"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(videos.router)
app.include_router(terminal.router)  # NEW
```

---

## 5. Frontend Implementation

### 5.1 New Frontend Components

**File:** `frontend/src/composables/useTerminalSession.ts`

```typescript
import { ref, onMounted, onUnmounted } from 'vue'

export interface TerminalMessage {
  type: 'output' | 'input' | 'status'
  data?: string
  status?: string
  message?: string
  timestamp: string
}

export function useTerminalSession(backendUrl: string = 'http://localhost:4444') {
  const messages = ref<TerminalMessage[]>([])
  const connected = ref(false)
  const sessionId = ref<string | null>(null)
  let ws: WebSocket | null = null

  const createSession = async () => {
    const response = await fetch(`${backendUrl}/api/v1/terminal/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cwd: '/Users/chris/big-3-super-agent/apps/content-gen'
      })
    })
    const data = await response.json()
    sessionId.value = data.session_id
    return data
  }

  const connect = async () => {
    const session = await createSession()
    const wsUrl = `ws://localhost:4444${session.websocket_url}`

    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      connected.value = true
    }

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      messages.value.push(message)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      connected.value = false
    }

    ws.onclose = () => {
      connected.value = false
    }
  }

  const sendInput = (command: string) => {
    if (ws && connected.value) {
      ws.send(JSON.stringify({
        type: 'input',
        data: command,
        session_id: sessionId.value
      }))
    }
  }

  const disconnect = () => {
    if (ws) {
      ws.close()
      ws = null
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    messages,
    connected,
    sessionId,
    connect,
    sendInput,
    disconnect
  }
}
```

**File:** `frontend/src/components/terminal/TerminalOutput.vue`

```vue
<template>
  <div class="terminal-output">
    <div
      v-for="(msg, index) in messages"
      :key="index"
      :class="['message', `message-${msg.type}`]"
    >
      <span v-if="msg.type === 'output'" class="output-text">{{ msg.data }}</span>
      <span v-else-if="msg.type === 'input'" class="input-text">$ {{ msg.data }}</span>
      <span v-else-if="msg.type === 'status'" class="status-text">
        [{{ msg.status }}] {{ msg.message }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import type { TerminalMessage } from '@/composables/useTerminalSession'

defineProps<{
  messages: TerminalMessage[]
}>()
</script>

<style scoped>
.terminal-output {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  height: 500px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.message {
  margin-bottom: 4px;
}

.output-text {
  color: #d4d4d4;
}

.input-text {
  color: #4ec9b0;
  font-weight: bold;
}

.status-text {
  color: #808080;
  font-style: italic;
}
</style>
```

**File:** `frontend/src/components/terminal/TerminalInput.vue`

```vue
<template>
  <div class="terminal-input">
    <span class="prompt">$</span>
    <input
      v-model="currentInput"
      @keyup.enter="handleSubmit"
      :disabled="!connected"
      placeholder="Type command..."
      class="input-field"
    />
    <button @click="handleSubmit" :disabled="!connected" class="send-btn">
      Send
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue'

defineProps<{
  connected: boolean
}>()

const emit = defineEmits<{
  submit: [command: string]
}>()

const currentInput = ref('')

const handleSubmit = () => {
  if (currentInput.value.trim()) {
    emit('submit', currentInput.value + '\n')
    currentInput.value = ''
  }
}
</script>

<style scoped>
.terminal-input {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #252526;
  border-top: 1px solid #3e3e42;
}

.prompt {
  color: #4ec9b0;
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-weight: bold;
}

.input-field {
  flex: 1;
  background: #3c3c3c;
  border: 1px solid #555;
  color: #d4d4d4;
  padding: 8px;
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 14px;
}

.input-field:focus {
  outline: none;
  border-color: #007acc;
}

.send-btn {
  background: #007acc;
  color: white;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 4px;
}

.send-btn:disabled {
  background: #555;
  cursor: not-allowed;
}
</style>
```

**File:** `frontend/src/views/TerminalAssistant.vue`

```vue
<template>
  <div class="terminal-assistant">
    <header class="header">
      <h1>Terminal Assistant UI</h1>
      <div class="status">
        <span :class="['status-indicator', { connected }]"></span>
        {{ connected ? 'Connected' : 'Disconnected' }}
        <button v-if="!connected" @click="connect" class="connect-btn">
          Connect
        </button>
        <button v-else @click="disconnect" class="disconnect-btn">
          Disconnect
        </button>
      </div>
    </header>

    <TerminalOutput :messages="messages" />
    <TerminalInput :connected="connected" @submit="sendInput" />
  </div>
</template>

<script setup lang="ts">
import TerminalOutput from '@/components/terminal/TerminalOutput.vue'
import TerminalInput from '@/components/terminal/TerminalInput.vue'
import { useTerminalSession } from '@/composables/useTerminalSession'

const {
  messages,
  connected,
  connect,
  sendInput,
  disconnect
} = useTerminalSession()
</script>

<style scoped>
.terminal-assistant {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1e1e1e;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
}

.header h1 {
  color: #d4d4d4;
  font-size: 20px;
  margin: 0;
}

.status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #d4d4d4;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #f44336;
}

.status-indicator.connected {
  background: #4caf50;
}

.connect-btn, .disconnect-btn {
  margin-left: 12px;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.connect-btn {
  background: #4caf50;
  color: white;
}

.disconnect-btn {
  background: #f44336;
  color: white;
}
</style>
```

### 5.2 Router Integration

**File:** `frontend/src/router/index.ts` (create if doesn't exist)

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import VideoGeneration from '@/views/VideoGeneration.vue'
import TerminalAssistant from '@/views/TerminalAssistant.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/videos'
    },
    {
      path: '/videos',
      name: 'videos',
      component: VideoGeneration
    },
    {
      path: '/terminal',
      name: 'terminal',
      component: TerminalAssistant
    }
  ]
})

export default router
```

**Update:** `frontend/src/main.ts`

```typescript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')
```

### 5.3 Navigation Menu

**Update:** `frontend/src/App.vue`

```vue
<template>
  <div id="app">
    <nav class="main-nav">
      <router-link to="/videos">Video Generation</router-link>
      <router-link to="/terminal">Terminal Assistant</router-link>
    </nav>
    <router-view />
  </div>
</template>

<style>
.main-nav {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #2d2d30;
  border-bottom: 1px solid #3e3e42;
}

.main-nav a {
  color: #d4d4d4;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
}

.main-nav a.router-link-active {
  background: #007acc;
  color: white;
}
</style>
```

---

## 6. Dependencies

### 6.1 Backend Dependencies

**Add to:** `backend/pyproject.toml`

```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.30.0",
    "websockets>=12.0",
    "ptyprocess>=0.7.0",  # NEW: PTY management
    "pydantic>=2.5.0",
]
```

### 6.2 Frontend Dependencies

**Add to:** `frontend/package.json`

```json
{
  "dependencies": {
    "vue": "^3.5.22",
    "vue-router": "^4.5.0"  // NEW: For routing
  }
}
```

Install:
```bash
cd frontend
npm install vue-router
```

---

## 7. Implementation Steps

### Phase 1: Backend Foundation
1. **Install backend dependencies**
   ```bash
   cd /Users/chris/big-3-super-agent/apps/content-gen/backend
   uv pip install ptyprocess websockets
   ```

2. **Create terminal models**
   - File: `backend/src/content_gen_backend/models/terminal_models.py`
   - Define Pydantic schemas for requests/responses

3. **Implement TerminalService**
   - File: `backend/src/content_gen_backend/services/terminal_service.py`
   - PTY spawning, I/O handling, session management

4. **Create terminal router**
   - File: `backend/src/content_gen_backend/routers/terminal.py`
   - WebSocket endpoint, REST endpoints

5. **Update main.py**
   - Import and register terminal router
   - Verify CORS includes WebSocket origins

6. **Test backend**
   ```bash
   cd backend
   uv run dev
   # Use wscat or Postman to test WebSocket
   ```

### Phase 2: Frontend Development
1. **Install frontend dependencies**
   ```bash
   cd /Users/chris/big-3-super-agent/apps/content-gen/frontend
   npm install vue-router
   ```

2. **Create TypeScript types**
   - File: `frontend/src/types/terminal.ts`
   - Define message interfaces

3. **Implement useTerminalSession composable**
   - File: `frontend/src/composables/useTerminalSession.ts`
   - WebSocket connection, message handling

4. **Build terminal components**
   - `TerminalOutput.vue`
   - `TerminalInput.vue`

5. **Create TerminalAssistant view**
   - File: `frontend/src/views/TerminalAssistant.vue`
   - Compose components

6. **Setup routing**
   - Create `router/index.ts`
   - Update `main.ts`
   - Update `App.vue` with navigation

7. **Test frontend**
   ```bash
   cd frontend
   npm run dev -- --port 3333
   # Open http://localhost:3333/terminal
   ```

### Phase 3: Integration & Testing
1. **End-to-end testing**
   - Start backend: `cd backend && uv run dev`
   - Start frontend: `cd frontend && npm run dev -- --port 3333`
   - Navigate to http://localhost:3333/terminal
   - Test command execution (e.g., `ls`, `pwd`, `echo "hello"`)

2. **Error handling**
   - Test session timeout
   - Test WebSocket reconnection
   - Test invalid commands

3. **Performance optimization**
   - Buffer output for high-volume streams
   - Implement message throttling if needed

### Phase 4: Documentation & Deployment
1. **Update README.md**
   - Document terminal UI feature
   - Add usage examples

2. **Update start.sh** (if needed)
   - Ensure both services start correctly

3. **Add environment variables** (if credentials needed)
   - Update `.env.sample` in backend

---

## 8. Security Considerations

### 8.1 Command Injection Prevention
- **Risk:** User input directly executed in shell
- **Mitigation:**
  - Run terminal in sandboxed environment
  - Implement command whitelist for production
  - Use restricted shell (rbash) if public-facing

### 8.2 Authentication & Authorization
- **Current State:** No auth in existing app
- **Recommendation:** Add authentication before production
  - JWT tokens
  - Session-based auth
  - Role-based access control

### 8.3 WebSocket Security
- **Implement:**
  - Origin validation
  - Rate limiting
  - Session timeout (30 min idle)

---

## 9. Alternative Approaches

### 9.1 Capture Existing Terminal Session
Instead of spawning new PTY, capture the terminal where the assistant runs:

**Pros:**
- Shows actual assistant responses
- No separate session management

**Cons:**
- More complex (requires tty intercept)
- Platform-specific (script, tmux, etc.)

**Implementation:**
Use `script` command or `tmux` with pipe:
```bash
script -q /dev/null | tee >(websocket_sender)
```

### 9.2 Log File Tailing
Stream assistant logs to browser:

**Pros:**
- Simpler (no PTY)
- Read-only (safer)

**Cons:**
- No input capability
- Requires structured logging

---

## 10. Success Criteria

### Functional Requirements
- [ ] WebSocket connection established within 2 seconds
- [ ] Terminal output streams in real-time (<100ms latency)
- [ ] User input executed correctly in spawned shell
- [ ] Multiple concurrent sessions supported
- [ ] Graceful disconnect/reconnect handling

### Non-Functional Requirements
- [ ] Handles 10+ concurrent sessions
- [ ] No memory leaks over 1-hour session
- [ ] Responsive UI (60fps scrolling)
- [ ] Works in Chrome, Firefox, Safari

---

## 11. Future Enhancements

1. **Session Persistence**
   - Save session history to database
   - Resume disconnected sessions

2. **Collaborative Terminals**
   - Multiple users viewing same session
   - Screen sharing functionality

3. **Advanced Terminal Features**
   - ANSI color support
   - Terminal size negotiation (resize)
   - Copy/paste support

4. **AI Integration**
   - Parse assistant responses
   - Syntax highlighting for code blocks
   - Smart autocomplete

---

## 12. Open Questions & Decisions Needed

**NOTE:** The following decisions should be made before implementation:

1. **Deployment Model:** Integrated frontend (OPTION A) or separate app (OPTION B)?
   - **Recommendation:** OPTION A for MVP

2. **Authentication:** Required for MVP or defer to v2?
   - **Recommendation:** Defer if internal tool, add if public

3. **Terminal Capture:** Spawn new shell or capture existing assistant terminal?
   - **Recommendation:** Spawn new shell for MVP (simpler)

4. **Session Storage:** In-memory or persistent (Redis/DB)?
   - **Recommendation:** In-memory for MVP

5. **UI Framework:** Plain CSS or integrate UI library (Tailwind, Vuetify)?
   - **Recommendation:** Plain CSS for MVP (matches existing style)

---

## 13. References

- [FastAPI WebSockets Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [ptyprocess Python Library](https://ptyprocess.readthedocs.io/)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [WebSocket API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

---

**End of Technical Specification**
