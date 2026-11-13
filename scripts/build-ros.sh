#!/usr/bin/env bash
# Build only this project's ROS CLI image; do not change host packages.
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
image_tag=ros2-learning:jazzy
command -v docker >/dev/null || { echo 'Docker가 필요합니다.' >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo 'Docker daemon 연결을 확인하세요.' >&2; exit 1; }
docker build --tag "$image_tag" --file "$project_root/environments/ros-jazzy/Dockerfile" "$project_root"
mkdir -p "$project_root/.learning"
docker image inspect "$image_tag" --format '{{.Id}}' > "$project_root/.learning/ros-image-id.txt"
docker run --rm "$image_tag" dpkg-query -W '-f=${Package}\t${Version}\n' > "$project_root/.learning/ros-packages.tsv"
echo 'ROS 기초 이미지 준비 완료. 다음: bash scripts/check-ros.sh'
