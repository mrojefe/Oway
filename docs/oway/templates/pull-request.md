# Template: pull request
Created: 2026-11-16T10:00:00Z · Last edited: 2026-11-16T10:00:00Z

The body of every pull request. One request is one PR. The title is a conventional commit in plain words, for example `fix(web): new threads no longer spike CPU`.

```markdown
## Problem
<one or two sentences: what was wrong or missing, how to see it>

## Change
<how it is fixed. If it spans parts, why>

## Scope
<slice id and issue it closes. Out of scope: ...>

## Verification
<the proof items that passed (ids from the matrix), at which revision, and what was not run. "Tests pass" alone is not enough. UI change: before and after images; motion or timing: a short video. Upload evidence to GitHub, never commit it>

## Agent
<role, model and harness that did the work>
```
