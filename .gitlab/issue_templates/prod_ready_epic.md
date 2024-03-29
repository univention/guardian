<!--
Copyright (C) 2023 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

/label ~"App::Guardian"
/label ~"Team::UCS@school"
/label ~"Status::New"
/epic univention&573
/milestone %"First public Guardian release"

## Accounting

- Univention GmbH (424)
- Development: Epic 573 - Make Guardian production ready (22605)

## Story

As a \<role\><br/>
I can \<capability\>,<br/>
so that \<receive benefit\>.

## Context/description

A little context to the issue. Where does the task come from, what is needed for implementation. Everything which is important but doesn't fit the user story syntax can be written down here.

A user story should be self-contained and provide value when shipped. It should also contain a "single source of truth".

Additional points:

- If possible, list implementation constraints here (e.g. after a refinement)
- Separation to other user stories
- Desired artifacts (package, documentation, release, etc.)
- Specific requirements regarding documentation if required
- For UI-heavy stories: Mockups, wireframes, storyboards, etc.

## Acceptance criteria & steps for reproduction

- [ ]
- [ ]

- [ ] All changed lines are covered by a unit test, if possible.
  - [ ] Happy case.
  - [ ] Unhappy case (errors and edge cases).
- [ ] There is at least one end to end test that covers the changed lines.
- [ ] Evaluate performance of the change.
  - [ ] Read the parent epic and verify performance requirements.
  - [ ] If necessary, performance tests exist. See [Performance commitment](https://git.knut.univention.de/univention/internal/decision-records/-/blob/main/ucsschool/0008-performance-commitment.md)
  - [ ] If there are no specific performance requirements, improve or at least avoid worsening existing performance, if possible.
  - [ ] Document reasons for worse performance in the code and on the ticket, if applicable.

If the changes affect security features such as authentication or authorization:

- [ ] The affected security feature has a dedicated end to end integration test.

/label ~"App::Guardian"
