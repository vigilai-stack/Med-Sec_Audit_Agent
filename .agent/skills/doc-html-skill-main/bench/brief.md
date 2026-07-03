# System to document: "PaySwift" checkout orchestration service

(Fictional system. Use ONLY these facts — do not invent extra detail, do not research anything.)

## Purpose
PaySwift is the checkout orchestration service that coordinates card payments for an e-commerce platform. It sits between the web storefront and external payment service providers (PSPs), owning retries, fraud checks, and idempotency.

## Components
- **Web storefront** — submits orders to the API.
- **Checkout API** — receives `POST /checkout`, orchestrates the payment.
- **Fraud service** — returns an allow/deny decision.
- **PSP adapter** — talks to the external payment provider; hard 8s timeout.
- **Ledger** — records authorized payments for reconciliation.

## Request flow
1. Storefront sends `POST /checkout` to the Checkout API.
2. API calls the Fraud service for a decision.
3. If allowed, API calls the PSP adapter to authorize the payment.
4. On success, API writes to the Ledger and returns confirmation.
5. On PSP timeout, API retries once with the same idempotency key, then fails gracefully.

## Key decisions
- Centralize orchestration in the Checkout API (not the web tier) to avoid duplicated retry logic.
- Use idempotency keys on authorize calls to prevent duplicate charges.
- Fraud decision owned by a single service.

## Risks
- PSP timeout without a defined retry policy → abandoned carts (likelihood medium, impact high).
- Duplicate charge on retry if idempotency is missing (likelihood low, impact high).
- Missing audit trail in the Ledger (likelihood medium, impact medium).

## Tech stack
- Language: TypeScript (Node.js).
- Datastore: PostgreSQL for the Ledger.
- Transport: REST/JSON over HTTPS.
- Deploy: containers behind an API gateway.

## Audience
Engineering, QA, and Product reviewers.

## Evidence references
- ADR-017 payment orchestration: docs/adr/017-payment-orchestration.md
- Checkout handler: services/checkout/handler.ts
