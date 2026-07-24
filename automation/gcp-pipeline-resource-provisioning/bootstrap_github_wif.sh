#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ID="gen-lang-client-0444933822"
GITHUB_REPOSITORY="NguyenCuong1989/DAIOF-Framewor"
POOL_ID="github-actions"
PROVIDER_ID="daiof-framewor"
SERVICE_ACCOUNT_ID="github-gcp-provisioner"
RESUME_RUN_ID="30117878807"
SYNC_GITHUB=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT_ID="${2:?missing value}"; shift 2 ;;
    --repository) GITHUB_REPOSITORY="${2:?missing value}"; shift 2 ;;
    --pool) POOL_ID="${2:?missing value}"; shift 2 ;;
    --provider) PROVIDER_ID="${2:?missing value}"; shift 2 ;;
    --service-account-id) SERVICE_ACCOUNT_ID="${2:?missing value}"; shift 2 ;;
    --resume-run-id) RESUME_RUN_ID="${2:?missing value}"; shift 2 ;;
    --no-github-sync) SYNC_GITHUB=0; shift ;;
    *) echo "UNKNOWN_ARGUMENT=$1" >&2; exit 64 ;;
  esac
done

TRACE_ID="gcp-wif-bootstrap-$(date -u +%Y%m%dT%H%M%SZ)-$$"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVIDENCE_DIR="$ROOT/evidence/$TRACE_ID"
LOG_DIR="$EVIDENCE_DIR/logs"
mkdir -p "$LOG_DIR"
STATUS="FAIL"
PHASE="bootstrap"

finalize() {
  rc=$?
  trap - EXIT
  set +e
  python3 - "$EVIDENCE_DIR/final-status.json" "$TRACE_ID" "$STATUS" "$PHASE" "$rc" <<'PY'
import datetime,json,pathlib,sys
path,trace_id,status,phase,rc=sys.argv[1:]
pathlib.Path(path).write_text(json.dumps({
  "schema":"APO.GCP.GITHUB.WIF.BOOTSTRAP.v1",
  "trace_id":trace_id,"status":status,"last_phase":phase,"exit_code":int(rc),
  "completed_at":datetime.datetime.now(datetime.timezone.utc).isoformat()
},indent=2),encoding="utf-8")
PY
  (
    cd "$EVIDENCE_DIR" || exit 1
    find . -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
  )
  zip_path="$ROOT/evidence/${TRACE_ID}.zip"
  (cd "$ROOT/evidence" && zip -qr "$zip_path" "$TRACE_ID")
  sha256sum "$zip_path" > "${zip_path}.sha256"
  echo "FINAL_STATUS=$STATUS"
  echo "LAST_PHASE=$PHASE"
  echo "EVIDENCE_ZIP=$zip_path"
  exit "$rc"
}
trap finalize EXIT
exec > >(tee -a "$LOG_DIR/terminal.log") 2> >(tee -a "$LOG_DIR/terminal.stderr.log" >&2)

for cmd in gcloud python3 zip sha256sum; do
  command -v "$cmd" >/dev/null || { echo "REQUIRED_COMMAND_MISSING=$cmd" >&2; exit 10; }
done

PHASE="identity"
ACTIVE_ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' | head -n1)"
[[ -n "$ACTIVE_ACCOUNT" ]] || { echo ACTIVE_GCLOUD_ACCOUNT_MISSING >&2; exit 11; }
ACCOUNT_SHA256="$(printf '%s' "$ACTIVE_ACCOUNT" | sha256sum | awk '{print $1}')"
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
[[ -n "$PROJECT_NUMBER" ]] || { echo PROJECT_NUMBER_MISSING >&2; exit 12; }
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
GITHUB_OWNER="${GITHUB_REPOSITORY%%/*}"

python3 - "$EVIDENCE_DIR/before.json" <<PY
import datetime,json,pathlib
pathlib.Path("$EVIDENCE_DIR/before.json").write_text(json.dumps({
  "schema":"APO.GCP.GITHUB.WIF.BEFORE.v1",
  "trace_id":"$TRACE_ID","project_id":"$PROJECT_ID","project_number":"$PROJECT_NUMBER",
  "github_repository":"$GITHUB_REPOSITORY","active_account_sha256":"$ACCOUNT_SHA256",
  "pool_id":"$POOL_ID","provider_id":"$PROVIDER_ID","service_account":"$SERVICE_ACCOUNT_EMAIL",
  "timestamp":datetime.datetime.now(datetime.timezone.utc).isoformat()
},indent=2),encoding="utf-8")
PY

PHASE="enable-apis"
gcloud services enable \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  composer.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  --project "$PROJECT_ID" > "$LOG_DIR/services-enable.log"

PHASE="service-account"
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project "$PROJECT_ID" --format=json > "$LOG_DIR/service-account-before.json" 2> "$LOG_DIR/service-account-before.stderr.log"; then
  gcloud iam service-accounts create "$SERVICE_ACCOUNT_ID" \
    --project "$PROJECT_ID" \
    --display-name "GitHub GCP Pipeline Provisioner" \
    --description "Keyless GitHub Actions identity for DAIOF dev orchestration-pipeline provisioning" \
    > "$LOG_DIR/service-account-create.log"
fi
gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project "$PROJECT_ID" --format=json > "$LOG_DIR/service-account-after.json"

PHASE="workload-identity-pool"
if ! gcloud iam workload-identity-pools describe "$POOL_ID" --project "$PROJECT_ID" --location global --format=json > "$LOG_DIR/pool-before.json" 2> "$LOG_DIR/pool-before.stderr.log"; then
  gcloud iam workload-identity-pools create "$POOL_ID" \
    --project "$PROJECT_ID" \
    --location global \
    --display-name "GitHub Actions Pool" \
    --description "Keyless GitHub Actions identities" \
    > "$LOG_DIR/pool-create.log"
fi
POOL_NAME="$(gcloud iam workload-identity-pools describe "$POOL_ID" --project "$PROJECT_ID" --location global --format='value(name)')"
[[ -n "$POOL_NAME" ]] || { echo WORKLOAD_IDENTITY_POOL_NAME_MISSING >&2; exit 13; }

PHASE="workload-identity-provider"
EXPECTED_CONDITION="assertion.repository == '${GITHUB_REPOSITORY}'"
if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project "$PROJECT_ID" --location global --workload-identity-pool "$POOL_ID" \
  --format=json > "$LOG_DIR/provider-before.json" 2> "$LOG_DIR/provider-before.stderr.log"; then
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
    --project "$PROJECT_ID" \
    --location global \
    --workload-identity-pool "$POOL_ID" \
    --display-name "DAIOF-Framewor GitHub Provider" \
    --issuer-uri "https://token.actions.githubusercontent.com" \
    --attribute-mapping "google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
    --attribute-condition "$EXPECTED_CONDITION" \
    > "$LOG_DIR/provider-create.log"
fi
PROVIDER_NAME="$(gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project "$PROJECT_ID" --location global --workload-identity-pool "$POOL_ID" \
  --format='value(name)')"
ACTUAL_CONDITION="$(gcloud iam workload-identity-pools providers describe "$PROVIDER_ID" \
  --project "$PROJECT_ID" --location global --workload-identity-pool "$POOL_ID" \
  --format='value(attributeCondition)')"
[[ "$ACTUAL_CONDITION" == "$EXPECTED_CONDITION" ]] || {
  echo "PROVIDER_CONDITION_CONFLICT" >&2
  echo "EXPECTED=$EXPECTED_CONDITION" >&2
  echo "ACTUAL=$ACTUAL_CONDITION" >&2
  exit 14
}

PHASE="impersonation-binding"
PRINCIPAL_SET="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository/${GITHUB_REPOSITORY}"
gcloud iam service-accounts add-iam-policy-binding "$SERVICE_ACCOUNT_EMAIL" \
  --project "$PROJECT_ID" \
  --role roles/iam.workloadIdentityUser \
  --member "$PRINCIPAL_SET" \
  --condition=None > "$LOG_DIR/workload-identity-user-binding.log"

PHASE="project-roles"
ROLES=(
  roles/composer.environmentAndStorageObjectAdmin
  roles/iam.serviceAccountUser
  roles/bigquery.dataEditor
  roles/storage.objectAdmin
)
for role in "${ROLES[@]}"; do
  safe_name="${role//\//_}"
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member "serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role "$role" \
    --condition=None > "$LOG_DIR/${safe_name}.log"
done

gcloud iam service-accounts get-iam-policy "$SERVICE_ACCOUNT_EMAIL" --project "$PROJECT_ID" --format=json > "$LOG_DIR/service-account-policy.json"
gcloud projects get-iam-policy "$PROJECT_ID" --flatten='bindings[].members' \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT_EMAIL" --format=json > "$LOG_DIR/project-role-bindings.json"

PHASE="github-sync"
GITHUB_SYNC="NOT_RUN"
if [[ "$SYNC_GITHUB" -eq 1 ]]; then
  if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh variable set GCP_PROJECT_ID --body "$PROJECT_ID" --repo "$GITHUB_REPOSITORY"
    gh variable set GCP_WIF_PROVIDER --body "$PROVIDER_NAME" --repo "$GITHUB_REPOSITORY"
    gh variable set GCP_SERVICE_ACCOUNT --body "$SERVICE_ACCOUNT_EMAIL" --repo "$GITHUB_REPOSITORY"
    GITHUB_SYNC="PASS"
    if [[ -n "$RESUME_RUN_ID" ]]; then
      gh run rerun "$RESUME_RUN_ID" --repo "$GITHUB_REPOSITORY"
    fi
  else
    GITHUB_SYNC="BLOCKED_GH_AUTH"
  fi
fi

python3 - "$EVIDENCE_DIR/result.json" <<PY
import datetime,json,pathlib
pathlib.Path("$EVIDENCE_DIR/result.json").write_text(json.dumps({
  "schema":"APO.GCP.GITHUB.WIF.RESULT.v1","trace_id":"$TRACE_ID","status":"PASS",
  "project_id":"$PROJECT_ID","project_number":"$PROJECT_NUMBER","github_repository":"$GITHUB_REPOSITORY",
  "workload_identity_pool":"$POOL_NAME","workload_identity_provider":"$PROVIDER_NAME",
  "service_account":"$SERVICE_ACCOUNT_EMAIL","principal_set":"$PRINCIPAL_SET",
  "project_roles":${ROLES[@]+["roles/composer.environmentAndStorageObjectAdmin","roles/iam.serviceAccountUser","roles/bigquery.dataEditor","roles/storage.objectAdmin"]},
  "github_variable_sync":"$GITHUB_SYNC","resume_run_id":"$RESUME_RUN_ID",
  "timestamp":datetime.datetime.now(datetime.timezone.utc).isoformat()
},indent=2),encoding="utf-8")
PY

STATUS="PASS"
PHASE="complete"
