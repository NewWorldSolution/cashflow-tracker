---
name: P1-I5 UI feedback from manual testing
description: UI issues and improvements identified during first manual test session of P1-I4 on main
type: project
---

Feedback collected during first live test (2026-03-22) after P1-I4 merge.

**Why:** User tested the app for the first time and identified UX problems to fix in P1-I5.
**How to apply:** Use this list as the starting requirements for P1-I5 scope.

## Issues found

1. **Category dropdown not filtered by direction** — when creating a transaction, income categories and expense categories are shown together in one list. They should be split: only show income categories when direction=income, only show expense categories when direction=expense.

2. **No navigation from dashboard** — the `/` dashboard has no links to `/transactions/` or `/transactions/new`. Users must type URLs manually.

## Still to collect
User is still testing — more feedback may follow.
