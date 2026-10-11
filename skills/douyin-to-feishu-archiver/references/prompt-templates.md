# Prompt Templates

Reusable skeletons for distilled prompts. Fill in the bracketed placeholders.

## Frontend Component Prompt
```
You are a senior [framework] developer. Build a [component name] with the following requirements:

## Behavior
- [interaction 1]
- [interaction 2]

## Visual Spec
- Layout: [flex/grid, direction, gap]
- Colors: [primary, secondary, background hex]
- Typography: [font family, sizes, weights]
- Spacing: [padding, margin values]

## Constraints
- Mobile-first, breakpoint at [768px]
- Accessibility: [ARIA labels, keyboard nav]
- No external UI libraries; use [CSS / Tailwind]

## Output
Provide the complete component file with inline styles or a scoped style block.
```

## API Endpoint Prompt
```
Design a RESTful API endpoint for [resource].

## Request
- Method: [GET/POST/PUT/DELETE]
- Path: /api/v1/[resource]
- Auth: [JWT / API key / none]
- Body params: [list with types and validation rules]

## Response
- Success (200): [JSON schema]
- Error (4xx): [error code mapping]

## Business Rules
1. [rule 1]
2. [rule 2]

## Output
Provide the route handler, request validation schema, and response type definitions.
```

## DevOps Pipeline Prompt
```
Set up a CI/CD pipeline for [project] using [GitHub Actions / GitLab CI].

## Stages
1. Lint & type check
2. Unit tests
3. Build
4. Deploy to [staging / production]

## Requirements
- [condition] triggers deployment
- Secrets: [list required env vars]
- Rollback: [strategy]

## Output
Provide the complete pipeline YAML file and a brief explanation of each stage.
```

## Distillation Rules
- Match the template to the video's primary category.
- Replace every placeholder with concrete content from the video.
- If the video does not provide a value, mark it `[to be confirmed]` rather than inventing one.
- Keep the output language consistent with the video's spoken language.
