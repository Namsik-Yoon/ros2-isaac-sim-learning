#!/usr/bin/env bash
# Start the Isaac editor stream and NVIDIA browser viewer on a trusted network.
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
runtime_dir="$repo_dir/.learning/isaac-runtime"
server_name=ros2-isaac-learning-ui
viewer_name=ros2-isaac-learning-viewer
image_ref=nvcr.io/nvidia/isaac-sim:6.2.0
viewer_image=ros2-isaac-viewer:6.2.0

if [[ -f "$repo_dir/.learning/isaac-ui.env" ]]; then
  # This is a local, Git-ignored configuration created by the operator.
  source "$repo_dir/.learning/isaac-ui.env"
fi
ISAACSIM_SIGNAL_PORT="${ISAACSIM_SIGNAL_PORT:-49100}"
ISAACSIM_STREAM_PORT="${ISAACSIM_STREAM_PORT:-47998}"
WEB_VIEWER_PORT="${WEB_VIEWER_PORT:-8210}"

exists() { docker inspect "$1" >/dev/null 2>&1; }
owned() {
  [[ "$(docker inspect --format '{{index .Config.Labels "ros2-learning.component"}}' "$1")" == "$2" ]] || {
    echo "Container name belongs to another workload: $1" >&2; exit 2;
  }
}
stop_one() {
  if exists "$1"; then
    owned "$1" "$2"
    docker stop --time 20 "$1" >/dev/null
    docker rm "$1" >/dev/null
  fi
}
validate_config() {
  : "${ISAACSIM_HOST:?Set ISAACSIM_HOST to a reachable IPv4 address on this host.}"
  python3 - "$ISAACSIM_HOST" "$ISAACSIM_SIGNAL_PORT" "$ISAACSIM_STREAM_PORT" "$WEB_VIEWER_PORT" <<'PY'
import ipaddress, sys
ipaddress.IPv4Address(sys.argv[1])
ports = [int(v) for v in sys.argv[2:]]
if any(p < 1024 or p > 65535 for p in ports) or len(set(ports)) != len(ports):
    raise SystemExit('Use distinct unprivileged ports between 1024 and 65535.')
PY
}
prepare_dirs() {
  command -v setfacl >/dev/null || { echo 'setfacl is required for UID 1234 cache access.' >&2; exit 2; }
  local owner_uid
  owner_uid="$(id -u)"
  for rel in cache/main cache/computecache cache/kit logs config data pkg hub stages; do
    mkdir -p "$runtime_dir/$rel"
    setfacl -m u:1234:rwx "$runtime_dir/$rel"
    setfacl -d -m "u:1234:rwx,u:$owner_uid:rwx" "$runtime_dir/$rel"
  done
  # Seed the UI fixture once; preserve scenes the operator has already edited.
  if [[ ! -e "$runtime_dir/stages/ui-contact-lab.usda" ]]; then
    cp "$repo_dir/sim/scenes/ui-contact-lab.usda" "$runtime_dir/stages/ui-contact-lab.usda"
  fi
}

case "${1:-status}" in
  build-viewer)
    validate_config
    docker build --network=host \
      --build-arg "ISAACSIM_HOST=$ISAACSIM_HOST" \
      --build-arg "ISAACSIM_SIGNAL_PORT=$ISAACSIM_SIGNAL_PORT" \
      --build-arg "ISAACSIM_STREAM_PORT=$ISAACSIM_STREAM_PORT" \
      -t "$viewer_image" "$repo_dir/environments/isaac-viewer"
    ;;
  start)
    validate_config
    [[ "${ACCEPT_EULA:-}" == Y ]] || { echo 'Set ACCEPT_EULA=Y after reviewing the NVIDIA license.' >&2; exit 2; }
    docker image inspect "$image_ref" "$viewer_image" >/dev/null
    prepare_dirs
    if exists "$server_name"; then
      owned "$server_name" isaac-ui
      echo 'Server container exists. Use status; stop before reconfiguring.' >&2
      exit 2
    fi
    if exists "$viewer_name"; then
      owned "$viewer_name" isaac-viewer
      echo 'Viewer container exists. Inspect status before changing it.' >&2
      exit 2
    fi
    docker run -d --name "$server_name" --label ros2-learning.component=isaac-ui \
      --pull=never --gpus all --network=host --user 1234:1234 \
      --cap-drop=ALL --security-opt=no-new-privileges \
      -e ACCEPT_EULA=Y -e NVIDIA_DRIVER_CAPABILITIES=all \
      -e ISAACSIM_PHYSICS_ENGINE=physx -e "ISAACSIM_HOST=$ISAACSIM_HOST" \
      -e "ISAACSIM_SIGNAL_PORT=$ISAACSIM_SIGNAL_PORT" -e "ISAACSIM_STREAM_PORT=$ISAACSIM_STREAM_PORT" \
      -e ROS_DOMAIN_ID=42 -e ROS_DISTRO=jazzy -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
      -e LD_LIBRARY_PATH=/isaac-sim/exts/isaacsim.ros2.core/jazzy/lib \
      --mount "type=bind,source=$runtime_dir/cache/main,target=/isaac-sim/.cache" \
      --mount "type=bind,source=$runtime_dir/cache/computecache,target=/isaac-sim/.nv/ComputeCache" \
      --mount "type=bind,source=$runtime_dir/cache/kit,target=/isaac-sim/kit/cache" \
      --mount "type=bind,source=$runtime_dir/logs,target=/isaac-sim/.nvidia-omniverse/logs" \
      --mount "type=bind,source=$runtime_dir/config,target=/isaac-sim/.nvidia-omniverse/config" \
      --mount "type=bind,source=$runtime_dir/data,target=/isaac-sim/.local/share/ov/data" \
      --mount "type=bind,source=$runtime_dir/pkg,target=/isaac-sim/.local/share/ov/pkg" \
      --mount "type=bind,source=$runtime_dir/hub,target=/var/cache/hub" \
      --mount "type=bind,source=$runtime_dir/stages,target=/workspace" \
      "$image_ref"
    docker run -d --name "$viewer_name" --label ros2-learning.component=isaac-viewer \
      --pull=never --network=host --cap-drop=ALL --security-opt=no-new-privileges \
      "$viewer_image" --host "$ISAACSIM_HOST" --port "$WEB_VIEWER_PORT"
    echo "Viewer: http://$ISAACSIM_HOST:$WEB_VIEWER_PORT (wait for the editor to load)"
    ;;
  stop)
    stop_one "$viewer_name" isaac-viewer
    stop_one "$server_name" isaac-ui
    echo 'Stopped. Saved stages and cache remain in .learning/isaac-runtime/.'
    ;;
  status)
    for name in "$server_name" "$viewer_name"; do
      if exists "$name"; then
        docker inspect --format '{{.Name}} {{.State.Status}}' "$name"
      else
        echo "$name: not created"
      fi
    done
    if exists "$server_name"; then
      owned "$server_name" isaac-ui
      docker logs "$server_name" 2>&1 | grep -E ' App is loaded[.]$|ROS2 Bridge startup failed' | tail -n 5 || true
    fi
    ;;
  *) echo 'Usage: bash scripts/isaac-ui.sh {build-viewer|start|status|stop}' >&2; exit 2 ;;
esac
