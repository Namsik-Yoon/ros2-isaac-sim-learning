#!/usr/bin/env bash
# Headless compatibility check only; this does not validate a robot scene or ROS Bridge.
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
image_ref="${ISAAC_IMAGE:-nvcr.io/nvidia/isaac-sim:6.2.0}"

if [[ "${ACCEPT_EULA:-}" != "Y" ]]; then
  echo 'Set ACCEPT_EULA=Y after reviewing the NVIDIA image license.' >&2
  echo 'See environments/isaac-container.md.' >&2
  exit 2
fi
for tool in docker timeout; do
  command -v "$tool" >/dev/null || { echo "Required tool missing: $tool" >&2; exit 2; }
done
if ! docker image inspect "$image_ref" >/dev/null 2>&1; then
  echo "Image not present. Pull the documented image first: $image_ref" >&2
  exit 2
fi

mkdir -p "$repo_dir/.learning"
run_dir="$(mktemp -d "$repo_dir/.learning/isaac-check.XXXXXX")"
log_file="$run_dir/check.log"
cleanup() {
  if [[ -s "$run_dir/container.cid" ]]; then
    docker rm -f "$(cat "$run_dir/container.cid")" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

docker image inspect "$image_ref" --format '{{.Id}} {{json .RepoDigests}}' > "$run_dir/image.txt"
echo "Compatibility log: $log_file"
set +e
timeout --signal=INT --kill-after=15s 300s docker run --rm --pull=never \
  --cidfile "$run_dir/container.cid" \
  --gpus all --network=host --cap-drop=ALL --security-opt=no-new-privileges \
  --entrypoint bash -e ACCEPT_EULA=Y \
  "$image_ref" ./isaac-sim.compatibility_check.sh --/app/quitAfter=10 --no-window \
  > "$log_file" 2>&1
result=$?
set -e
printf '%s\n' "$result" > "$run_dir/exit-code.txt"
if [[ "$result" -ne 0 ]]; then
  echo "Isaac checker process failed (exit $result). Inspect $log_file" >&2
  exit "$result"
fi
if ! grep -q 'System checking result: PASSED' "$log_file"; then
  echo "Checker exited without a PASSED result. Inspect $log_file" >&2
  exit 1
fi
echo 'PASS: headless compatibility checker. GUI, robot physics and ROS Bridge remain separate checks.'
