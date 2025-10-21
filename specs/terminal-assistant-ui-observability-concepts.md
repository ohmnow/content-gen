# Terminal Assistant UI: Visual Feedback & Observability Design Concepts

**Version:** 1.0
**Created:** 2025-10-21
**Purpose:** Explore enhanced UI designs that provide deep observability into AI assistant activity beyond basic terminal output

---

## Executive Summary

This document explores advanced UI/UX concepts for surfacing AI assistant activity through rich visual feedback, real-time metrics, and multi-dimensional observability. The goal is to transform a basic terminal interface into a comprehensive development and debugging environment that provides users with deep insight into what the assistant is thinking, doing, and planning.

---

## Table of Contents

1. [Core Observability Events](#1-core-observability-events)
2. [Visual Component Concepts](#2-visual-component-concepts)
3. [Dashboard Layouts](#3-dashboard-layouts)
4. [Real-Time Metrics & Graphs](#4-real-time-metrics--graphs)
5. [Activity Timeline](#5-activity-timeline)
6. [Cognitive State Visualization](#6-cognitive-state-visualization)
7. [File System Activity Monitor](#7-file-system-activity-monitor)
8. [Token Usage & Cost Tracking](#8-token-usage--cost-tracking)
9. [Tool Usage Analytics](#9-tool-usage-analytics)
10. [Error & Warning System](#10-error--warning-system)
11. [Session Replay & History](#11-session-replay--history)
12. [Advanced Interaction Patterns](#12-advanced-interaction-patterns)
13. [Implementation Priorities](#13-implementation-priorities)

---

## 1. Core Observability Events

### 1.1 Event Taxonomy

Define a comprehensive set of events that the assistant emits during operation:

```typescript
// Event Categories
enum ObservabilityEventType {
  // Cognitive Events
  THINKING_START = 'thinking_start',
  THINKING_END = 'thinking_end',
  PLAN_CREATED = 'plan_created',
  PLAN_UPDATED = 'plan_updated',
  DECISION_MADE = 'decision_made',

  // Tool Events
  TOOL_INVOCATION_START = 'tool_invocation_start',
  TOOL_INVOCATION_END = 'tool_invocation_end',
  TOOL_ERROR = 'tool_error',

  // File Events
  FILE_READ = 'file_read',
  FILE_WRITTEN = 'file_written',
  FILE_EDITED = 'file_edited',
  FILE_DELETED = 'file_deleted',

  // Communication Events
  USER_MESSAGE = 'user_message',
  ASSISTANT_MESSAGE = 'assistant_message',
  CLARIFICATION_NEEDED = 'clarification_needed',

  // Task Events
  TASK_STARTED = 'task_started',
  TASK_COMPLETED = 'task_completed',
  TASK_FAILED = 'task_failed',
  SUBTASK_CREATED = 'subtask_created',

  // Resource Events
  TOKEN_USAGE = 'token_usage',
  API_CALL = 'api_call',
  RATE_LIMIT_HIT = 'rate_limit_hit',

  // System Events
  SESSION_START = 'session_start',
  SESSION_END = 'session_end',
  ERROR = 'error',
  WARNING = 'warning',
}

interface ObservabilityEvent {
  id: string
  type: ObservabilityEventType
  timestamp: string
  duration_ms?: number
  metadata: Record<string, any>
  context?: {
    task_id?: string
    tool_name?: string
    file_path?: string
    error_message?: string
  }
}
```

### 1.2 Event Stream Architecture

```
┌─────────────────┐
│  Claude Agent   │
│   (Terminal)    │
└────────┬────────┘
         │ emits events
         ▼
┌─────────────────┐
│ Event Collector │ ◄──── Captures all observable events
│   (Backend)     │
└────────┬────────┘
         │ streams via WebSocket
         ▼
┌─────────────────┐
│  Event Store    │ ◄──── In-memory + persistent storage
│  (Redis/Memory) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Frontend UI   │ ◄──── Renders visualizations
│  (Vue 3 + D3)   │
└─────────────────┘
```

---

## 2. Visual Component Concepts

### 2.1 Status Indicator Suite

**Multi-State Indicator**
```
┌─────────────────────────────────┐
│ Assistant Status                │
├─────────────────────────────────┤
│ ● Idle                          │  ← Gray pulse
│ ● Thinking                      │  ← Yellow pulse
│ ● Executing Tool                │  ← Blue pulse
│ ● Writing Code                  │  ← Green pulse
│ ● Waiting for Approval          │  ← Orange pulse
│ ● Error State                   │  ← Red pulse
└─────────────────────────────────┘
```

**Progress Indicators**
- **Linear Progress Bar:** For file operations with known size
- **Indeterminate Spinner:** For open-ended operations (thinking, API calls)
- **Step Progress:** Visual stepper showing current phase in multi-step plan
- **Ring Progress:** Circular progress for token budget (fills as tokens consumed)

**Visual Metaphors:**
- Brain icon pulsing = thinking/planning
- Gear icon spinning = executing operation
- Checkmark animation = task completed
- Red X with shake = error occurred

### 2.2 Activity Feed

Real-time scrolling feed of assistant actions:

```
┌─────────────────────────────────────────────┐
│ Activity Feed                         [•••] │
├─────────────────────────────────────────────┤
│ 12:34:56  📖 Read file: src/main.ts         │
│ 12:34:57  🧠 Analyzing code structure       │
│ 12:34:59  ✏️  Edited: src/main.ts (L45-52) │
│ 12:35:01  🔧 Ran command: npm test          │
│ 12:35:03  ✅ Task completed: Fix bug #123   │
│ 12:35:05  📝 Wrote: spec/new-feature.md     │
└─────────────────────────────────────────────┘
```

**Features:**
- Color-coded by event type
- Icon-based visual classification
- Click to expand for detailed metadata
- Filter by event type
- Search/grep within activity log
- Export as JSON/CSV

### 2.3 File System Heat Map

Visual representation of which files the assistant is interacting with:

```
┌─────────────────────────────────────────────┐
│ File System Activity              🔥 Hot    │
├─────────────────────────────────────────────┤
│ src/                                        │
│   ├─ main.ts         ████████░ (8 edits)   │
│   ├─ config.ts       ██░░░░░░░ (2 reads)   │
│   └─ utils.ts        ████░░░░░ (4 edits)   │
│ tests/                                      │
│   └─ main.test.ts    ██████░░░ (6 reads)   │
│ package.json         █░░░░░░░░ (1 read)    │
└─────────────────────────────────────────────┘
```

**Visual Encoding:**
- Heat map intensity = frequency of access
- Color gradient: Blue (read) → Green (edit) → Red (high activity)
- File size indicator (bubble size if using tree map)
- Hover for detailed stats (# reads, # writes, last accessed)

### 2.4 Cognitive Process Visualizer

Show the assistant's "thought process" as a flowchart:

```
┌─────────────────────────────────────────────┐
│ Current Thought Process                     │
├─────────────────────────────────────────────┤
│                                             │
│   [User Request]                            │
│         │                                   │
│         ▼                                   │
│   [Analyze Codebase]  ◄── Currently here   │
│         │                                   │
│         ├─► [Read main.ts]                  │
│         ├─► [Read config.ts]                │
│         └─► [Grep for patterns]             │
│         │                                   │
│         ▼                                   │
│   [Generate Plan]                           │
│         │                                   │
│         ▼                                   │
│   [Execute Changes]                         │
│         │                                   │
│         ▼                                   │
│   [Verify & Report]                         │
│                                             │
└─────────────────────────────────────────────┘
```

**Implementation Ideas:**
- Animated flowchart that builds as assistant progresses
- Highlight current node with pulsing border
- Branch visualization for conditional logic
- Collapse/expand subtrees for complex workflows

---

## 3. Dashboard Layouts

### 3.1 Split-Panel Layout (Recommended for MVP)

```
┌──────────────────────────────────────────────────────────────┐
│ Header: Session Info | Status | Token Usage | Time         │
├─────────────────────┬────────────────────────────────────────┤
│                     │                                        │
│  Left Panel (40%)   │    Center Panel (40%)                  │
│                     │                                        │
│  ┌───────────────┐  │    ┌────────────────────────────┐     │
│  │ Activity Feed │  │    │   Terminal Output          │     │
│  │               │  │    │   (Traditional View)       │     │
│  │ • File read   │  │    │                            │     │
│  │ • Thinking... │  │    │   $ npm test               │     │
│  │ • Tool call   │  │    │   > Running tests...       │     │
│  │ • Edit made   │  │    │   ✓ All tests passed       │     │
│  └───────────────┘  │    └────────────────────────────┘     │
│                     │                                        │
│  ┌───────────────┐  │    ┌────────────────────────────┐     │
│  │ Current Tasks │  │    │   User Input Field         │     │
│  │ [✓] Read code │  │    └────────────────────────────┘     │
│  │ [→] Analyze   │  │                                        │
│  │ [ ] Generate  │  │                                        │
│  └───────────────┘  │                                        │
│                     │                                        │
├─────────────────────┴────────────────────────────────────────┤
│  Right Sidebar (20%): File Changes, Metrics, Status          │
│                                                              │
│  ┌─────────────────────────┐                                │
│  │ Files Modified (3)      │                                │
│  │  • src/main.ts +12/-5   │                                │
│  │  • tests/app.test.ts +8 │                                │
│  └─────────────────────────┘                                │
│                                                              │
│  ┌─────────────────────────┐                                │
│  │ Token Usage             │                                │
│  │  ████████░░░░ 65%       │                                │
│  │  13K / 20K tokens       │                                │
│  └─────────────────────────┘                                │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Tab-Based Layout (For Advanced Users)

Multiple tabs for different views:

```
┌──────────────────────────────────────────────────────────────┐
│ [Terminal] [Activity] [Files] [Metrics] [Timeline] [Logs]   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Tab Content Area (context switches based on selection)     │
│                                                              │
│  - Terminal: Traditional shell output                       │
│  - Activity: Detailed event stream with filters             │
│  - Files: Diff viewer for all file changes                  │
│  - Metrics: Graphs and charts for performance               │
│  - Timeline: Gantt-style view of task execution             │
│  - Logs: Structured logs with severity filtering            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3.3 Inspector Mode (DevTools-Inspired)

Inspired by browser DevTools:

```
┌──────────────────────────────────────────────────────────────┐
│ Main Interaction Area (Terminal + Chat)                     │
│                                                              │
│  User: "Add error handling to the API"                      │
│  Assistant: I'll analyze the API and add proper error       │
│  handling. Let me start by reading the current code...      │
│                                                              │
├══════════════════════════════════════════════════════════════┤
│ ▼ Inspector Panel (Collapsible, Bottom Drawer)              │
├──────────────────────────────────────────────────────────────┤
│ [Events] [Network] [Performance] [Console] [Sources]        │
├──────────────────────────────────────────────────────────────┤
│ Events Tab:                                                  │
│  Timestamp    | Type          | Tool       | Duration       │
│  12:34:56.123 | file_read     | Read       | 45ms          │
│  12:34:56.890 | tool_call     | Grep       | 120ms         │
│  12:34:58.012 | file_edited   | Edit       | 230ms         │
│  12:34:59.456 | thinking      | -          | 1.2s          │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Real-Time Metrics & Graphs

### 4.1 Token Usage Visualization

**Circular Gauge (Primary Display)**
```
        ┌────────────┐
        │   Tokens   │
        │    65%     │
        │            │
        │   13,042   │
        │  / 20,000  │
        └────────────┘
```

**Token Flow Chart (Historical View)**
```
Tokens
  │
20k├                                              ╱ Spike
  │                                          ╱╲╱
15k├                                     ╱───
  │                               ╱─────╯
10k├                         ╱────╯
  │                   ╱─────╯
 5k├             ╱────╯
  │      ╱──────╯
  └────┴────┴────┴────┴────┴────┴────┴────┴────┴──► Time
      0    5   10   15   20   25   30   35   40  (min)
```

**Features:**
- Color zones: Green (0-60%), Yellow (60-80%), Red (80-100%)
- Projection line showing estimated completion time
- Breakdown by tool type (Read: 3K, Edit: 5K, Think: 5K)
- Cost estimate if API is paid

### 4.2 Tool Usage Distribution

**Pie Chart**
```
        Tool Invocations (Last Hour)

            Read: 45%
           ╱──────╲
        Edit: 30%  │
       ╱────────────┤
      │     Grep: 15%
      │    ╱─────────
       ╲──╯ Bash: 10%
```

**Bar Chart (Frequency Over Time)**
```
Tool Calls/min
  │
30├     █
  │     █
25├     █
  │     █
20├     █     █
  │     █     █
15├ █   █     █
  │ █   █ █   █
10├ █   █ █   █ █
  │ █ █ █ █ █ █ █
 5├ █ █ █ █ █ █ █
  │ █ █ █ █ █ █ █
  └─┴─┴─┴─┴─┴─┴─┴─► Time
   R E G B R E G B
   e d r a e d r a
   a i a s a i a s
   d t p h d t p h
```

### 4.3 Performance Metrics

**Latency Distribution Histogram**
```
Tool Call Latency (ms)
Frequency
  │
50├ █
  │ █
40├ █
  │ █ █
30├ █ █
  │ █ █ █
20├ █ █ █
  │ █ █ █ █
10├ █ █ █ █ █
  │ █ █ █ █ █ █
  └─┴─┴─┴─┴─┴─┴──► Duration
   0 50 100 150 200 250 300+ (ms)

Avg: 125ms | P95: 250ms | P99: 350ms
```

**Real-Time Throughput Gauge**
```
Operations/Second
┌──────────────────┐
│       ↗ 12       │  ← Current rate
│      /           │
│    /             │
│  /               │
│─────────────────►│
│  Avg: 8 ops/s    │
└──────────────────┘
```

---

## 5. Activity Timeline

### 5.1 Gantt-Style Timeline

Horizontal timeline showing task execution with overlaps and dependencies:

```
┌─────────────────────────────────────────────────────────────┐
│ Task Timeline                                   [Zoom: 1m]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Read codebase      ████░░░░░░░░░░░░░░░░░░░░░░░             │
│ Analyze structure  ░░░░████░░░░░░░░░░░░░░░░░░              │
│ Generate plan      ░░░░░░░░████░░░░░░░░░░░░░░              │
│ Edit files         ░░░░░░░░░░░░████████░░░░░░              │
│ Run tests          ░░░░░░░░░░░░░░░░░░░░████░░              │
│ Commit changes     ░░░░░░░░░░░░░░░░░░░░░░░░██              │
│                                                             │
│ └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴────►    │
│ 0s  10s 20s 30s 40s 50s 60s 70s 80s 90s 100s 110s 120s     │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Click on bar to see detailed event metadata
- Color-code by task type (read=blue, write=green, think=yellow)
- Show parallel operations side-by-side
- Hover to see duration and timing stats

### 5.2 Vertical Event Timeline (Scrollable)

Like GitHub commit history:

```
┌─────────────────────────────────────────────┐
│ Event Timeline                      Filter ▼│
├─────────────────────────────────────────────┤
│                                             │
│ ● 12:34:56 - Session started                │
│ │                                           │
│ ○ 12:34:58 - User message received          │
│ │  "Add error handling to API"             │
│ │                                           │
│ ○ 12:35:01 - Thinking (2.3s)                │
│ │  [Expand to see internal reasoning]      │
│ │                                           │
│ ●─12:35:03 - Plan created                   │
│ │  • Read src/api.ts                       │
│ │  • Analyze error patterns                │
│ │  • Add try-catch blocks                  │
│ │                                           │
│ ○ 12:35:05 - File read: src/api.ts          │
│ │  [View file contents]                    │
│ │                                           │
│ ○ 12:35:08 - File edited: src/api.ts        │
│ │  +15 lines, -3 lines [View diff]         │
│ │                                           │
│ ○ 12:35:10 - Tool: Bash (npm test)          │
│ │  Exit code: 0 [View output]              │
│ │                                           │
│ ● 12:35:15 - Task completed ✓               │
│                                             │
└─────────────────────────────────────────────┘
```

**Features:**
- Infinite scroll with virtualization for performance
- Expand/collapse events to see metadata
- Jump to specific timestamp
- Bookmark important events
- Export timeline as JSON/CSV

---

## 6. Cognitive State Visualization

### 6.1 "Brain Activity" Monitor

Visual representation of what the assistant is currently "thinking about":

```
┌─────────────────────────────────────────────┐
│ Cognitive Activity                          │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────┐           │
│  │  Current Focus Area          │           │
│  │                              │           │
│  │  [Analyzing code structure]  │  ← Large  │
│  │                              │           │
│  └──────────────────────────────┘           │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Error   │  │ Test     │  │ Imports  │  │
│  │ Handling │  │ Coverage │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│     ↑ Related sub-thoughts                  │
│                                             │
└─────────────────────────────────────────────┘
```

**Features:**
- Bubble size = cognitive "weight" (time spent thinking)
- Bubble color = type of thought (analysis=blue, planning=yellow, execution=green)
- Animation: bubbles pulse, grow, shrink based on activity
- Connections show thought relationships

### 6.2 Decision Tree Viewer

Show the decision-making process:

```
┌─────────────────────────────────────────────┐
│ Decision Tree: "Should I run tests?"        │
├─────────────────────────────────────────────┤
│                                             │
│   Check if tests exist                      │
│         │                                   │
│    ┌────┴────┐                              │
│    ↓         ↓                              │
│  Yes ✓     No ✗                             │
│    │         └──► Skip testing              │
│    │                                        │
│    ↓                                        │
│   Check if code changed                     │
│         │                                   │
│    ┌────┴────┐                              │
│    ↓         ↓                              │
│  Yes ✓     No ✗                             │
│    │         └──► Skip testing              │
│    │                                        │
│    ↓                                        │
│   Run tests ✓  ← Decision made              │
│                                             │
└─────────────────────────────────────────────┘
```

### 6.3 Confidence Meter

Show assistant's confidence in current action:

```
┌─────────────────────────────────────────────┐
│ Confidence in Current Action                │
├─────────────────────────────────────────────┤
│                                             │
│  Action: "Edit src/api.ts to add error      │
│           handling"                         │
│                                             │
│  Confidence: ████████░░ 85%                 │
│                                             │
│  Factors:                                   │
│  + Similar patterns found      (+20%)       │
│  + Tests exist to verify       (+15%)       │
│  - Large file (complexity)     (-10%)       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 7. File System Activity Monitor

### 7.1 Diff Viewer Panel

Real-time diff viewer showing file changes as they happen:

```
┌─────────────────────────────────────────────┐
│ Live Diff: src/api.ts                  [×] │
├─────────────────────────────────────────────┤
│  42 │ export async function fetchData() {   │
│  43 │-  const response = await fetch(url)   │
│  44 │+  try {                               │
│  45 │+    const response = await fetch(url) │
│  46 │+    if (!response.ok) {               │
│  47 │+      throw new Error('API failed')   │
│  48 │+    }                                 │
│  49 │+    return await response.json()      │
│  50 │+  } catch (error) {                   │
│  51 │+    console.error(error)              │
│  52 │+    throw error                       │
│  53 │+  }                                   │
│  54 │ }                                     │
│     │                                       │
│     └─► [Approve] [Reject] [Ask Question]  │
└─────────────────────────────────────────────┘
```

**Features:**
- Side-by-side or unified diff view
- Syntax highlighting
- Line-by-line annotations (why this change was made)
- Approve/reject individual hunks
- Comment on specific lines

### 7.2 File Change Summary

Aggregate view of all modifications:

```
┌─────────────────────────────────────────────┐
│ Files Changed (5)               [View All] │
├─────────────────────────────────────────────┤
│                                             │
│ ✏️  src/api.ts              +23  -5         │
│     • Added error handling                  │
│     • Improved type safety                  │
│                                             │
│ ✏️  src/types.ts             +8  -0         │
│     • Added ErrorResponse type              │
│                                             │
│ 📄 tests/api.test.ts        +45  -2         │
│     • Added error test cases                │
│                                             │
│ 📄 README.md                 +3  -1         │
│     • Updated error handling docs           │
│                                             │
│ 🗑️  src/old-api.ts          DELETED         │
│                                             │
│ Total: +79 lines, -8 lines                  │
└─────────────────────────────────────────────┘
```

### 7.3 Directory Tree with Activity Indicators

```
┌─────────────────────────────────────────────┐
│ Project Files                        🔍 □ │
├─────────────────────────────────────────────┤
│                                             │
│ 📁 src/                           🔥🔥🔥     │
│   ├─ 📄 main.ts                   🔥        │
│   ├─ 📝 api.ts                    🔥🔥🔥     │
│   ├─ 📄 types.ts                  🔥        │
│   └─ 📁 utils/                              │
│       └─ 📄 helpers.ts                      │
│                                             │
│ 📁 tests/                         🔥🔥      │
│   └─ 📄 api.test.ts               🔥🔥      │
│                                             │
│ 📄 package.json                             │
│ 📄 tsconfig.json                            │
│ 📄 README.md                      🔥        │
│                                             │
│ Legend: 🔥 = Activity level                 │
└─────────────────────────────────────────────┘
```

---

## 8. Token Usage & Cost Tracking

### 8.1 Token Budget Dashboard

```
┌─────────────────────────────────────────────┐
│ Token Budget & Cost Tracking                │
├─────────────────────────────────────────────┤
│                                             │
│ Session Tokens: 13,042 / 20,000 (65%)      │
│ ████████████░░░░░░░░                        │
│                                             │
│ Breakdown:                                  │
│  Input tokens:     8,520  ($0.085)         │
│  Output tokens:    4,522  ($0.136)         │
│  Total cost:       $0.22                    │
│                                             │
│ By Tool:                                    │
│  Read    ████░░░░░░  3,200 tokens           │
│  Edit    ██████░░░░  5,100 tokens           │
│  Bash    ██░░░░░░░░  1,800 tokens           │
│  Think   ██░░░░░░░░  2,942 tokens           │
│                                             │
│ Estimated remaining budget:                 │
│  ~45 more operations at current rate        │
│                                             │
└─────────────────────────────────────────────┘
```

### 8.2 Cost Projection Graph

```
┌─────────────────────────────────────────────┐
│ Projected Cost Over Time                    │
├─────────────────────────────────────────────┤
│                                             │
│ Cost ($)                                    │
│   │                                   ╱     │
│ 1 ├                              ╱────      │
│   │                         ╱────            │
│0.5├                    ╱────                 │
│   │               ╱────                      │
│   │          ╱────  ← Current: $0.22         │
│   └─────┴────┴────┴────┴────┴────┴───►      │
│        0   10   20   30   40   50   60 (min)│
│                                             │
│  Projected total: $0.85 (if session contin.)│
└─────────────────────────────────────────────┘
```

### 8.3 Token Efficiency Metrics

```
┌─────────────────────────────────────────────┐
│ Efficiency Metrics                          │
├─────────────────────────────────────────────┤
│                                             │
│ Tokens per Task:          450 avg           │
│ Tokens per File Edit:     820 avg           │
│ Tokens per Tool Call:     125 avg           │
│                                             │
│ Efficiency Score: ████████░░ 82/100         │
│  (Compared to similar sessions)             │
│                                             │
│ Optimization Suggestions:                   │
│  • Consider batch file reads                │
│  • Use Grep before Read for large files     │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 9. Tool Usage Analytics

### 9.1 Tool Invocation Heatmap

Calendar-style heatmap showing tool usage intensity:

```
┌─────────────────────────────────────────────┐
│ Tool Usage Heatmap (Last 7 Days)            │
├─────────────────────────────────────────────┤
│         Mon Tue Wed Thu Fri Sat Sun         │
│ Read    ██  ███ ███ ██  █   ░   ░           │
│ Edit    ██  ███ ██  ███ ██  ░   ░           │
│ Bash    █   ██  █   ██  █   ░   ░           │
│ Grep    ██  ██  ███ ██  █   ░   ░           │
│ Task    █   █   █   █   █   ░   ░           │
│                                             │
│ Intensity: ░ None  █ Low  ██ Med  ███ High  │
└─────────────────────────────────────────────┘
```

### 9.2 Tool Success Rate

```
┌─────────────────────────────────────────────┐
│ Tool Success Rates (Last 100 Invocations)   │
├─────────────────────────────────────────────┤
│                                             │
│ Read     ████████████████████ 98% (49/50)  │
│ Edit     ███████████████████░ 94% (47/50)  │
│ Bash     ████████████████░░░░ 86% (43/50)  │
│ Grep     ████████████████████ 100% (50/50) │
│                                             │
│ Common Failures:                            │
│  • Bash: Command not found (3x)             │
│  • Edit: Merge conflict (2x)                │
│                                             │
└─────────────────────────────────────────────┘
```

### 9.3 Tool Latency Comparison

```
┌─────────────────────────────────────────────┐
│ Average Tool Latency                        │
├─────────────────────────────────────────────┤
│                                             │
│ Grep     ▓░░░░░░░░░░  45ms                  │
│ Read     ▓▓▓░░░░░░░░ 125ms                  │
│ Bash     ▓▓▓▓▓░░░░░░ 340ms                  │
│ Edit     ▓▓▓▓▓▓░░░░░ 450ms                  │
│ Task     ▓▓▓▓▓▓▓▓▓░░ 2.3s                   │
│                                             │
│ ─────┴─────┴─────┴─────┴─────┴───►         │
│ 0    500ms  1s   1.5s  2s   2.5s            │
└─────────────────────────────────────────────┘
```

---

## 10. Error & Warning System

### 10.1 Error Feed with Severity Levels

```
┌─────────────────────────────────────────────┐
│ Errors & Warnings                   [Clear]│
├─────────────────────────────────────────────┤
│                                             │
│ 🔴 ERROR   12:35:45                         │
│    Tool 'Bash' failed: npm test             │
│    Exit code: 1                             │
│    [View full output] [Retry]               │
│                                             │
│ 🟡 WARNING 12:34:23                         │
│    File src/api.ts has no tests             │
│    Confidence: Low                          │
│    [Suggest fix]                            │
│                                             │
│ 🔵 INFO    12:33:01                         │
│    Token usage at 80% of budget             │
│    [View token breakdown]                   │
│                                             │
│ 🟢 SUCCESS 12:32:15                         │
│    All files edited successfully            │
│    [View changes]                           │
│                                             │
└─────────────────────────────────────────────┘
```

### 10.2 Error Context Panel

When error occurs, show detailed context:

```
┌─────────────────────────────────────────────┐
│ Error Details: Bash Command Failed          │
├─────────────────────────────────────────────┤
│                                             │
│ Command: npm test                           │
│ Exit Code: 1                                │
│ Duration: 3.2s                              │
│                                             │
│ [STDOUT]                                    │
│ Running tests...                            │
│ ✓ api.test.ts (2 passed)                    │
│ ✗ auth.test.ts (1 failed)                   │
│                                             │
│ [STDERR]                                    │
│ TypeError: Cannot read property 'token'     │
│   at line 45 in auth.test.ts               │
│                                             │
│ Context:                                    │
│  • Recent file changes: auth.ts (+12, -5)   │
│  • Last successful test: 2 min ago          │
│                                             │
│ [Suggest Fix] [Revert Changes] [Ignore]    │
└─────────────────────────────────────────────┘
```

### 10.3 Warning Aggregator

```
┌─────────────────────────────────────────────┐
│ Active Warnings (3)                         │
├─────────────────────────────────────────────┤
│                                             │
│ ⚠️  No tests for modified files (2)         │
│    • src/api.ts                             │
│    • src/types.ts                           │
│    [Generate tests]                         │
│                                             │
│ ⚠️  Token budget at 85%                     │
│    Estimated 5 operations remaining         │
│    [Optimize] [Extend budget]               │
│                                             │
│ ⚠️  Large file edited (1,200 lines)         │
│    Consider splitting into modules          │
│    [Suggest refactor]                       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 11. Session Replay & History

### 11.1 Session Recording

Record entire session for replay:

```
┌─────────────────────────────────────────────┐
│ Session History                             │
├─────────────────────────────────────────────┤
│                                             │
│ 📹 Current Session                          │
│    Started: 12:30:00 | Duration: 5m 32s    │
│    [●] Recording...                         │
│                                             │
│ 📼 Previous Sessions                        │
│                                             │
│ 📁 Oct 21, 2025 11:45 AM (15m)             │
│    "Fix authentication bug"                 │
│    [▶️ Replay] [📄 Export] [🗑️  Delete]     │
│                                             │
│ 📁 Oct 21, 2025 10:30 AM (22m)             │
│    "Add error handling to API"              │
│    [▶️ Replay] [📄 Export] [🗑️  Delete]     │
│                                             │
│ 📁 Oct 20, 2025 4:15 PM (8m)               │
│    "Refactor user service"                  │
│    [▶️ Replay] [📄 Export] [🗑️  Delete]     │
│                                             │
└─────────────────────────────────────────────┘
```

### 11.2 Replay Controls

```
┌─────────────────────────────────────────────┐
│ Replay: "Fix authentication bug"            │
├─────────────────────────────────────────────┤
│                                             │
│ [◀◀] [▶️] [▶▶] [⏸️]   Speed: 1x [▼]         │
│                                             │
│ ━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━         │
│ 5:23 / 15:00                                │
│                                             │
│ Current Event:                              │
│ 🧠 Analyzing auth.ts structure...           │
│                                             │
│ [Jump to Error] [Jump to End]               │
│                                             │
└─────────────────────────────────────────────┘
```

### 11.3 Session Comparison

Compare two sessions side-by-side:

```
┌──────────────────────┬──────────────────────┐
│ Session A (Oct 21)   │ Session B (Oct 20)   │
├──────────────────────┼──────────────────────┤
│ Duration: 15m        │ Duration: 22m        │
│ Tasks: 5             │ Tasks: 3             │
│ Files changed: 8     │ Files changed: 12    │
│ Token usage: 13K     │ Token usage: 18K     │
│ Errors: 1            │ Errors: 0            │
│                      │                      │
│ Tools Used:          │ Tools Used:          │
│  Read:  12x          │  Read:  18x          │
│  Edit:   8x          │  Edit:  15x          │
│  Bash:   3x          │  Bash:   5x          │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

---

## 12. Advanced Interaction Patterns

### 12.1 Hover Actions

Rich tooltips and hover interactions:

```
┌─────────────────────────────────────────────┐
│ Activity Feed                               │
├─────────────────────────────────────────────┤
│                                             │
│ 12:34:56  📖 Read file: src/main.ts         │
│            ↑ [Hover shows preview popup]    │
│           ┌────────────────────────────┐    │
│           │ src/main.ts                │    │
│           │ Size: 245 lines            │    │
│           │ Last modified: 2 min ago   │    │
│           │                            │    │
│           │ export function main() {   │    │
│           │   // ... (preview)         │    │
│           │ }                          │    │
│           │                            │    │
│           │ [View Full] [View Diff]    │    │
│           └────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

### 12.2 Contextual Actions

Right-click or action menu on events:

```
┌─────────────────────────────────────────────┐
│ 12:35:08  ✏️  Edited: src/api.ts             │
│           ┌───────────────────────┐          │
│           │ View full file        │          │
│           │ View diff             │          │
│           │ Revert this change    │          │
│           │ Copy file path        │          │
│           │ ──────────────────────│          │
│           │ Add comment           │          │
│           │ Bookmark this event   │          │
│           │ Share event link      │          │
│           └───────────────────────┘          │
└─────────────────────────────────────────────┘
```

### 12.3 Inline Annotations

Allow users to comment on specific events:

```
┌─────────────────────────────────────────────┐
│ 12:35:01  🧠 Thinking (2.3s)                 │
│           💬 User comment: "Why so long?"    │
│           ↳ 🤖 Assistant: "Large file,       │
│              needed to analyze 1,200 lines"  │
│                                             │
│           [Reply] [Resolve] [Delete]        │
└─────────────────────────────────────────────┘
```

### 12.4 Split-Screen Diff

View code changes side-by-side with terminal:

```
┌──────────────────────┬──────────────────────┐
│ Terminal Output      │ Live File Viewer     │
├──────────────────────┼──────────────────────┤
│                      │ src/api.ts           │
│ $ Editing api.ts...  │                      │
│                      │ 45 │ -const res =    │
│ ✓ Edit complete      │ 45 │ +try {          │
│                      │ 46 │ +  const res =  │
│ $ Running tests...   │ 47 │ +  if (!res.ok)│
│                      │ 48 │ +    throw new  │
│ ✓ Tests passed       │ 49 │ +} catch (err) │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

### 12.5 Voice Commands (Future)

Integration with voice input:

```
┌─────────────────────────────────────────────┐
│ Voice Control                      [🎤 OFF] │
├─────────────────────────────────────────────┤
│                                             │
│ Say commands like:                          │
│  • "Show me the errors"                     │
│  • "What files were changed?"               │
│  • "Replay the last 2 minutes"              │
│  • "Zoom in on the timeline"                │
│  • "Filter for file edits"                  │
│                                             │
│ [Enable Voice Control]                      │
└─────────────────────────────────────────────┘
```

---

## 13. Implementation Priorities

### Phase 1: MVP (Must-Have)

**Priority 1 (Week 1-2):**
1. **Basic Status Indicator**
   - Idle, Thinking, Executing, Error states
   - Simple color-coded dot with label

2. **Activity Feed**
   - Real-time scrolling list of events
   - Basic icons for event types
   - Click to expand details

3. **Token Usage Gauge**
   - Simple progress bar
   - Current/max display
   - Color zones (green/yellow/red)

4. **File Change List**
   - List of modified files
   - Line count changes (+/-)
   - Click to view diff

**Priority 2 (Week 3-4):**
5. **Event Timeline** (Vertical)
   - Chronological event list
   - Expandable event details
   - Basic filtering (by type)

6. **Error Panel**
   - List of errors/warnings
   - Severity indicators
   - Context and suggested actions

7. **Tool Usage Bar Chart**
   - Simple bar chart of tool frequency
   - Last hour view

### Phase 2: Enhanced Observability (Nice-to-Have)

**Priority 3 (Month 2):**
8. **Gantt Timeline**
   - Horizontal task timeline
   - Overlapping operations
   - Zoom controls

9. **File System Heat Map**
   - Visual tree with activity indicators
   - Color-coded intensity

10. **Token Flow Chart**
    - Historical token usage over time
    - Projection line

11. **Diff Viewer Panel**
    - Syntax-highlighted diffs
    - Side-by-side comparison

### Phase 3: Advanced Features (Future)

**Priority 4 (Month 3+):**
12. **Cognitive Process Visualizer**
    - Flowchart of thought process
    - Animated state transitions

13. **Session Replay**
    - Record and playback sessions
    - Speed controls
    - Jump to specific events

14. **Performance Metrics Dashboard**
    - Latency histograms
    - Throughput gauges
    - P95/P99 metrics

15. **Comparison Tools**
    - Session-to-session comparison
    - A/B testing different approaches

---

## 14. Technical Implementation Notes

### 14.1 Event Streaming Architecture

```typescript
// Backend: Event emission
class ObservabilityService {
  async emitEvent(event: ObservabilityEvent) {
    // Store in memory/Redis
    await this.eventStore.add(event)

    // Broadcast to all connected WebSocket clients
    await this.websocketService.broadcast({
      type: 'observability_event',
      data: event
    })
  }
}

// Frontend: Event consumption
const useObservability = () => {
  const events = ref<ObservabilityEvent[]>([])

  const ws = new WebSocket('ws://localhost:4444/ws/observability')

  ws.onmessage = (msg) => {
    const event = JSON.parse(msg.data)
    events.value.push(event)

    // Trigger UI updates
    updateActivityFeed(event)
    updateMetrics(event)
    updateTimeline(event)
  }

  return { events }
}
```

### 14.2 Data Visualization Libraries

**Recommended Stack:**
- **D3.js** - For custom charts and graphs
- **Chart.js** - For simple bar/line/pie charts
- **Vis.js** - For timeline and network graphs
- **React Flow / Vue Flow** - For flowcharts and cognitive graphs

**Example: Token Usage Gauge**
```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { arc } from 'd3-shape'

const tokensUsed = ref(13042)
const tokensMax = ref(20000)

const percentage = computed(() =>
  (tokensUsed.value / tokensMax.value) * 100
)

const gaugeColor = computed(() => {
  if (percentage.value < 60) return '#4caf50' // Green
  if (percentage.value < 80) return '#ff9800' // Yellow
  return '#f44336' // Red
})
</script>

<template>
  <div class="token-gauge">
    <svg width="200" height="200">
      <!-- Background arc -->
      <path :d="backgroundArc" fill="#e0e0e0" />
      <!-- Progress arc -->
      <path :d="progressArc" :fill="gaugeColor" />
      <!-- Center text -->
      <text x="100" y="100" text-anchor="middle">
        {{ percentage.toFixed(0) }}%
      </text>
    </svg>
  </div>
</template>
```

### 14.3 Performance Considerations

**Optimization Strategies:**
1. **Event Throttling**: Batch events every 100ms to avoid UI jank
2. **Virtual Scrolling**: Use `vue-virtual-scroller` for long activity feeds
3. **Data Windowing**: Only keep last N events in memory
4. **Lazy Loading**: Load historical data on-demand
5. **WebWorker Processing**: Offload heavy calculations (metrics aggregation)

**Example: Event Throttling**
```typescript
// Throttle event processing to every 100ms
const eventBuffer: ObservabilityEvent[] = []

const flushEventBuffer = throttle(() => {
  const batchedEvents = [...eventBuffer]
  eventBuffer.length = 0

  // Update UI with batched events
  updateUI(batchedEvents)
}, 100)

ws.onmessage = (msg) => {
  const event = JSON.parse(msg.data)
  eventBuffer.push(event)
  flushEventBuffer()
}
```

### 14.4 Accessibility Considerations

**WCAG 2.1 AA Compliance:**
- Use semantic HTML (`<section>`, `<article>`, `<nav>`)
- Provide ARIA labels for all interactive elements
- Ensure color contrast ratios meet 4.5:1 minimum
- Support keyboard navigation (Tab, Enter, Space, Arrows)
- Add screen reader announcements for important events

**Example: Accessible Status Indicator**
```vue
<div
  class="status-indicator"
  role="status"
  :aria-label="`Assistant is currently ${status}`"
  :aria-live="status === 'error' ? 'assertive' : 'polite'"
>
  <span class="status-dot" :class="status"></span>
  <span class="status-label">{{ statusLabel }}</span>
</div>
```

---

## 15. Mockup Descriptions

### 15.1 "Mission Control" Dashboard

Imagine a NASA mission control center, but for AI assistant activity:

**Central Screen:**
- Large terminal output in center
- Real-time activity feed scrolling on left
- Status indicators and metrics on right

**Top Bar:**
- Session timer (elapsed time)
- Token usage gauge (circular, prominent)
- Status indicator (pulsing dot)
- Quick actions (pause, export, clear)

**Bottom Panel:**
- Mini-timeline showing recent events (last 5 minutes)
- Expandable inspector panel (like browser DevTools)

**Visual Style:**
- Dark theme (reduces eye strain)
- Neon accents (cyan, green, yellow for different states)
- Monospace fonts for terminal content
- San-serif for UI labels

### 15.2 "Code Flow" View

Focus on file changes and code evolution:

**Left Panel (30%):**
- File tree with heat map indicators
- Click file to see history of changes

**Center Panel (50%):**
- Diff viewer showing current file being edited
- Real-time highlighting as changes occur
- Syntax highlighting with theme support

**Right Panel (20%):**
- Statistics for selected file
  - Number of edits
  - Lines added/removed
  - Tokens used on this file
- Related files (imports, dependencies)

### 15.3 "Brain View" (Cognitive Visualization)

Abstract visualization of assistant's thought process:

**Main Area:**
- Network graph showing concepts and relationships
- Nodes = thoughts/concepts
- Edges = relationships/dependencies
- Size = importance/time spent
- Color = type (analysis, planning, execution)

**Animation:**
- New thoughts appear as bubbles
- Active thought pulses
- Completed thoughts fade to background
- Connections draw as relationships form

**Interaction:**
- Click node to see details
- Hover for quick preview
- Pan and zoom to explore thought space

---

## 16. Key Insights & Recommendations

### 16.1 User Research Considerations

**Personas:**
1. **Developer using assistant for coding** - Wants to understand what changed
2. **QA testing assistant behavior** - Needs detailed logs and replay
3. **Manager monitoring usage** - Interested in metrics and costs
4. **AI researcher studying behavior** - Wants raw event data export

**User Needs:**
- Transparency: "What is the assistant doing right now?"
- Control: "Can I stop/pause this operation?"
- Verification: "Did it do what I asked?"
- Learning: "Why did it make this choice?"
- Debugging: "What went wrong?"

### 16.2 Design Principles

1. **Progressive Disclosure**: Start simple, allow drilling down
2. **Real-Time Feedback**: Never leave user wondering what's happening
3. **Contextual Actions**: Right action at right time
4. **Consistent Visual Language**: Same icons/colors mean same things
5. **Performance First**: UI must remain responsive under load

### 16.3 Metrics for Success

**Qualitative:**
- User reports feeling "in control"
- Reduced confusion about assistant behavior
- Faster debugging when things go wrong

**Quantitative:**
- Time to identify error root cause (target: <30s)
- User interaction rate with observability features (target: >60%)
- Session replay usage (indicates value in historical view)

---

## 17. Future Vision

### 17.1 Predictive Insights

AI analyzing the AI:

```
┌─────────────────────────────────────────────┐
│ Predictive Insights                         │
├─────────────────────────────────────────────┤
│                                             │
│ 🔮 Prediction: This task will likely:       │
│   • Take ~8 more minutes                    │
│   • Use 3,000 more tokens ($0.08)           │
│   • Modify 3 additional files               │
│   • Require 1 test fix                      │
│                                             │
│ Confidence: ████████░░ 82%                  │
│                                             │
│ Based on: 47 similar past sessions          │
│                                             │
└─────────────────────────────────────────────┘
```

### 17.2 Collaborative Observability

Multiple users watching same session:

```
┌─────────────────────────────────────────────┐
│ Viewers (3) 👥👥👥                           │
├─────────────────────────────────────────────┤
│                                             │
│ Alice (you): Viewing + commenting           │
│ Bob: Viewing                                │
│ Charlie: Viewing + controlling              │
│                                             │
│ 💬 Bob: "Why did it skip the tests?"        │
│ 💬 You: "Good question, let me check..."    │
│                                             │
└─────────────────────────────────────────────┘
```

### 17.3 Integration with Dev Tools

IDE plugin that syncs with web UI:

```
VS Code Extension:
┌─────────────────────────────────────────────┐
│ Claude Code Assistant                       │
├─────────────────────────────────────────────┤
│ ● Active (Editing src/api.ts)               │
│                                             │
│ [Open Dashboard] [Pause] [View History]    │
│                                             │
│ Recent Activity:                            │
│ • 2s ago: Edited src/api.ts                 │
│ • 5s ago: Ran npm test                      │
│ • 8s ago: Read src/types.ts                 │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 18. Conclusion

This document presents a comprehensive vision for transforming the Terminal Assistant UI from a simple terminal output viewer into a rich, multi-dimensional observability platform. The proposed features range from essential MVP components (status indicators, activity feeds) to advanced future concepts (cognitive visualization, predictive insights).

**Key Takeaways:**

1. **Start with Basics**: Implement Phase 1 (MVP) first - status indicator, activity feed, token usage, file changes
2. **Prioritize Real-Time**: Users need immediate feedback on what's happening
3. **Enable Debugging**: Error panels, context, and replay features are critical
4. **Think Holistically**: Assistant activity spans cognitive, file system, tool, and resource dimensions
5. **Design for Scale**: Use event streaming, throttling, and virtualization for performance

**Next Steps:**

1. Review and prioritize features based on user needs
2. Create high-fidelity mockups for Phase 1 MVP
3. Implement event emission infrastructure in backend
4. Build basic observability components in frontend
5. User test with real coding sessions
6. Iterate based on feedback

---

**Document Status:** ✅ Complete
**Last Updated:** 2025-10-21
**Contributors:** TechSpecExpert
**Related Documents:**
- `/Users/chris/big-3-super-agent/apps/content-gen/specs/terminal-assistant-ui-spec.md` (Base Technical Spec)
