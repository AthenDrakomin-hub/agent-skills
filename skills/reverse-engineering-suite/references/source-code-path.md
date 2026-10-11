# Source Code Reverse-Engineering Path (Path A)

Detailed workflow for analyzing a source codebase and producing a PRD.

## Step 1 — Automated Scan

```bash
python3 scripts/codebase_analyzer.py <project-dir> -o analysis.json
```

The analyzer extracts:
- All routes and their corresponding components/pages
- Component tree with props and state
- API calls (endpoint, method, request/response shapes)
- State management (Redux/Pinia/Zustand/Vuex/Context)
- Data models and TypeScript interfaces / Pydantic schemas / Django models
- Enums, constants, and status code mappings
- Mock data vs real API integration detection

## Step 2 — Framework-Specific Analysis

### React / Next.js
- Scan `app/` (App Router) or `pages/` (Pages Router) for routes
- Identify Server Components vs Client Components (`'use client'`)
- Map `getServerSideProps` / `getStaticProps` data fetching
- Trace hooks: `useState`, `useEffect`, `useReducer`, custom hooks
- Analyze `_app.js` and `_document.js` for global config

### Vue / Nuxt
- Scan `pages/` for file-based routing
- Analyze `vuex` / `pinia` stores
- Trace `computed`, `watch`, lifecycle hooks
- Identify `nuxt.config.js` modules and plugins
- Map `middleware/` and `layouts/`

### Angular
- Scan `app-routing.module.ts` for routes
- Analyze `@Injectable` services and their HTTP calls
- Map `@Input`/`@Output` component communication
- Identify route guards and resolvers

### Backend (NestJS / Express / Django / FastAPI)
- Map all controllers/routers to endpoints
- Extract request DTOs and response serializers
- Identify middleware, guards, interceptors
- Map database models and relationships
- Trace service-layer business logic

## Step 3 — Page-by-Page Documentation

For each page/route, produce a document with:

```markdown
# {Route Path} — {Page Name}

## Purpose
One-sentence business purpose.

## Route & Navigation
- Path: /example
- Linked from: [list of pages/components that link here]
- Navigates to: [list of destinations]

## Fields & UI Elements
| Element | Type | Source | Validation | Behavior |
|---|---|---|---|---|
| Email input | text | user input | required, email format | updates form state |
| Submit button | button | — | disabled if invalid | calls POST /api/auth |

## API Calls
| Endpoint | Method | Trigger | Request | Response |
|---|---|---|---|---|
| /api/auth/login | POST | submit click | {email, password} | {token, user} |

## State
- Local: [list of useState/useRef/data]
- Global: [list of store slices used]

## Edge Cases
- Empty state: [what shows when no data]
- Error state: [what shows on API failure]
- Loading state: [skeleton/spinner]
```

## Step 4 — API Inventory

For each endpoint:
```markdown
## {METHOD} {path}

### Purpose
{business purpose}

### Auth
{none / JWT bearer / session cookie / API key}

### Request
| Field | Type | Required | Validation |
|---|---|---|---|

### Response (200)
| Field | Type | Description |
|---|---|---|

### Error Codes
| Code | Condition |
|---|---|
```

## Step 5 — Enum & Constant Dictionary

Collect all:
- Status codes (order status, user roles, payment states)
- Type discriminators (`type: 'admin' | 'user'`)
- Feature flags
- Configuration constants
- Error code mappings

## Step 6 — PRD Generation

```bash
python3 scripts/prd_scaffolder.py analysis.json -o prd/ -n "App Name"
```

Then fill in business-readable descriptions. The scaffold creates:
- `README.md` — executive summary
- `pages/` — one file per route
- `api/` — one file per endpoint
- `models/` — data schemas
- `enums.md` — constant dictionary
- `state.md` — state map

## Mock Detection Rules

Flag as mock if:
- Data is imported from a `mock/`, `fixtures/`, or `__mocks__/` directory
- API calls are wrapped in `if (process.env.NODE_ENV === 'development')`
- Endpoint URLs contain `mock`, `jsonplaceholder`, `dummy`, `example.com`
- Data is hardcoded arrays in component files without API calls

Mark each flagged item in the PRD as `[MOCK] — not a real integration`.
