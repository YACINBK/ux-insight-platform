# Frontend — UX Insight dashboard

Angular 20 + Angular Material single-page dashboard for the UX Insight
Platform. It talks to the Spring Boot gateway (default
`http://localhost:8080/api`) and renders:

- **Stats cards** — total questions / attachments, plus a recent-questions panel
- **Manual Mode** — question form with image + JSON attachments; images are
  analyzed by the vision service before the whole submission goes to the LLM
- **Premium Auto Mode** — URL input returning demo analysis scores (labeled as
  demo in the UI)
- **Chat panel** — the LLM's answers, with a loading spinner between turns

## Structure

```
src/app/
├── app.ts / app.config.ts        # root component + providers (no router: single page)
├── services/ux-tracking-service  # the one HTTP service (gateway API)
└── components/
    ├── dashboard/                # layout, stats, mode toggle, auto-analysis
    ├── question-form/            # manual-mode submission flow
    ├── file-upload/              # drag & drop + buttons (images / JSON)
    └── chat-conversation/        # answer bubbles + auto-scroll
public/env.js                     # runtime config: window.API_BASE_URL
```

## Runtime configuration

The API base URL is **not** baked into the bundle. `public/env.js` sets
`window.API_BASE_URL` (default `http://localhost:8080/api`) and is loaded by
`index.html` — edit it before building the Docker image to point at a
different gateway. (`docker compose` does not template it; it is a static
file served by nginx.)

## Commands

```bash
npm install
npm start        # dev server at http://localhost:4200 (expects the gateway on :8080)
npm run build    # production build → dist/
npm test         # Karma/Jasmine (smoke spec)
```

Docker: built by the root `docker-compose.yml` (multi-stage: Node 20 build →
nginx:alpine serving on port 4200, with an `/api/` reverse proxy to the
gateway for relative-URL deployments).

## Testing

One smoke spec (`app.spec.ts`) covers root-component creation and dashboard
rendering. Broader component/service tests are a roadmap item.
