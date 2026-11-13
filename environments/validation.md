# 초기 환경 검증 기록

검증일: 2026-11-13 (Asia/Seoul). 아래 작업은 에이전트가 환경 준비 과정에서 수행했다. 학습자의 실습·이해 완료 기록이 아니다.

## 확인한 결과

| 검사 | 결과 |
| --- | --- |
| 진단 도구 단위 테스트 | 14개 통과 |
| 호스트 환경 수집 | 정상, 개인 `.learning/environment.json`에 저장 |
| ROS Docker 이미지 빌드 | 성공 |
| 컨테이너 OS / Python | Ubuntu 24.04.5 / Python 3.12.3 |
| ROS 배포판 / 통신 설정 | Jazzy / Fast DDS / domain 42 / LOCALHOST |
| 별도 컨테이너 간 실제 송수신 | `Hello World: 0` 수신 확인 |
| 대화형 셸 진입·ROS 접근·종료 | 확인 |
| 실행 사용자 | 호스트 UID/GID로 실행 |
| NVIDIA Container Toolkit / Docker GPU 전달 | 기존 런타임에서 ROS 이미지의 `nvidia-smi` 실행 성공, RTX 3090 Ti 확인 |
| Isaac Sim 6.2 이미지 / Compatibility Checker | 이미지 준비 완료, headless 검사 `PASSED`, 프로세스 exit 0 |
| Isaac Sim 편집기 서버 | `Full Streaming App is loaded` 확인 |
| Isaac Sim 브라우저 영상 | 같은 서버의 headless Chrome에서 1920×1080 비디오 수신 확인 |
| Isaac Sim UI 입력·최소 물리 장면 | 파일 열기·키보드 입력, 상자 낙하·바닥 정착·Pause·Stop 초기 위치 복원 확인 |
| 다른 PC의 사용자 접속 | 아직 검증하지 않음 |
| Isaac 내부 ROS 런타임 | Jazzy `rclpy` 로드 성공 |
| 외부 ROS 토픽 왕복·주행 제어 | 아직 검증하지 않음 |
| 드론 환경 | 조사 단계, 아직 설치·검증하지 않음 |

기본 이미지 digest는 Dockerfile에 고정되어 있다. 이번 빌드의 주요 추가 패키지는 `ros-jazzy-demo-nodes-py=0.33.11-1noble.20260912.164047`, `ros-jazzy-example-interfaces=0.12.1-1noble.20260911.054159`이다. 전체 목록과 최종 이미지 ID는 개인 `.learning/`에 보관한다. APT 저장소 snapshot은 고정하지 않았다.

현재 PC에서의 실행 확인이다. 다른 GPU·OS나 새로 설치한 PC에서의 재현 검증을 의미하지 않는다. ROS 통신 확인은 Isaac Sim 호환성을 보증하지 않는다.

## 다시 검사하기

```bash
python3 -m unittest discover -s tests -v
python3 scripts/doctor.py --json --output .learning/environment.json
bash scripts/check-ros.sh
```

진단 도구의 종료 코드 0은 정보 수집 완료를 뜻한다. Isaac 준비 여부는 보고서의 별도 항목과 실제 Compatibility Checker 결과를 함께 확인한다.

## Isaac 컨테이너 검사 결과

`ACCEPT_EULA=Y bash scripts/check-isaac.sh`로 실행했다. RTX 3090 Ti와 드라이버 580.126.09가 인식됐고 Vulkan GPU 초기화 후 `System checking result: PASSED`, 종료 코드 0을 확인했다. 검사용 임시 컨테이너는 종료 후 삭제했다.

이미지: `nvcr.io/nvidia/isaac-sim:6.2.0`, 배포 digest: `sha256:a025b65a7442d56806a1cc3f5eed081caf736c24b72d62dccf68ef66945d8690`. 실행별 이미지 ID·원문 로그는 개인 `.learning/isaac-check.*/`에 기록했다.

검사에 표시된 Ubuntu 24.04.3은 컨테이너 환경이다. 호스트 Ubuntu 20.04의 공식 지원을 뜻하지 않는다. 검사 도구의 최소치·용량 집계는 설치 요구사항이나 실제 호스트 파일시스템 여유 공간을 대체하지 않는다. 후속 브라우저 영상 검증은 아래에 별도 기록한다.

검사 로그에 OmniHub 자식 프로세스 시작 실패 경고가 있었으나 검사는 정상 완료했다. 자산 로딩 단계에서 재현 여부를 확인한다. 현재 CPU governor 경고와 display 없음도 기록했으며 호스트 설정은 바꾸지 않았다.

## Isaac UI 스트리밍

[`scripts/isaac-ui.sh`](../scripts/isaac-ui.sh)로 Isaac 6.2 서버와 별도 Node 22 기반 NVIDIA viewer를 실행했다. 공식 viewer 생성기 버전은 `@nvidia/create-ov-web-rtc-app@2.1.5`이며, SDK는 `@nvidia/ov-web-rtc@6.8.2`로 고정했다. LAN HTTP에서 `crypto.randomUUID`가 없는 경우를 처리하도록 수정한 뒤 재빌드했다. 서버의 `Full Streaming App is loaded`와 같은 서버의 headless Chrome에서 1920×1080 비디오 수신을 확인했다.

브라우저에서 파일 탐색·파일명 입력으로 `/workspace/ui-contact-lab.usda`를 열고, Play로 상자 낙하·바닥 정착을 관찰했다. Pause 후 정지 화면과 Stop 후 초기 위치 복원을 확인했다. 접촉 힘·정확한 정착 오차는 측정하지 않았다. 원본 USD와 개인 사본을 분리하며, 검증 화면은 개인 `.learning/isaac-contact-*.png`에 보관했다. 다른 PC의 네트워크 경로와 사용자의 직접 조작은 아직 확인하지 않았다. 내부 Jazzy `rclpy`가 로드됐지만 외부 ROS 노드와의 토픽 왕복·주행 그래프는 아직 검증하지 않았다. 접속·저장·진단 방법은 [UI 실행 안내](isaac-ui.md)를 따른다.

검증 중 중복 브라우저 연결에서 `NVST_R_BUSY`를 관찰했고, 검증 클라이언트를 정리한 뒤 단일 연결로 확인했다. headless 서버의 GLFW 창 초기화 경고가 남았으나 위 UI·물리 조작은 동작했다. 외부 NVIDIA 자산 로딩은 이번 최소 장면에서 시험하지 않았다.
