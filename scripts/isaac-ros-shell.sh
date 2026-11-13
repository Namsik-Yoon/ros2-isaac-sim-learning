#!/usr/bin/env bash
# External ROS nodes for the running Isaac container; domain remains 42.
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if [[ $# -eq 0 ]]; then set -- bash --noprofile --norc; fi
exec bash "$project_root/scripts/ros-shell.sh" env \
  ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET \
  FASTRTPS_DEFAULT_PROFILES_FILE=/workspaces/ros2-learning/environments/fastdds-udp.xml \
  "$@"
