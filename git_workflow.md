# Git Workflow — Quantum Technology for the Curious Engineer

This document describes how we use Git on this project. Everyone on the team (and future 3S groups inheriting this repo) should follow this to keep the history clean and avoid stepping on each other's work.

## Branch structure

```
master
 └── dev
      ├── feature/adf4351-control
      ├── feature/mqtt-broker-setup
      ├── feature/sqlite-schema
      └── feature/dashboard-ui
```

### `master
- Always in a **working, demo-able state**.
- Nothing is committed directly to `master`. Changes only arrive via a Pull Request (PR) from `dev`.
- This is what we show the client/committee if asked "can we see the current state of the project?"
- Tag milestones here as they happen, e.g. `v0.1-hardware-poc`, `v0.2-mqtt-integration`. Useful for reporting on project progress later.

### `dev`
- The integration branch. Finished features land here first.
- Should always build and run, but can be a little rougher than `master`.
- Periodically merged into `master` once stable (e.g. before a demo, or at the end of a sprint).

### `feature/xyz`
- One branch per unit of work. Branch off `dev`, not `master`.
- Naming: `feature/short-description` (e.g. `feature/photodiode-logging`, `feature/run-metadata-form`).
- Merged back into `dev` via PR when done, then **deleted**. Don't let old feature branches pile up.

### `hotfix/xyz` (as needed)
- For urgent fixes discovered close to a demo, when `dev` isn't in a mergeable state.
- Branch off ``, fix, then merge back into **both** `master` and `dev` so they don't drift apart.

## Day-to-day workflow

1. Make sure your local `dev` is up to date:
   ```
   git checkout dev
   git pull origin dev
   ```
2. Create your feature branch:
   ```
   git checkout -b feature/your-feature-name
   ```
3. Work, commit often, with meaningful messages (see below).
4. Before opening a PR, pull the latest `dev` into your branch and resolve any conflicts locally:
   ```
   git checkout dev
   git pull origin dev
   git checkout feature/your-feature-name
   git merge dev
   ```
5. Push your branch and open a PR into `dev`.
6. Get at least one other team member to review before merging.
7. After merging, delete the feature branch (locally and on the remote).

## Commit messages

Write commit messages that explain *what* changed and *why*, not just "stuff" or "fix". A good format:

```
<type>: <short description>

Optional longer explanation if needed.
```

Common types: `feat` (new feature), `fix` (bug fix), `docs` (documentation only), `refactor`, `test`, `chore` (tooling/config).

Examples:
- `feat: add MQTT topic structure for photodiode readings`
- `fix: correct SPI pulse timing for ESP32 clock speed`
- `docs: update setup instructions in README`

Good commit messages double as documentation — future 3S groups inheriting this project will read the commit history to understand how things evolved.

## Pull requests

- Even in a small team, get a second pair of eyes before merging into `dev` or `master`. This catches bugs early and matches how professional engineering teams operate — appropriate given this project's funding and client expectations.
- Keep PRs focused and reasonably small. A PR that touches five unrelated things is hard to review properly.
- Write a short PR description: what does this change, and why?

## Avoiding merge conflicts

Working in separate folders (e.g. `firmware/`, `backend/`, `dashboard/`) avoids most conflicts automatically. Conflicts are still possible in shared files, most commonly:

- `docker-compose.yml`
- `.env.example`
- Dependency files (`requirements.txt`, `package.json`)
- `README.md`
- Any shared schema/interface definitions (e.g. MQTT topic list, database schema file)

To minimize friction:
- Keep feature branches short-lived — merge often rather than letting branches diverge for weeks.
- Pull `dev` into your feature branch before opening a PR (step 4 above), so conflicts get resolved locally rather than surprising a reviewer.

## Repository hygiene

- Keep `README.md` on `master` current — setup instructions, architecture overview, and how to run the project. This is part of the deliverable, not an afterthought, since this project is meant to serve as an educational platform for future groups.
- Don't commit secrets (API keys, credentials, `.env` files) — use `.env.example` as a template and add real `.env` files to `.gitignore`.
- Don't commit large binary files or build artifacts — add them to `.gitignore` instead.
