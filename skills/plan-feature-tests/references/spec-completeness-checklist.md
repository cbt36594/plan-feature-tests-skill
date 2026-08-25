# Specification Completeness Checklist

Use this checklist before designing tests for UI, API, interaction, accessibility, or stateful behavior. Inspect only applicable items, but do not silently supply missing values.

## Source and Scope

- Identify the feature goal, entry points, affected modules, user roles, supported platforms, and explicit exclusions.
- Record the authoritative source and version for the spec, design, API contract, and implementation.
- List acceptance criteria with stable IDs. Flag duplicated, conflicting, or non-observable criteria.
- Identify every screen, component, dialog, list/card type, navigation path, and backend dependency in scope.

## UI and Content

For every affected screen, component, and responsive variant, confirm:

- Width, height, minimum/maximum size, aspect ratio, density, and safe-area behavior.
- Position, alignment, spacing, padding, margin, grouping, list/card density, and scroll behavior.
- Color, opacity, gradient, border, radius, shadow, elevation, and theme variants.
- Font family, size, weight, line height, letter spacing, truncation, wrapping, and dynamic text scaling.
- Icon/image source, dimensions, crop/fit behavior, resolution, animation, placeholder, and failure fallback.
- Exact title, label, button, hint, toast, dialog, empty/error text, localization, and data source.
- Default, pressed, focused, selected, loading, success, empty, error, disabled, permission-denied, unauthenticated, offline, and stale-data states.
- Tap/click target, gestures, keyboard behavior, duplicate tap, back/cancel, dismissal, navigation, and transition behavior.
- Small-screen, large-screen, orientation, keyboard-open, status/navigation bar, clipping, overlap, and scroll cases.

## Accessibility

- Confirm semantic roles, labels/content descriptions, state announcements, and reading/focus order.
- Confirm contrast, non-color indicators, touch target size, keyboard access, and visible focus.
- Confirm screen-reader behavior, dynamic font scaling, reduced-motion handling, and error identification when applicable.

## API and Data

- Confirm method, path, environment, headers, authentication, request parameters, encoding, and idempotency.
- Confirm response schema, field names/types/nullability, defaults, UI mapping, localization, and ordering.
- Confirm success, empty, partial, malformed, error-code, timeout, retry, offline, cache, stale-data, pagination, duplicate, and rate-limit behavior.
- Confirm encryption/public-key, cookie/token refresh, privacy, data retention, and destructive-operation rules when applicable.
- Confirm test accounts, fixtures, mock responses, backend controls, data reset, and ownership of cleanup.

## Logic and Runtime

- Confirm business rules, validation boundaries, sorting/filtering, state transitions, and persistence.
- Confirm lifecycle, cancellation, retry, concurrency, duplicate request, adapter/list recycling, process recreation, and foreground/background behavior.
- Confirm failure recovery, user feedback, telemetry/log expectations, and shared-component regression boundaries.

## Classify Every Gap

Record each missing, conflicting, or ambiguous item as `Needs Confirmation` with:

- Requirement or screen/component ID.
- Missing or conflicting parameter.
- Affected test cases and risk.
- Recommended source of truth or safe options.
- Whether unaffected planning can continue.

Do not convert a missing requirement into a generic default, personal preference, assumed PASS criterion, or hidden out-of-scope decision.
