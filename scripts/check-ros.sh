#!/usr/bin/env bash
# Infrastructure check only: it never updates the learner's lesson status.
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
command -v timeout >/dev/null || { echo 'GNU timeout이 필요합니다.' >&2; exit 1; }
check_dir=$(mktemp -d "${TMPDIR:-/tmp}/ros2-check.XXXXXXXXXX")
check_token=${check_dir##*/}
check_token=${check_token//[^a-zA-Z0-9_]/_}
check_topic="/setup_${check_token}"
talker_pid=''
cleanup() {
  for cid_file in "$check_dir/talker.cid" "$check_dir/listener.cid"; do
    if [[ -s $cid_file ]]; then
      container_id=$(cat "$cid_file")
      if [[ $container_id =~ ^[0-9a-f]{64}$ ]]; then
        timeout --kill-after=2s 5s docker stop --time 2 "$container_id" >/dev/null 2>&1 || true
      fi
    fi
  done
  if [[ -n $talker_pid ]]; then
    kill -TERM "$talker_pid" 2>/dev/null || true
    wait "$talker_pid" 2>/dev/null || true
  fi
  rm -rf -- "$check_dir"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
ROS2_CONTAINER_CIDFILE="$check_dir/talker.cid" timeout --kill-after=3s 40s bash "$project_root/scripts/ros-shell.sh" \
  ros2 run demo_nodes_py talker --ros-args -r "chatter:=$check_topic" \
  > "$check_dir/talker.log" 2>&1 &
talker_pid=$!
if ! ROS2_CONTAINER_CIDFILE="$check_dir/listener.cid" timeout --kill-after=3s 25s bash "$project_root/scripts/ros-shell.sh" \
  ros2 topic echo "$check_topic" std_msgs/msg/String --once > "$check_dir/listener.log" 2>&1; then
  cat "$check_dir/talker.log" "$check_dir/listener.log" >&2
  echo 'ROS 컨테이너 간 통신 확인 실패. environments/README.md를 확인하세요.' >&2
  exit 1
fi
if ! python3 -c 'import pathlib,sys; sys.exit(0 if "Hello World:" in pathlib.Path(sys.argv[1]).read_text() else 1)' "$check_dir/listener.log"; then
  cat "$check_dir/listener.log" >&2
  echo '예상 메시지를 받지 못했습니다.' >&2
  exit 1
fi
cat "$check_dir/listener.log"
echo 'PASS: 서로 다른 ROS 컨테이너 사이에서 발행한 메시지를 수신했습니다.'
echo '이 결과는 환경 검증이며 학습자의 실습/이해 완료를 의미하지 않습니다.'
