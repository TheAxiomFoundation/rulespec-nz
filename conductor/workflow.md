# Project Workflow

## Guiding Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
2. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` *before* implementation
3. **Test-Driven Development:** Write unit tests before implementing functionality.
4. **Bleeding Edge & High Code Coverage:** Enforce >90% code coverage across all modules.
5. **Progressive Strictness:** Ensure typing, formatting, and linting standards ramp up from local checks to phase checkpoints.
6. **Non-Interactive & CI-Aware:** Prefer non-interactive commands. Use `CI=true` for watch-mode tools to ensure single execution.

## Task Workflow

All tasks follow a strict lifecycle:

### Standard Task Workflow

1. **Select Task:** Choose the next available task from `plan.md` in sequential order
2. **Mark In Progress:** Before beginning work, edit `plan.md` and change the task from `[ ]` to `[~]`
3. **Write Failing Tests (Red Phase):**
   - Create a new test file for the feature or bug fix.
   - Write unit and property-based tests (using `hypothesis`) that clearly define the expected behavior.
   - **CRITICAL:** Run the tests and confirm they fail. Do not proceed until you have failing tests.
4. **Implement to Pass Tests (Green Phase):**
   - Write the minimum code necessary to make the tests pass.
   - Ensure implementation uses Pydantic v2, Pydantic AI, or other stack libraries where appropriate.
   - Run the test suite and confirm all tests now pass.
5. **Refactor and Profile:**
   - Refactor for quality, readability, and performance.
   - Profile performance bottlenecks using `scalene`.
   - Run local strictness checks: `basedpyright` for static typing and `ruff` for linting.
6. **Verify Coverage and Robustness:**
   - Run coverage reports (Target: >90% coverage):
     ```bash
     pixi run pytest --cov=nz --cov-report=html
     ```
   - Check test suite resilience using `mutmut` mutation testing for critical logical paths.
7. **Commit Code Changes:**
   - Stage all code changes related to the task.
   - Commit with a clear, structured message (e.g. `feat(auth): Add Pydantic validation for user model`).
8. **Attach Task Summary with Git Notes:**
   - Get the commit hash: `git log -1 --format="%H"`.
   - Attach detailed task summary with `git notes add -m "<note content>" <commit_hash>`.
9. **Record Commit in Plan:**
   - Update `plan.md` task status to `[x]` and append the first 7 characters of the commit hash.
10. **Commit Plan Update:**
    - Stage and commit the updated `plan.md`.

### Phase Completion Verification and Checkpointing Protocol

**Trigger:** Executed immediately after a task is completed that concludes a phase in `plan.md`.

1. **Announce Protocol Start:** Inform the user that the phase verification has begun.
2. **Ensure Test Coverage for Phase Changes:**
   - Determine phase scope using `git diff --name-only <previous_checkpoint_sha> HEAD`.
   - Verify every modified code file has corresponding tests (Unit, Integration, and E2E as required).
3. **Execute Automated Tests and Mutation Checks:**
   - Run unit, integration, and E2E tests: `pixi run pytest` / `pytest-goblin`.
   - Verify typing strictly: `pixi run basedpyright`.
   - Run comprehensive linting: `pixi run ruff check --select ALL`.
   - Verify coverage reports (>90% target) upload via `codecov`.
4. **Manual Verification Plan:**
   - Present a detailed, step-by-step verification plan to the user.
5. **Await Explicit User Feedback:**
   - Pause and await user confirmation before creating the checkpoint commit.
6. **Create Checkpoint Commit & Record:**
   - Perform the checkpoint commit and record its SHA in `plan.md` as `[checkpoint: <sha>]`.

## Quality Gates

Before marking any task complete, verify:
- [ ] All unit, integration, and E2E tests pass.
- [ ] Code coverage meets requirements (>90%) and is reported to Codecov.
- [ ] Strict type safety passes under `basedpyright`.
- [ ] Linters run cleanly under `ruff` with all applicable rules (`ALL`) enabled.
- [ ] No regression in performance metrics (verified via `scalene` if critical).
- [ ] Code complies with Pydantic v2 schemas and Pydantic AI agent designs where applicable.
- [ ] Implementation notes and Git Notes attached.

## Development & CI Commands

### Setup & Environment
```bash
# Initialize and sync bleeding-edge Pixi environment
pixi init
pixi add python ruff basedpyright pytest pytest-cov hypothesis mutmut scalene pydantic pydantic-ai
pixi run install
```

### Run Tests and Quality Suite
```bash
# Run pytest with coverage gate
pixi run pytest --cov=nz --cov-fail-under=90

# Run basedpyright strict typing check
pixi run basedpyright

# Run ruff checks
pixi run ruff check .

# Run mutation testing
pixi run mutmut run

# Profile with scalene
pixi run scalene your_script.py
```
