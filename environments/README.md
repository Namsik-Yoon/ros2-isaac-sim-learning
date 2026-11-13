# 실행 환경

확인 기준일: 2026-11-13 (Asia/Seoul). 현재 상태와 아직 검증하지 않은 후보를 구분합니다.

## A. ROS 2 기초 실습 — 설치 완료, 통신 시험 결과는 아래 기록

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

## B. Isaac Sim 주행 — 설치 전

후보 조합은 Ubuntu 24.04 + ROS 2 Jazzy + Isaac Sim 6.2.0입니다. ROS workspace가 필요하면 `IsaacSim-6.2.0` 태그에 맞춥니다. [NVIDIA 공식 ROS 설치 안내](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_ros.html)

현재 호스트 Ubuntu 20.04는 이 Isaac Sim 지원 OS 목록에 없습니다. Ubuntu 24.04가 들어 있는 ROS 컨테이너만으로 호스트 그래픽·드라이버·GUI 조건이 충족되는 것은 아닙니다. [시스템 요구사항](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/requirements.html)

현재 GPU는 RTX 3090 Ti 24GB, RAM은 약 128GB입니다. 버전별 GPU 지원은 Compatibility Checker와 작은 장면으로 확인합니다. 드라이버 580.126.09를 무조건 바꿔야 한다고 판정하지 않습니다. 공식 시스템 표의 드라이버는 검증 버전이며 [Omniverse 기술 요구사항](https://docs.omniverse.nvidia.com/dev-guide/latest/common/technical-requirements.html)도 함께 확인합니다.

스토리지는 공식 50GB SSD 참고치와 별도로 캐시·빌드용 여유 100GiB 이상을 프로젝트 권장치로 둡니다. `/mnt`에는 별도 파일시스템의 넉넉한 여유 공간이 확인되었으나, 이것은 Ubuntu 24.04가 설치되었다는 뜻이 아닙니다. 실시간 용량은 `doctor.py`로 확인합니다.

사용자는 현재 PC의 Ubuntu 이전을 검토할 수 있다고 답했습니다. [이전 검토 문서](ubuntu-migration.md)에 방법·백업·부팅 준비 항목을 정리했습니다. 현재 `/mnt`에는 기존 데이터가 있으므로 이를 빈 설치 디스크로 취급하지 않습니다. 아직 OS·파티션·드라이버 변경은 수행하지 않았습니다.

지원 환경 준비 후 Compatibility Checker → 작은 장면 → ROS Bridge → `/cmd_vel` 주행 순으로 검증합니다. 장면의 ROS 도메인을 42로 맞추는 것도 해당 단계에서 기록합니다.

## C. 드론 — 호환성 조사 단계

Pegasus 문서의 검증 조합은 Isaac Sim 5.1.0 + Ubuntu 22.04 + PX4 1.14.3입니다. 6.2와의 호환성은 확인되지 않았으며 5.1은 NVIDIA 문서에서 지원 종료로 표시됩니다. 주행 환경 전체를 이 조합에 맞추지 않고, 드론 단원 전에 버전·확장·비행 제어기 조합을 다시 검증합니다.

- [Pegasus 설치 안내](https://pegasussimulator.github.io/PegasusSimulator/source/setup/installation.html)
- [Isaac Sim 5.1 요구사항/지원 상태](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/requirements.html)
- [PX4 ROS 2 안내](https://docs.px4.io/main/en/ros2/user_guide)
- [ROS 공식 Dockerfile](https://github.com/osrf/docker_images/blob/master/ros/jazzy/ubuntu/noble/ros-base/Dockerfile)

## 진단과 복구

`python3 scripts/doctor.py`는 기본적으로 읽기 전용입니다. `--json --output .learning/environment.json`을 주면 해당 개인 파일에 저장합니다. 도구가 없거나 사양이 부족해도 수집이 끝나면 종료 코드 0이므로, readiness 항목을 읽어야 합니다. 출력 오류는 1, 잘못된 인자는 2입니다.

이미지가 없으면 build 스크립트를 다시 실행합니다. ROS 통신이 안 되면 도메인·토픽·두 프로세스의 실행 상태부터 확인합니다. 다른 프로젝트의 Docker 이미지/컨테이너를 지우는 정리 명령은 사용하지 않습니다.
