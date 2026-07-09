# Task 9 Report

## Status
Implemented the Lab tab with reusable controls, live experiment runs through the shared API client, cumulative revenue/regret charts, arm-share stacking, rolling reward trend, and a winner summary panel.

## Files
- Created `frontend/src/pages/Lab.tsx`
- Created `frontend/src/components/LabControls.tsx`
- Created `frontend/src/charts/ArmShareChart.tsx`
- Created `frontend/src/charts/RewardTrendChart.tsx`
- Updated `frontend/src/App.tsx`
- Updated `frontend/src/styles.css`

## Verification
- Ran `cd frontend; npm run build`
- Build succeeded after rerunning unsandboxed because the sandboxed Vite/esbuild path hit Windows `spawn EPERM`

## Concerns
- Vite reports a pre-existing large-chunk warning for the production JS bundle (`566.59 kB` after minification).
- The Lab surface auto-runs the default experiment on first load so the tab is populated immediately; subsequent runs are explicit via the Run button.

## Task 9 Fixes
- Bounded Lab horizon controls and request construction to `10..1000`, so the UI cannot submit an out-of-range run.
- Snapshotted the settings from the last successful run and rewired KPI and winner-summary copy to use that snapshot; when controls diverge, the page now shows a clear rerun warning instead of silently relabeling old results.
- Removed implicit fixture fallback from `runExperiment()` so Lab POST failures surface as errors; kept fixture generation available only through an explicit helper for offline use.
- Removed the initial Lab auto-run and replaced it with a ready-state prompt that reflects the default configuration until the user clicks Run.
- Simplified the environment toggle semantics to pressed-state buttons and updated the controls copy to describe the explicit run behavior.

## Verification Refresh
- Re-ran `cd frontend; npm run build` after the fix set.
- Build succeeded; the remaining output is the existing Vite chunk-size warning for the production JS bundle.
