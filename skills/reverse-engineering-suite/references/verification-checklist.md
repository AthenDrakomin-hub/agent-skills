# Verification Checklist

Pre-delivery quality gate for all three reverse-engineering paths. Run through this before declaring any analysis complete.

## Universal Checks (all paths)

- [ ] Every claim cites evidence (file:line, tool output, captured request, or decompiled function)
- [ ] No fabricated endpoints, functions, or data models
- [ ] Uncertain findings marked `[unverified]` or `[low confidence]`
- [ ] Output language matches user's language; technical identifiers in English
- [ ] No hardcoded local paths in generated code or docs
- [ ] All referenced scripts exist and are executable
- [ ] Report states limitations and missing inputs upfront

## Path A (Source Code → PRD) Checks

- [ ] `codebase_analyzer.py` ran successfully and `analysis.json` exists
- [ ] Every route in the codebase has a corresponding page doc
- [ ] Every API call in code has an entry in the API inventory
- [ ] Mock data is explicitly flagged as `[MOCK]`
- [ ] All enums and status codes collected in `enums.md`
- [ ] Page docs list every field with type, source, and validation
- [ ] Endpoint docs include method, path, auth, request schema, response schema, error codes
- [ ] State map covers both local and global state
- [ ] `prd_scaffolder.py` output structure matches expected layout
- [ ] Business descriptions are product-manager readable, not just code comments

## Path B (Binary → Analysis + Reimplementation) Checks

- [ ] `check-env.ps1` ran; required engines confirmed available
- [ ] Target subtype correctly identified per `target-routing.md`
- [ ] Surface analysis complete: strings, imports, exports, metadata
- [ ] Deep analysis used the correct engine for the subtype
- [ ] Every module has a breakdown from `module-breakdown-template.md`
- [ ] Report follows `report-template.md` structure
- [ ] Reimplementation plan follows `replication-guide.md`
- [ ] Legal-use assumption stated in report header
- [ ] No cracking/deobfuscation/license-bypass content
- [ ] Reimplementation code is independent rewrite, not verbatim decompiled copy
- [ ] No copyrighted assets, branding, or UI reproduced
- [ ] Packed/obfuscated targets flagged, not silently skipped
- [ ] Confidence levels assigned to all findings

## Path C (Website → Behavior Reconstruction) Checks

- [ ] Frontend assets captured; framework identified
- [ ] Network traffic captured via HAR or mitmproxy
- [ ] All observed endpoints cataloged with method, path, auth, schemas
- [ ] User flows documented as state machines (idle/loading/success/error)
- [ ] Loading, empty, and error states covered for each flow
- [ ] Data model inferred from responses, not guessed
- [ ] Design tokens extracted (colors, spacing, typography)
- [ ] Auth mechanism documented
- [ ] No attempts to access other users' data or unauthorized endpoints
- [ ] Clean-room code (if generated) is original implementation, not copied
- [ ] Rate limiting respected; no brute-forcing

## Output Quality Bar

An analysis is complete when:
1. An engineer could reconstruct the target's functionality using only the output
2. Every page/endpoint/module has a dedicated section
3. The difference between "observed" and "inferred" is explicit
4. The report is self-contained (does not require the original target to understand)
5. No section says "TODO" or "to be determined" without explaining why

## Confidence Rating Scale

Apply to each major finding:
- **High** — Direct evidence from source code, decompiled output, or captured traffic
- **Medium** — Inferred from multiple indirect evidence sources (e.g. string references + import patterns)
- **Low** — Single indirect evidence or reasonable assumption; must be flagged
- **Unknown** — Cannot be determined from available evidence; state explicitly
