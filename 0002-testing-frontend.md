
# Testing Concept for Guardian Frontend

---

- status: draft
- supersedes: -
- superseded by: -
- date: 2023-11-03
- author: UCS@school team
- approval level: low
- coordinated with: {list everyone involved in the decision and whose opinions were sought (e.g. subject-matter experts)}
- scope: -
- resubmission: -

<!--
Explanation "approval level"

- low: Low impact on platform and business. Decisions at this level can be made within the TDA with the involved team(s). Other stakeholders are then informed.
- medium: Decisions of medium scope, i.e. minor adjustments to the platform or strategic decisions regarding specifications. The approval of the product owner is requested and the decision is made jointly.
- high: Decisions with a high impact on the business and IT. Changes that have a high-cost implication or strategic impact, among other things. These types of decisions require the decision to be made together with the leadership board.
-->

---

## Context and Problem Statement

We want to make sure the Guardian frontend supports all expected use cases.
Tests are a way to document those, make sure they are robust and performant, and prevent future work
to affect already published features.

## Considered Options

1: End-to-end tests
- Option 1.1: Playwright
- Option 1.2: Cypress

2: Unit tests
- Option 2.1: Vitest
- Option 2.2: Jest

## Pros and Cons of the Options

### Option 1.1: Playwright

- Good, because it's already used for other product parts ([ADR](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0001-playwright-for-ete-testing.md?ref_type=heads))

### Option 1.2: Cypress

- Good, because we already used it in other Vue projects (BSB RAM, Univention Portal) and have experience with it.

### Option 2.1: Vitest

- Good, because it is a Vite-native testing tool, and we use Vite

### Option 2.2: Jest

- Good, because we use it in other Vue projects (Univention Portal).
- Neutral, the Jest experience does not lie in the UCS@school team though

## Decision Outcome

Chosen option for E2E tests: "Option 1.1: Playwright"

We already have an [ADR](https://git.knut.univention.de/univention/decision-records/-/blob/main/dev/0001-playwright-for-ete-testing.md?ref_type=heads)
to use Playwright for other product parts, and we don't want to use too many different tools.
Also using Playwright has no visible downside to cypress feature wise.

Chosen option for unit tests: "Option 1.1: Vitest"

As we already use Vite as build tool/dev server, using Vitest (which is a Vite native testing tool) reduces
the amount of dependencies configuration and maintenance of an additional tool.
