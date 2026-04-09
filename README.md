# Dayli

Dayli is an LLM-powered conversational calendar assistant. Users can describe their day in natural language, iteratively refine it through conversation, and sync approved changes to external calendar providers.

## What this scaffold includes

- A production-oriented Python package layout
- Modular agent interfaces for planning, parsing, validation, calendar execution, and response generation
- Clear separation between user interaction, LLM reasoning, and tool integrations
- Memory and conversation state abstractions for iterative scheduling
- Deterministic domain services for conflict checking and schedule edits

## Architecture

```text
User/API
  -> Conversation Manager
  -> Agent Router / Workflow
  -> Planner Agent
  -> Parser Agent
  -> Validator Agent
  -> Calendar Agent
  -> Response Agent
  -> Calendar Providers + Persistence + Memory
```

## Project structure

```text
dayli/
├── apps/
│   ├── api/
│   ├── mobile/
│   └── worker/
├── dayli/
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── domain/
│   ├── llm/
│   ├── memory/
│   ├── observability/
│   ├── orchestration/
│   ├── prompts/
│   ├── repositories/
│   └── tools/
├── tests/
└── pyproject.toml
```

## Core modules

### `apps/api`

FastAPI app entrypoint with chat, session, and health routes.

### `apps/mobile`

Expo React Native client for the iPhone demo. It provides a chat-style interface, starter prompts, and schedule preview cards backed by the Dayli API.

### `dayli/orchestration`

Owns the end-to-end conversation workflow. The `ConversationManager` loads memory, routes intent, invokes agents, and returns a user-safe result.

### `dayli/agents`

- `PlannerAgent`: classifies user intent and determines the required workflow
- `ParserAgent`: extracts structured events and edit instructions from natural language
- `ValidatorAgent`: checks constraints, conflicts, ambiguity, and policy violations
- `CalendarAgent`: executes approved calendar operations through tool adapters
- `ResponseAgent`: generates concise conversational responses based on the workflow result

### `dayli/domain`

Contains deterministic scheduling logic, edit operations, and conflict rules. This layer should own business logic rather than prompts.

### `dayli/memory`

Supports:

- short-term conversation state
- persistent user preferences
- summarized historical context

### `dayli/llm`

Abstraction around model clients, structured outputs, and guardrails. This is the boundary for prompt execution.

### `dayli/tools`

Calendar providers and time/availability utilities. This is the only layer that should perform external side effects.

## Example flow

1. User sends: `Move my gym to tomorrow`
2. API forwards the message to `ConversationManager`
3. Memory is loaded for the current session and user
4. Planner detects an event edit request
5. Parser extracts target event and requested change
6. Validator resolves conflicts and missing references
7. Calendar agent updates the provider event if valid
8. Response agent returns a user-facing confirmation

## Suggested stack

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Redis
- OpenAI API
- Google Calendar API
- Microsoft Graph API
- Celery or Dramatiq
- OpenTelemetry + Sentry

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn apps.api.main:app --reload
```

## iPhone demo path

Run the backend:

```bash
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

Run the Expo client:

```bash
cd apps/mobile
npm install
EXPO_PUBLIC_DAYLI_API_URL=http://YOUR_LOCAL_IP:8000 npm start
```

Open the project in Expo Go on your iPhone and use the starter prompts to demo:

- initial schedule creation
- iterative edits like `Move my gym to tomorrow`
- softer refinement like `Make my morning less busy`

Use your machine's LAN IP instead of `127.0.0.1` so the iPhone can reach the backend.

## Next build steps

1. Implement persistence repositories against PostgreSQL
2. Add Redis-backed session and summary memory
3. Replace the stub LLM client with a real provider integration
4. Add Google and Outlook OAuth flows
5. Add a preview/apply write mode before production calendar mutations
