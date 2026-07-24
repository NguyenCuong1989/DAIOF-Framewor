#!/usr/bin/env bash
set -Eeuo pipefail

MODE="auto"
APPROVE_DEPLOY=0
ENV_NAME="dev"
PROJECT_ID=""
REGION=""
BQ_LOCATION=""
COMPOSER_ENVIRONMENT=""
ARTIFACT_BUCKET=""
DATASET_ID=""
TABLE_ID="agent_events"
KEEP_WORK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:?missing value}"; shift 2 ;;
    --approve-deploy) APPROVE_DEPLOY=1; shift ;;
    --environment) ENV_NAME="${2:?missing value}"; shift 2 ;;
    --project) PROJECT_ID="${2:?missing value}"; shift 2 ;;
    --region) REGION="${2:?missing value}"; shift 2 ;;
    --bq-location) BQ_LOCATION="${2:?missing value}"; shift 2 ;;
    --composer-environment) COMPOSER_ENVIRONMENT="${2:?missing value}"; shift 2 ;;
    --artifact-bucket) ARTIFACT_BUCKET="${2:?missing value}"; shift 2 ;;
    --dataset-id) DATASET_ID="${2:?missing value}"; shift 2 ;;
    --table-id) TABLE_ID="${2:?missing value}"; shift 2 ;;
    --keep-work) KEEP_WORK=1; shift ;;
    *) echo "UNKNOWN_ARGUMENT=$1" >&2; exit 64 ;;
  esac
done

case "$MODE" in discover|validate|auto|deploy|verify) ;; *) echo "INVALID_MODE=$MODE" >&2; exit 64 ;; esac
if [[ "$MODE" == "deploy" && "$APPROVE_DEPLOY" -ne 1 ]]; then
  echo "DEPLOYMENT_GATE=DENIED" >&2
  exit 66
fi

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACE_ID="gcp-resource-provisioning-$(date -u +%Y%m%dT%H%M%SZ)-$$"
WORK_DIR="$BASE_DIR/work/$TRACE_ID"
EVIDENCE_DIR="$BASE_DIR/evidence/$TRACE_ID"
LOG_DIR="$EVIDENCE_DIR/logs"
mkdir -p "$WORK_DIR/scripts" "$LOG_DIR"
STATUS="FAIL"
PHASE="bootstrap"
DEPLOY_RAN=0

finalize() {
  rc=$?
  trap - EXIT
  set +e
  python3 - "$EVIDENCE_DIR/final-status.json" "$TRACE_ID" "$STATUS" "$PHASE" "$rc" "$DEPLOY_RAN" <<'PY'
import datetime, json, pathlib, sys
path, trace_id, status, phase, rc, deploy_ran = sys.argv[1:]
pathlib.Path(path).write_text(json.dumps({
  "schema": "APO.GCP.PIPELINE.RESOURCE.PROVISIONING.EVIDENCE.v3",
  "trace_id": trace_id,
  "status": status,
  "last_phase": phase,
  "exit_code": int(rc),
  "deployment_ran": deploy_ran == "1",
  "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
}, indent=2), encoding="utf-8")
PY
  (
    cd "$EVIDENCE_DIR" || exit 1
    find . -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
  )
  zip_path="$BASE_DIR/evidence/${TRACE_ID}.zip"
  (cd "$BASE_DIR/evidence" && zip -qr "$zip_path" "$TRACE_ID")
  sha256sum "$zip_path" > "${zip_path}.sha256"
  [[ "$KEEP_WORK" -eq 1 || "$STATUS" != PASS ]] || rm -rf "$WORK_DIR"
  echo "FINAL_STATUS=$STATUS"
  echo "LAST_PHASE=$PHASE"
  echo "EVIDENCE_ZIP=$zip_path"
  exit "$rc"
}
trap finalize EXIT
exec > >(tee -a "$LOG_DIR/terminal.log") 2> >(tee -a "$LOG_DIR/terminal.stderr.log" >&2)

for cmd in gcloud python3 zip sha256sum grep awk; do
  command -v "$cmd" >/dev/null || { echo "REQUIRED_COMMAND_MISSING=$cmd" >&2; exit 10; }
done

PHASE="identity"
[[ -n "$PROJECT_ID" ]] || PROJECT_ID="$(gcloud config get-value project 2>"$LOG_DIR/project.stderr.log")"
[[ -n "$PROJECT_ID" && "$PROJECT_ID" != "(unset)" ]] || { echo PROJECT_ID_MISSING >&2; exit 11; }
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)' 2>"$LOG_DIR/project-number.stderr.log")"
[[ -n "$PROJECT_NUMBER" ]] || { echo PROJECT_NUMBER_MISSING >&2; exit 12; }
ACTIVE_ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>"$LOG_DIR/auth.stderr.log" | head -n1)"
[[ -n "$ACTIVE_ACCOUNT" ]] || { echo ACTIVE_ACCOUNT_MISSING >&2; exit 13; }
ACCOUNT_SHA256="$(printf '%s' "$ACTIVE_ACCOUNT" | sha256sum | awk '{print $1}')"

PHASE="composer-discovery"
gcloud composer environments list --project "$PROJECT_ID" --format='csv[no-heading](name,location)' > "$LOG_DIR/composer-candidates.csv"
if [[ -z "$COMPOSER_ENVIRONMENT" ]]; then
  mapfile -t matches < <(awk -F, -v env="$ENV_NAME" 'BEGIN{IGNORECASE=1} index($1,env)>0{print}' "$LOG_DIR/composer-candidates.csv")
  if [[ ${#matches[@]} -eq 1 ]]; then
    COMPOSER_ENVIRONMENT="${matches[0]%%,*}"
    [[ -n "$REGION" ]] || REGION="${matches[0]#*,}"
  else
    mapfile -t all < "$LOG_DIR/composer-candidates.csv"
    if [[ ${#all[@]} -eq 1 ]]; then
      COMPOSER_ENVIRONMENT="${all[0]%%,*}"
      [[ -n "$REGION" ]] || REGION="${all[0]#*,}"
    else
      echo "COMPOSER_ENVIRONMENT_AMBIGUOUS_OR_MISSING" >&2
      exit 14
    fi
  fi
fi
[[ -n "$REGION" ]] || REGION="$(awk -F, -v n="$COMPOSER_ENVIRONMENT" '$1==n{print $2;exit}' "$LOG_DIR/composer-candidates.csv")"
[[ -n "$REGION" ]] || { echo REGION_MISSING >&2; exit 15; }
[[ -n "$BQ_LOCATION" ]] || BQ_LOCATION="$REGION"
[[ -n "$DATASET_ID" ]] || DATASET_ID="hyperai_events_${ENV_NAME//-/_}"

PHASE="bucket-discovery"
gcloud storage buckets list --project "$PROJECT_ID" --format='value(name)' > "$LOG_DIR/bucket-candidates.txt"
if [[ -z "$ARTIFACT_BUCKET" ]]; then
  mapfile -t buckets < <(awk -v env="$ENV_NAME" 'BEGIN{IGNORECASE=1} index($0,env)>0 && ($0~/artifact|pipeline|composer/){print}' "$LOG_DIR/bucket-candidates.txt")
  [[ ${#buckets[@]} -eq 1 ]] || { echo "ARTIFACT_BUCKET_AMBIGUOUS_OR_MISSING=${#buckets[@]}" >&2; exit 16; }
  ARTIFACT_BUCKET="${buckets[0]}"
fi

python3 - "$EVIDENCE_DIR/runtime-context.json" <<PY
import datetime, json, os, pathlib, platform
pathlib.Path("$EVIDENCE_DIR/runtime-context.json").write_text(json.dumps({
  "schema": "APO.GCP.RUNTIME.CONTEXT.v3",
  "trace_id": "$TRACE_ID",
  "mode": "$MODE",
  "project_id": "$PROJECT_ID",
  "project_number": "$PROJECT_NUMBER",
  "active_account_sha256": "$ACCOUNT_SHA256",
  "environment": "$ENV_NAME",
  "region": "$REGION",
  "bq_location": "$BQ_LOCATION",
  "composer_environment": "$COMPOSER_ENVIRONMENT",
  "artifact_bucket": "$ARTIFACT_BUCKET",
  "dataset_id": "$DATASET_ID",
  "table_id": "$TABLE_ID",
  "host": platform.node(),
  "platform": platform.platform(),
  "cwd": os.getcwd(),
  "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
}, indent=2), encoding="utf-8")
PY

if [[ "$MODE" == discover ]]; then STATUS=PASS; PHASE=discover-complete; exit 0; fi

PHASE="resource-types"
gcloud beta orchestration-pipelines resource-types list > "$LOG_DIR/resource-types.log"
for type in bigquery.dataset bigquery.table; do grep -Fq "$type" "$LOG_DIR/resource-types.log" || { echo "UNSUPPORTED_RESOURCE_TYPE=$type" >&2; exit 17; }; done
gcloud composer environments describe "$COMPOSER_ENVIRONMENT" --project "$PROJECT_ID" --location "$REGION" --format=json > "$LOG_DIR/composer.json"
gcloud storage buckets describe "gs://$ARTIFACT_BUCKET" --format=json > "$LOG_DIR/bucket.json"

PHASE="render"
cp "$BASE_DIR/deployment.yaml.template" "$WORK_DIR/deployment.yaml"
cp "$BASE_DIR/hyperai-resource-smoke.yaml" "$WORK_DIR/"
cp "$BASE_DIR/scripts/smoke.py" "$WORK_DIR/scripts/"
python3 - "$WORK_DIR/deployment.yaml" <<PY
from pathlib import Path
p=Path("$WORK_DIR/deployment.yaml")
s=p.read_text()
for a,b in {
"__ENV_NAME__":"$ENV_NAME","__PROJECT_ID__":"$PROJECT_ID","__REGION__":"$REGION","__BQ_LOCATION__":"$BQ_LOCATION",
"__COMPOSER_ENVIRONMENT__":"$COMPOSER_ENVIRONMENT","__ARTIFACT_BUCKET__":"$ARTIFACT_BUCKET","__DATASET_ID__":"$DATASET_ID","__TABLE_ID__":"$TABLE_ID"}.items(): s=s.replace(a,b)
if "__" in s: raise SystemExit("UNRESOLVED_PLACEHOLDER")
if "updateAction: recreate" in s: raise SystemExit("RECREATE_FORBIDDEN")
p.write_text(s)
PY
cp "$WORK_DIR/deployment.yaml" "$EVIDENCE_DIR/deployment.resolved.yaml"
cp "$WORK_DIR/hyperai-resource-smoke.yaml" "$EVIDENCE_DIR/"

if [[ "$MODE" != verify ]]; then
  PHASE="validate-syntax"
  (cd "$WORK_DIR" && gcloud beta orchestration-pipelines validate --environment="$ENV_NAME" --mode=syntax-only > "$LOG_DIR/validate-syntax.log")
  PHASE="validate-full"
  (cd "$WORK_DIR" && gcloud beta orchestration-pipelines validate --environment="$ENV_NAME" > "$LOG_DIR/validate-full.log")
fi

SHOULD_DEPLOY=0
[[ "$MODE" == deploy ]] && SHOULD_DEPLOY=1
[[ "$MODE" == auto && "$APPROVE_DEPLOY" -eq 1 ]] && SHOULD_DEPLOY=1
if [[ "$SHOULD_DEPLOY" -eq 1 ]]; then
  command -v bq >/dev/null || { echo REQUIRED_COMMAND_MISSING=bq >&2; exit 18; }
  PHASE="before-state"
  set +e
  bq --project_id="$PROJECT_ID" show --format=prettyjson "$PROJECT_ID:$DATASET_ID" > "$LOG_DIR/before-dataset.json" 2> "$LOG_DIR/before-dataset.stderr.log"; echo $? > "$LOG_DIR/before-dataset.exitcode"
  bq --project_id="$PROJECT_ID" show --format=prettyjson "$PROJECT_ID:$DATASET_ID.$TABLE_ID" > "$LOG_DIR/before-table.json" 2> "$LOG_DIR/before-table.stderr.log"; echo $? > "$LOG_DIR/before-table.exitcode"
  set -e
  PHASE="deploy"
  DEPLOY_RAN=1
  (cd "$WORK_DIR" && gcloud beta orchestration-pipelines deploy --environment="$ENV_NAME" --local > "$LOG_DIR/deploy.log")
fi

if [[ "$MODE" == verify || "$SHOULD_DEPLOY" -eq 1 ]]; then
  PHASE="verify"
  bq --project_id="$PROJECT_ID" show --format=prettyjson "$PROJECT_ID:$DATASET_ID" > "$LOG_DIR/verify-dataset.json"
  bq --project_id="$PROJECT_ID" show --format=prettyjson "$PROJECT_ID:$DATASET_ID.$TABLE_ID" > "$LOG_DIR/verify-table.json"
  python3 - "$LOG_DIR/verify-table.json" <<'PY'
import json, pathlib, sys
x=json.loads(pathlib.Path(sys.argv[1]).read_text())
if x.get("requirePartitionFilter") is not True: raise SystemExit("PARTITION_FILTER_NOT_REQUIRED")
PY
fi

python3 - "$EVIDENCE_DIR/skill-result.json" <<PY
import datetime, json, pathlib
pathlib.Path("$EVIDENCE_DIR/skill-result.json").write_text(json.dumps({
  "schema":"APO.GCP.PIPELINE.RESOURCE.PROVISIONING.RESULT.v3",
  "trace_id":"$TRACE_ID","status":"PASS","project_id":"$PROJECT_ID","environment":"$ENV_NAME","region":"$REGION",
  "dataset":"$PROJECT_ID:$DATASET_ID","table":"$PROJECT_ID:$DATASET_ID.$TABLE_ID",
  "deployment":"PASS" if "$SHOULD_DEPLOY"=="1" else "NOT_RUN",
  "verification":"PASS" if ("$MODE"=="verify" or "$SHOULD_DEPLOY"=="1") else "NOT_RUN",
  "destructive_update_action":False,"completed_at":datetime.datetime.now(datetime.timezone.utc).isoformat()
}, indent=2), encoding="utf-8")
PY
STATUS="PASS"
PHASE="complete"
