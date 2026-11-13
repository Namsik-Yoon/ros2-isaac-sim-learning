# Official ROS Jazzy base, resolved on 2026-11-13. Ubuntu Noble is inside the image.
FROM ros:jazzy-ros-base@sha256:00b8d47a6e6384a2834e3d01fa87ae767876543baa574f2d64a75c04ea33c698

RUN apt-get update \
    && apt-get install -y --no-install-recommends ros-jazzy-demo-nodes-py \
    && rm -rf /var/lib/apt/lists/*

ENV ROS_DOMAIN_ID=42 \
    ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
    ROS_HOME=/tmp/ros2-learning \
    RMW_IMPLEMENTATION=rmw_fastrtps_cpp

WORKDIR /workspaces/ros2-learning
CMD ["bash", "--noprofile", "--norc"]
