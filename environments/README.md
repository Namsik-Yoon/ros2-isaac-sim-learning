# 실행 환경

확인 기준일: 2026-11-13 (Asia/Seoul). 현재 상태와 아직 검증하지 않은 후보를 구분합니다.

## A. ROS 2 개발 환경 — 설치·통신 검증 완료

- 호스트: Ubuntu 20.04 x86_64, Docker 28.1.1.
- 컨테이너: Ubuntu 24.04 Noble, ROS 2 Jazzy, Python 3.12 계열.
- 공식 `ros:jazzy-ros-base` 이미지 digest는 [Dockerfile](ros-jazzy/Dockerfile)에 고정했습니다.
- `demo_nodes_py`를 추가합니다. 기본 이미지 digest는 고정했지만 추가 APT 패키지 저장소는 snapshot으로 고정하지 않았으므로 재빌드 시 패키지 버전이 달라질 수 있습니다.
- 실제 빌드의 이미지 ID와 전체 패키지 목록은 `.learning/ros-image-id.txt`, `.learning/ros-packages.tsv`에 저장합니다.

```bash
bash scripts/build-ros.sh
bash scripts/check-ros.sh
bash scripts/ros-shell.sh
```

위 명령은 저장소 최상위에서 실행합니다. 셸을 여러 개 열면 각각 별도 임시 컨테이너를 사용합니다. 모두 `ROS_DOMAIN_ID=42`, `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`, Fast DDS를 사용합니다. Linux의 host network와 IPC를 공유해 같은 PC 내 통신을 맞춥니다. 이 설정은 여러 PC 통신이나 GPU/GUI 실행용 설정이 아닙니다. 동일 PC의 다른 ROS 작업이 domain 42를 쓰면 서로 보일 수 있으므로 그때는 프로젝트 설정을 함께 조정합니다.

컨테이너는 호스트 사용자 UID/GID로 실행하고 저장소만 `/workspaces/ros2-learning`에 연결합니다. 이 경로에 쓰는 파일은 호스트에도 남습니다. 그 외 컨테이너 내부에서 설치/수정한 내용은 종료하면 없어집니다. 필요한 의존성은 Dockerfile에 추가해 다시 빌드합니다. 개인 `.learning/`은 Docker 빌드 컨텍스트에서 제외합니다.

표준 ROS 환경은 컨테이너 진입 시 준비됩니다. 나중에 자기 패키지를 빌드하면 해당 셸에서 `source ros2_ws/install/setup.bash`도 실행합니다. 이미지의 Python과 호스트 Python을 혼용하지 않습니다.

통신 확인은 `check-ros.sh`의 PASS 출력으로 판단합니다. 실제 최종 검증 기록은 [검증 기록](validation.md)에 남깁니다. 수업 실행·이해도는 별도입니다.

## B. Isaac Sim UI — 직접 바퀴 구동 확인, ROS 명령 수신 확인

후보 조합은 Ubuntu 24.04 + ROS 2 Jazzy + Isaac Sim 6.2.0입니다. ROS workspace가 필요하면 `IsaacSim-6.2.0` 태그에 맞춥니다. [NVIDIA 공식 ROS 설치 안내](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_ros.html)

현재 호스트 Ubuntu 20.04는 이 Isaac Sim 지원 OS 목록에 없습니다. Ubuntu 24.04가 들어 있는 ROS 컨테이너만으로 호스트 그래픽·드라이버·GUI 조건이 충족되는 것은 아닙니다. [시스템 요구사항](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/requirements.html)

현재 GPU는 RTX 3090 Ti 24GB, RAM은 약 128GB입니다. 버전별 GPU 지원은 Compatibility Checker와 작은 장면으로 확인합니다. 드라이버 580.126.09를 무조건 바꿔야 한다고 판정하지 않습니다. 공식 시스템 표의 드라이버는 검증 버전이며 [Omniverse 기술 요구사항](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html)도 함께 확인합니다.

스토리지는 공식 50GB SSD 참고치와 별도로 캐시·빌드용 여유 100GiB 이상을 프로젝트 권장치로 둡니다. 최초 진단과 달리 최신 확인에서는 `/mnt`가 별도 마운트가 아니라 루트 파일시스템을 가리킵니다. 과거 데이터 디스크의 여유 용량을 현재 사용 가능 공간으로 계산하지 않습니다. 실시간 용량과 mount 상태를 확인합니다.

지원 OS로 이전하는 경로는 [이전 검토 문서](ubuntu-migration.md)에 남겨둡니다. 현재 NVIDIA Container Toolkit 1.17.8과 Docker GPU runtime가 이미 설치되어 있고, 기존 ROS 이미지의 GPU 접근을 실제 검증했습니다. [Isaac 컨테이너 실행 검사](isaac-container.md)도 실제로 실행해 `PASSED`와 종료 코드 0을 확인했습니다. 이미지는 설치됐으며 결과와 한계는 [검증 기록](validation.md)에 남겼습니다. Ubuntu 20.04 공식 지원과 이 PC에서의 실제 구동 여부는 구분합니다. OS·파티션·드라이버 변경은 수행하지 않았습니다.

Isaac 6.2 편집기와 별도 Node 22 기반 NVIDIA WebRTC viewer를 실행했습니다. 같은 서버의 headless Chrome에서 1920×1080 비디오 수신을 확인했습니다. 서버의 `Full Streaming App is loaded`와 내부 Jazzy `rclpy` 로드도 확인했습니다. 같은 브라우저에서 장면 파일을 열고 상자 낙하·바닥 정착·Pause·Stop 초기 위치 복원을 확인했습니다. 다른 PC의 Chrome/Edge에서 사용자 화면 표시도 확인했습니다. 최초 `Waiting for stream` 고착은 서버 재시작 후 복구됐습니다. 이후 외부 ROS의 `/cmd_vel` 수신 ACK와 사용자가 관찰한 전진·정지를 확인했습니다. Odometry·clock 발행과 폐루프 주행은 별도 검증 대상입니다. UI 입력·물리의 최신 상태는 [UI 실행 안내](isaac-ui.md)와 [검증 기록](validation.md)에 기록합니다.

브라우저 접속, 시작·종료, 포트 설정과 저장 장면 경로는 [UI 실행 안내](isaac-ui.md)를 따릅니다. 장면은 컨테이너 `/workspace`와 연결된 `.learning/isaac-runtime/stages/`에 보존합니다. 호스트 DISPLAY 없이 서버 편집기를 스트리밍하며, 장면의 ROS 도메인 42, 시간·좌표·QoS 계약은 실제 연결에서 기록합니다. 영상 수신 성공과 ROS 제어 성공을 구분합니다.

### 외부 ROS 노드에서 Isaac에 연결

Isaac 주행 명령에는 아래 셸을 사용합니다. 기본 `ros-shell.sh`의 로컬 ROS 컨테이너 실험 설정은 유지합니다.

```bash
bash scripts/isaac-ros-shell.sh
```

[isaac-ros-shell.sh](../scripts/isaac-ros-shell.sh)는 기존 ROS 이미지와 domain `42`를 사용하며, 외부 노드에 `ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET`과 [UDP 전송 프로필](fastdds-udp.xml)을 적용합니다. DDS 발견 범위가 같은 subnet으로 넓어지므로 동일 domain의 다른 ROS 노드도 발견 대상입니다. [NVIDIA의 컨테이너용 Fast DDS UDP 안내](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_ros.html)를 참고했습니다.

실제 비교: `LOCALHOST` 기본 설정에서는 `/cmd_vel` 구독자 발견에 성공했지만 reliable 메시지 ACK를 받지 못했습니다. UDP 프로필만 추가하고 `LOCALHOST`를 유지해도 실패했습니다. 외부 노드에 **UDP + SUBNET**을 함께 적용한 뒤 초기 0 속도와 최종 0 속도 메시지 ACK를 받았고, 중간에 전진 `0.05 m/s`를 2초 발행했습니다. Isaac 서버는 재시작하거나 IPC 설정을 변경하지 않았습니다. 이 비교만으로 공유 메모리와 discovery 설정 중 단일 원인을 확정하지 않습니다.

ACK는 DDS 수신 확인이며 UI의 실제 움직임·odometry 검증을 대신하지 않습니다. 시각적 주행 결과는 사용자 관찰과 대조합니다. 전체 절차는 [ROS 주행 그래프](../lessons/002-ros-drive-graph.md)에 있습니다.

## C. 드론 — 호환성 조사 단계

Pegasus 문서의 검증 조합은 Isaac Sim 5.1.0 + Ubuntu 22.04 + PX4 1.14.3입니다. 6.2와의 호환성은 확인되지 않았으며 5.1은 NVIDIA 문서에서 지원 종료로 표시됩니다. 주행 환경 전체를 이 조합에 맞추지 않고, 드론 단원 전에 버전·확장·비행 제어기 조합을 다시 검증합니다.

- [Pegasus 설치 안내](https://pegasussimulator.github.io/PegasusSimulator/source/setup/installation.html)
- [Isaac Sim 5.1 요구사항/지원 상태](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html)
- [PX4 ROS 2 안내](https://docs.px4.io/main/en/ros2/user_guide)
- [ROS 공식 Dockerfile](https://github.com/osrf/docker_images/blob/master/ros/jazzy/ubuntu/noble/ros-base/Dockerfile)

## 진단과 복구

`python3 scripts/doctor.py`는 기본적으로 읽기 전용입니다. `--json --output .learning/environment.json`을 주면 해당 개인 파일에 저장합니다. 도구가 없거나 사양이 부족해도 수집이 끝나면 종료 코드 0이므로, readiness 항목을 읽어야 합니다. 출력 오류는 1, 잘못된 인자는 2입니다.

이미지가 없으면 build 스크립트를 다시 실행합니다. ROS 통신이 안 되면 도메인·토픽·두 프로세스의 실행 상태부터 확인합니다. 다른 프로젝트의 Docker 이미지/컨테이너를 지우는 정리 명령은 사용하지 않습니다.
