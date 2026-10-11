# Website Reverse-Engineering Path (Path C)

Detailed workflow for analyzing a live website and producing a behavior reconstruction.

## Step 1 — Frontend Asset Capture

### Static download
```bash
# Download the landing page and linked assets
wget -r -l 3 -p -E https://target.com  # Linux/macOS
# or use browser DevTools: More tools → Save page as → Complete
```

### Bundle analysis
- Identify framework from JS bundle filenames (`_next/`, `nuxt/`, `assets/index-*.js`)
- Extract route definitions from bundled JS (search for `path:`, `Route`, `createRouter`)
- Map component names from minified code (React DevTools / Vue DevTools if available)
- Identify state management: Redux devtools, Vuex/Pinia, Zustand store names

### CSS / Design system extraction
- Collect CSS custom properties (`:root { --primary: ... }`)
- Identify design tokens: colors, spacing scale, typography scale, border radius
- Note component library (Tailwind classes, Ant Design, Material UI, custom)

## Step 2 — Network Traffic Capture

### Method 1 — Browser DevTools HAR
1. Open DevTools → Network tab
2. Check "Preserve log" and "Disable cache"
3. Navigate the full user flow (login → key features → logout)
4. Right-click → "Save all as HAR with content"

### Method 2 — CLI capture
```bash
# mitmproxy for full traffic capture
mitmweb --mode regular -w capture.mitm

# or curl individual endpoints
curl -s -H "Authorization: Bearer <token>" https://api.target.com/v1/endpoint | jq .
```

### API endpoint cataloging
For each captured request, record:
```
| Method | Path | Auth | Request Body | Response Shape | Status Codes |
```

Group endpoints by resource (users, orders, products, etc.).

## Step 3 — Behavior Specification

Document every user flow as a state machine:

```markdown
## Flow: User Login

### States
- idle (initial)
- typing
- submitting
- success → redirects to /dashboard
- error → shows inline message, returns to typing

### Transitions
| From | Event | To | Side Effect |
|---|---|---|---|
| idle | input change | typing | update form state |
| typing | submit click | submitting | POST /api/auth/login |
| submitting | 200 response | success | store token, redirect |
| submitting | 401 response | error | show "Invalid credentials" |
| error | input change | typing | clear error |
```

Include:
- Loading states (skeleton, spinner, disabled buttons)
- Empty states (no data, first-time user)
- Error states (network error, 4xx, 5xx, validation errors)
- Pagination / infinite scroll behavior
- Real-time updates (WebSocket, SSE, polling intervals)

## Step 4 — Data Model Inference

From API responses and frontend state, derive:
- Entities (User, Order, Product, etc.)
- Fields and types
- Relationships (one-to-many, many-to-many)
- Enumerations (status, role, type fields)

```markdown
## Entity: User
| Field | Type | Notes |
|---|---|---|
| id | string (UUID) | primary key |
| email | string | unique |
| role | enum | admin / user / guest |
| created_at | ISO 8601 | |
| profile | object | nested: {avatar, display_name} |
```

## Step 5 — Reconstruction Output

Deliver:
1. `behavior-spec.md` — all user flows with state machines
2. `api-inventory.md` — complete endpoint catalog with schemas
3. `frontend-map.md` — component tree, routes, state management, design tokens
4. `data-model.md` — inferred entities and relationships
5. `scaffolds/` — clean-room code (on request)

## Clean-Room Code Generation Rules

When generating reconstruction code:
- Write original implementation based on the behavior spec, not copied from their bundles
- Use your own component structure and styling
- API contracts (endpoints, request/response shapes) can be replicated — these are interfaces, not copyrightable expression
- Do not copy their branding, copy, images, or exact visual design
- If the site uses proprietary algorithms (recommendation, pricing), describe observed behavior and implement a reasonable equivalent

## Authentication-Aware Analysis
- Only analyze endpoints accessible to the user's own account
- Do not attempt to access other users' data or admin endpoints without authorization
- If the site has rate limiting, respect it — do not brute-force endpoints
- Document auth mechanism (JWT, session cookie, OAuth, API key) in the report
