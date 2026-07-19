#!/bin/zsh
set -u
set -o pipefail

REPO="${1:-$PWD}"
OUT="${2:-$REPO/artifacts/execution-canvas-gate-$(date -u '+%Y%m%dT%H%M%SZ')}"
mkdir -p "$OUT" || exit 2
exec > >(tee "$OUT/gate.log") 2>&1

fail() {
  printf '%s\n' 'FINAL_GATE=FAIL' "CAUSE=$1" "ARTIFACTS=$OUT"
  exit "${2:-1}"
}

printf '%s\n' \
  '===== EXECUTION CANVAS NATIVE GATE =====' \
  "TIME_UTC=$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
  "HOSTNAME=$(hostname)" \
  "REPO=$REPO"

[[ -d "$REPO/.git" ]] || fail NOT_A_GIT_CHECKOUT 10
cd "$REPO" || fail REPO_NOT_ACCESSIBLE 11
[[ "$(git branch --show-current)" == codex/execution-canvas ]] ||
  fail WRONG_BRANCH 12
git merge-base --is-ancestor d47f319 HEAD ||
  fail REQUIRED_COMMIT_MISSING 13

git status --short > "$OUT/git_status.txt"
git log --oneline -5 > "$OUT/git_log.txt"
printf '%s\n' "HEAD=$(git rev-parse HEAD)"

WORKBENCH="$REPO/vscode-merged"
PACKAGE="$WORKBENCH/package.json"
LOCK="$WORKBENCH/package-lock.json"
[[ -f "$PACKAGE" ]] || fail WORKBENCH_PACKAGE_MISSING 20
PKG_NAME="$(node -p "require('$PACKAGE').name")"
printf '%s\n' "WORKBENCH_PACKAGE_NAME=$PKG_NAME"

if [[ "$PKG_NAME" == vscode-python-envs ]]; then
  cp "$PACKAGE" "$OUT/observed-package.json"
  [[ -f "$LOCK" ]] && cp "$LOCK" "$OUT/observed-package-lock.json"
  fail REPOSITORY_TOOLCHAIN_MISMATCH 21
fi

if [[ -f "$WORKBENCH/yarn.lock" ]] && command -v yarn >/dev/null 2>&1; then
  PM=yarn
  (
    cd "$WORKBENCH" &&
    yarn install --frozen-lockfile &&
    yarn gulp compile
  ) 2>&1 | tee "$OUT/build.log"
elif [[ -f "$LOCK" ]] && command -v npm >/dev/null 2>&1; then
  PM=npm
  (
    cd "$WORKBENCH" &&
    npm ci &&
    npm run compile
  ) 2>&1 | tee "$OUT/build.log"
else
  fail NO_PINNED_PACKAGE_MANAGER 22
fi
[[ "${pipestatus[1]}" -eq 0 ]] || fail NATIVE_COMPILE_FAILED 23
printf '%s\n' "PACKAGE_MANAGER=$PM" 'NATIVE_BUILD=PASS'

command -v lsof >/dev/null 2>&1 || fail LSOF_NOT_FOUND 30
lsof -nP -iTCP:9001 -sTCP:LISTEN > "$OUT/port9001_listener.txt" 2>&1 ||
  fail NO_LISTENER_ON_9001 31
cat "$OUT/port9001_listener.txt"

curl --silent --show-error --max-time 3 \
  http://127.0.0.1:9001/openapi.json > "$OUT/openapi.json" ||
  fail HYPERAI_OPENAPI_UNAVAILABLE 32

if command -v jq >/dev/null 2>&1; then
  jq -e '.paths["/api/v1/execution-canvas/events"]' "$OUT/openapi.json" >/dev/null ||
    fail INGESTION_ROUTE_MISSING 33
else
  grep -F '"/api/v1/execution-canvas/events"' "$OUT/openapi.json" >/dev/null ||
    fail INGESTION_ROUTE_MISSING 33
fi

printf '%s\n' \
  'SOURCE_COMMITTED=PASS' \
  'NATIVE_BUILD=PASS' \
  'HYPERAI_INGESTION_ENDPOINT=PASS' \
  'FINAL_GATE=PASS' \
  "ARTIFACTS=$OUT"
