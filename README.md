# rch-dabs

Declarative Automation Bundle for the RCH project. Manages job definitions as code and deploys to Databricks workspaces via Git + GitHub Actions CI/CD.

---

## CI/CD Pipeline Diagram

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        Git Branching Strategy                           │
└─────────────────────────────────────────────────────────────────────────┘

  Developer                  GitHub                        Databricks
  ─────────                  ──────                        ──────────

  ┌──────────────┐   ┌─────────────────────┐
  │ feature/*    │──>│  Push to feature    │
  │ branch       │   │  branch             │
  └──────────────┘   └────────┬────────────┘
                              │
                     ┌────────▼────────────┐
                     │  CI: Validate       │  ← ci.yml
                     │  (validate dev +    │
                     │   validate prod)    │
                     └────────┬────────────┘
                              │ ✅ Pass
                     ┌────────▼────────────┐
                     │  PR: feature → dev  │
                     └────────┬────────────┘
                              │
                     ┌────────▼────────────┐
                     │  CI: Validate       │  ← ci.yml (on PR)
                     └────────┬────────────┘
                              │ ✅ Pass
                     ┌────────▼────────────┐
                     │  Merge to dev       │
                     └────────┬────────────┘
                              │
                     ┌────────▼────────────┐     ┌──────────────────────┐
                     │  CD: Deploy Dev     │────>│  DEV Workspace       │
                     │  (validate + deploy)│     │  ┌────────────────┐  │
                     │  ← deploy-dev.yml   │     │  │ rch_daily_ops  │  │
                     └────────┬────────────┘     │  │ -dev           │  │
                              │                  │  └────────────────┘  │
                              │ Test in DEV      │  Catalog:            │
                              │                  │  rch-dbx-dev-        │
                     ┌────────▼────────────┐     │  catalog             │
                     │  PR: dev → main     │     └──────────────────────┘
                     └────────┬────────────┘
                              │
                     ┌────────▼────────────┐
                     │  CI: Validate       │  ← ci.yml (on PR)
                     └────────┬────────────┘
                              │ ✅ Pass
                     ┌────────▼────────────┐
                     │  Merge to main      │
                     └────────┬────────────┘
                              │
                     ┌────────▼────────────┐     ┌──────────────────────┐
                     │  CD: Deploy Prod    │────>│  PROD Workspace      │
                     │  (validate + deploy)│     │  ┌────────────────┐  │
                     │  ← deploy-prod.yml  │     │  │ rch_daily_ops  │  │
                     └─────────────────────┘     │  │ -prod          │  │
                                                 │  └────────────────┘  │
                                                 │  Catalog:            │
                                                 │  rch-dbx-prod-       │
                                                 │  catalog             │
                                                 │  run_as: SP (PROD)   │
                                                 └──────────────────────┘
```

### Flow Summary

```text
feature/* ──push──> CI validates
    │
    └──PR──> dev ──merge──> DEV workspace
                    │
                    └──PR──> main ──merge──> PROD workspace
```

| Stage | Trigger | Workflow | Action |
| --- | --- | --- | --- |
| **CI** | Push to `feature/**` | `ci.yml` | `bundle validate` (dev + prod) |
| **CI** | PR to `dev` or `main` | `ci.yml` | `bundle validate` (dev + prod) |
| **CD Dev** | Push to `dev` (merge) | `deploy-dev.yml` | `bundle validate` + `bundle deploy --target dev` |
| **CD Prod** | Push to `main` (merge) | `deploy-prod.yml` | `bundle validate` + `bundle deploy --target prod` |

> **Rule**: Feature branches (`feature/*`) cannot PR directly to `main`. The flow must go through `dev` first. The CI workflow will block and fail if this rule is violated.

---

## Project Structure

```text
rch-dabs/
├── databricks.yml                   → Bundle config (targets: dev & prod)
├── resources/
│   └── daily-ops-jobs.yml           → Job resource definition
├── src/
│   └── tasks/
│       └── reconciliation.py        → RCH reconciliation notebook
└── .github/workflows/
    ├── ci.yml                       → Validates on PRs + feature branch pushes
    ├── deploy-dev.yml               → Deploys to DEV on push to 'dev'
    └── deploy-prod.yml              → Deploys to PROD on push to 'main'
```

---

## Setup Guide

### 1. Prerequisites

- Databricks CLI installed (`databricks/setup-cli@main` in GitHub Actions)
- Two Databricks workspaces (DEV + PROD)
- One Service Principal per workspace for OAuth M2M authentication

### 2. Create Service Principals

In the **Databricks Account Console** (accounts.cloud.databricks.com):

1. Go to **User management** → **Service principals**
2. Create a Service Principal for DEV (e.g., `RCHServicePrincipalDEV`)
3. Create a Service Principal for PROD (e.g., `RCHServicePrincipalPROD`)
4. For each SP: generate an **OAuth secret** (Client ID + Client Secret)
5. **Assign each SP to its workspace** (Workspace access tab → Add to workspace)
6. Grant each SP permissions on its respective Unity Catalog

### 3. Configure GitHub Secrets

In your GitHub repo: **Settings** → **Secrets and variables** → **Actions**, add these secrets:

| Secret Name | Value |
| --- | --- |
| `DATABRICKS_DEV_HOST` | `https://xxxxxxxxxxxxxxxxxx.cloud.databricks.com` |
| `DATABRICKS_DEV_CLIENT_ID` | DEV Service Principal Application ID |
| `DATABRICKS_DEV_CLIENT_SECRET` | DEV Service Principal OAuth Secret |
| `DATABRICKS_PROD_HOST` | `https://xxxxxxxxxxxxxxxxxx.cloud.databricks.com` |
| `DATABRICKS_PROD_CLIENT_ID` | PROD Service Principal Application ID |
| `DATABRICKS_PROD_CLIENT_SECRET` | PROD Service Principal OAuth Secret |

### 4. Authentication Method

All workflows use **OAuth M2M** (machine-to-machine) via environment variables:

```yaml
env:
  DATABRICKS_AUTH_TYPE: oauth-m2m
  DATABRICKS_HOST: ${{ secrets.DATABRICKS_<ENV>_HOST }}
  DATABRICKS_CLIENT_ID: ${{ secrets.DATABRICKS_<ENV>_CLIENT_ID }}
  DATABRICKS_CLIENT_SECRET: ${{ secrets.DATABRICKS_<ENV>_CLIENT_SECRET }}
```

No tokens or `.databrickscfg` files needed — credentials stay in GitHub Secrets.

---

## How to Use

### Daily Workflow for Developers

```text
1. Create feature branch     →  git checkout -b feature/my-change
2. Make changes              →  Edit notebooks, YAML, or config
3. Validate locally          →  databricks bundle validate --target dev
4. Push to feature branch    →  CI validates automatically
5. Open PR: feature → dev    →  CI validates again
6. Merge to dev              →  Auto-deploys to DEV workspace
7. Test in DEV               →  Verify job runs correctly
8. Open PR: dev → main       →  CI validates (dev + prod)
9. Merge to main             →  Auto-deploys to PROD workspace
```

### Bundle Commands (Local Development)

| Command | What it does |
| --- | --- |
| `databricks bundle validate --target dev` | Check YAML for errors (no workspace changes) |
| `databricks bundle deploy --target dev` | Upload files + create/update job in DEV |
| `databricks bundle run rch_daily_ops --target dev` | Trigger job run immediately in DEV |
| `databricks bundle summary --target dev` | Show deployed resource URLs and state |

> **Note**: `deploy` only updates definitions. It does **not** run the job. Manual UI changes will be overwritten on next deploy.

---

## Making Changes

| What to change | Steps |
| --- | --- |
| **Add a task** | Create notebook in `src/tasks/` + add task entry in `resources/daily-ops-jobs.yml` |
| **Add a job** | Create new `resources/<name>.yml` |
| **Change schedule** | Edit `schedule` in `resources/daily-ops-jobs.yml` |
| **Change parameters** | Edit `parameters` in `resources/daily-ops-jobs.yml` |
| **Change catalog/schema** | Edit `variables` in `databricks.yml` |
| **Update notebook code** | Edit file in `src/tasks/`, commit and push |

---

## Environment Details

| Aspect | DEV | PROD |
| --- | --- | --- |
| **Feature branches** | `feature/*` | N/A |
| **Deploy branch** | `dev` | `main` |
| **Workspace** | `xxxxxxxxxxxxxxxxxx` | `xxxxxxxxxxxxxxxxxx` |
| **Catalog** | `rch-dbx-dev-catalog` | `rch-dbx-prod-catalog` |
| **Schema** | `analytics` | `analytics` |
| **Job Name** | `rch_daily_ops-dev` | `rch_daily_ops-prod` |
| **Schedule** | Every 6 hours (:55) | Every 6 hours (:55) |
| **run_as** | Current user | Service Principal (PROD) |

---

## Troubleshooting

| Issue | Solution |
| --- | --- |
| Job changed after deploy | Expected — deploy overwrites job to match YAML |
| Auth error in GitHub Actions | Verify Service Principal secrets in GitHub repo settings |
| SP "doesn't exist" error | Ensure SP is assigned to the target workspace in Account Console |
| Validation fails | Run `databricks bundle validate --target dev` locally |
| Job fails at runtime | Check catalog/schema exist with correct permissions |
| Can't deploy prod manually | By design — prod only deploys via merge to `main` |

---

**Reference:** [CI/CD on Databricks](https://docs.databricks.com/aws/en/dev-tools/ci-cd/) — official Databricks documentation.
