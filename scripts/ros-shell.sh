#!/usr/bin/env bash
# Each terminal gets a disposable container sharing Linux loopback and DDS IPC.
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
image_tag=ros2-learning:jazzy
if [[ $(uname -s) != Linux ]]; then
  echo '이 스크립트는 Linux Docker용입니다. environments/README.md를 확인하세요.' >&2
  exit 1
fi
command -v docker >/dev/null || { echo 'Docker가 필요합니다.' >&2; exit 1; }
docker image inspect "$image_tag" >/dev/null 2>&1 || {
  echo '먼저 bash scripts/build-ros.sh 를 실행하세요.' >&2
  exit 1
}
run_args=(--rm --init --network host --ipc host
  --user "$(id -u):$(id -g)" --cap-drop ALL --security-opt no-new-privileges
  --env ROS_DOMAIN_ID=42 --env ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
  --env ROS_HOME=/tmp/ros2-learning --env RMW_IMPLEMENTATION=rmw_fastrtps_cpp
  --mount "type=bind,source=$project_root,target=/workspaces/ros2-learning"
  --workdir /workspaces/ros2-learning)
if [[ -t 0 && -t 1 ]]; then run_args+=(-it); fi
# Used by the environment check to clean up only containers it actually created.
if [[ -n ${ROS2_CONTAINER_CIDFILE:-} ]]; then run_args+=(--cidfile "$ROS2_CONTAINER_CIDFILE"); fi
if [[ $# -eq 0 ]]; then set -- bash --noprofile --norc; fi
exec docker run "${run_args[@]}" "$image_tag" "$@"
