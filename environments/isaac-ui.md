# Isaac Sim UI 실행과 장면 저장

Isaac Sim 6.2 편집기를 GPU 서버에서 실행하고, 별도의 NVIDIA WebRTC viewer를 브라우저에서 연다. 실습은 브라우저 안의 Isaac Stage·Property·Viewport·Action Graph와 Play·Pause·Stop을 중심으로 진행한다. 설치·시작·진단 명령은 서버에서 한 번 준비한다.

## 현재 검증 범위

검증일: 2026-11-13. 에이전트가 같은 서버에서 실행한 headless Chrome으로 확인한 결과다. 사용자의 다른 PC에서의 접속·조작은 별도 확인 대상이다.

| 항목 | 상태 |
| --- | --- |
| Isaac 6.2 Compatibility Checker | `PASSED`, 종료 코드 0 |
| 편집기 서버 | `Full Streaming App is loaded` 확인 |
| 브라우저 영상 | 같은 서버의 headless Chrome에서 1920×1080 비디오 수신 확인 |
| ROS 내부 런타임 | Jazzy `rclpy` 로드 성공. 실제 ROS 토픽 왕복은 미검증 |
| UI 마우스·키보드 입력 | 파일 탐색·파일명 입력·장면 열기·실행 버튼 조작 확인 |
| 최소 장면의 물리·Play/Pause/Stop | 상자 낙하·바닥 정착, Pause, Stop 시 초기 위치 복원 확인 |
| 다른 PC의 사용자 접속 | 미검증 |
| 주행로봇·ROS 제어 | 미구현·미검증 |



## 서버 준비

Linux에서 동작하는 Docker GPU runtime, `python3`, `setfacl`, 로컬 Isaac 이미지가 필요하다. `setfacl`은 배포판의 `acl` 패키지에 포함된다. 호스트에 Node.js를 설치할 필요는 없다. viewer는 별도 Node 22 컨테이너에서 빌드·실행한다.

처음 준비하는 서버는 [컨테이너 검사](isaac-container.md)를 먼저 진행한다. 이 PC의 Ubuntu 20.04는 공식 지원 OS 목록 밖이며, 현재 실행 성공을 다른 머신의 호환성 보장으로 해석하지 않는다.

저장소 최상위의 `.learning/isaac-ui.env`에 접속 설정을 저장한다. 기존 파일이 있다면 필요한 값만 수정한다. 아래 `192.168.1.100`은 예시이며 **이 서버에 실제 할당된, 접속 PC에서 도달 가능한 LAN IPv4 주소**로 바꾼다.

```bash
ISAACSIM_HOST=192.168.1.100
ISAACSIM_SIGNAL_PORT=49100
ISAACSIM_STREAM_PORT=47998
WEB_VIEWER_PORT=8210
```

이 파일은 Git에서 제외되고 시작 스크립트가 shell 설정으로 읽는다. 주소에는 URL scheme이나 포트를 넣지 않는다. 이 구성은 IPv4만 허용한다.

| 포트 기본값 | 용도 |
| --- | --- |
| TCP 8210 | 브라우저 viewer HTTP 접속 |
| TCP 49100 | WebRTC signaling |
| UDP 47998 | WebRTC 미디어 전송 |

Docker는 host network를 사용한다. 접속 PC에서 세 포트에 도달해야 하며, HTML 페이지만 열리는 상태와 영상이 수신되는 상태를 구분한다. HTTP이며 로그인 기능이 없는 실험용 구성이므로 신뢰하는 LAN에서 사용한다. 인터넷 공개나 인증 게이트웨이는 이 구성의 범위에 포함하지 않는다. Isaac 인스턴스 하나에는 클라이언트 하나만 연결한다. [NVIDIA 스트리밍 안내](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/manual_livestream_clients.html)

## 시작·접속·종료

명령은 저장소 최상위의 서버 터미널에서 실행한다. viewer 최초 준비 시 빌드한다.

```bash
bash scripts/isaac-ui.sh build-viewer
```

[NVIDIA 컨테이너 라이선스 안내](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_container.html)를 확인한 뒤 서버와 viewer를 시작한다.

```bash
ACCEPT_EULA=Y bash scripts/isaac-ui.sh start
bash scripts/isaac-ui.sh status
```

두 컨테이너가 `running`이고 `Full Streaming App is loaded`가 나타날 때까지 기다린다. 프로세스가 `running`인 것만으로 스트림 준비를 판정하지 않는다. 첫 실행의 캐시·셰이더 준비에는 시간이 걸릴 수 있다.

접속 PC의 Chrome/Edge에서 `http://<서버 LAN 주소>:8210`을 연다. `start` 출력에도 실제 URL이 표시된다. 브라우저 탭 하나만 유지하고, 기존 테스트 클라이언트가 연결되어 있다면 먼저 종료한다. 영상이 보이면 UI 안을 클릭해 입력을 전달한다. 브라우저 새로고침은 서버의 장면 초기화와 별개다.

실습을 마칠 때 Isaac UI에서 장면을 저장한 뒤 다음을 실행한다.

```bash
bash scripts/isaac-ui.sh stop
```

이 명령은 프로젝트 이름과 소유 label이 일치하는 서버·viewer 컨테이너만 정지·제거한다. `.learning/isaac-runtime/`의 저장 장면과 캐시는 유지한다. 이미 컨테이너가 있으면 `start`는 덮어쓰지 않고 중단하므로, 재설정 전에 `status`를 확인하고 저장 후 `stop`한다.

`ISAACSIM_HOST`, signaling 또는 stream 포트를 바꾸면 viewer에 컴파일된 접속 주소도 달라져야 한다. 저장·정지 → 설정 수정 → `build-viewer` → `start` 순으로 반영한다. viewer HTTP 포트만 바꾸는 경우에는 설정 변경 후 재시작으로 적용할 수 있다.

## 장면 열기와 보존

첫 장면 원본은 [`sim/scenes/ui-contact-lab.usda`](../sim/scenes/ui-contact-lab.usda)다. Isaac의 파일 열기 대화상자에서 `/workspace/ui-contact-lab.usda`를 연다. 시작 시 최초 사본을 제공하며, 실습 중 저장한 기존 사본은 덮어쓰지 않는다.

| Isaac 컨테이너 경로 | 서버 저장소 경로 | 용도 |
| --- | --- | --- |
| `/workspace/` | `.learning/isaac-runtime/stages/` | UI에서 저장하는 개인 장면, 컨테이너 종료 후 보존 |
| `/workspace/ui-contact-lab.usda` | `.learning/isaac-runtime/stages/ui-contact-lab.usda` | 첫 접촉·낙하 실험용 사본 |
| 원본 fixture | `sim/scenes/ui-contact-lab.usda` | Git에 포함하는 작은 자체 작성 USD |

장면에는 `/World/TestBody` 동적 상자, `/World/Ground` 바닥, `/World/PhysicsScene`, `/World/Overview` 카메라가 있다. 원본의 단위는 미터, 위쪽 축은 Z이며 상자는 높이 1.5 m, 한 변 0.5 m, 질량 1 kg으로 설정했다. 에이전트가 UI에서 낙하·바닥 정착과 Stop 후 초기 위치 복원을 확인했다. 접촉 힘이나 정확한 정착 오차는 측정하지 않았다. [002의 UI 실험](../lessons/002-first-motion.md)에서 높이·collision·실행 상태를 바꾼다.

UI의 Save As로 `/workspace/` 아래에 별도 실험 이름을 저장한다. 서버 캐시나 컨테이너 내부의 다른 임시 위치에 저장한 파일이 모두 보존된다고 가정하지 않는다. 공개 재현용 장면은 사용한 외부 자산 경로를 확인한 뒤 작은 자체 작성 USD와 설정만 `sim/scenes/`에 옮긴다. NVIDIA 원본 자산·캐시·대용량 녹화는 커밋하지 않는다.

## viewer 구성과 진단

[`environments/isaac-viewer/Dockerfile`](isaac-viewer/Dockerfile)은 [NVIDIA 6.2 공식 viewer Dockerfile](https://github.com/isaac-sim/IsaacSim/blob/v6.2.0/tools/docker/web-viewer/Dockerfile)을 바탕으로 한다. Node 22에서 `@nvidia/create-ov-web-rtc-app@2.1.5`와 SDK `@nvidia/ov-web-rtc@6.8.2`를 고정하고, HTTP LAN 접속에서 `crypto.randomUUID`가 없는 경우를 처리한다. NVIDIA SDK의 라이선스는 해당 패키지 조건을 따른다. 베이스 이미지·전이 npm 의존성은 digest/완전한 snapshot으로 고정하지 않았으므로 재빌드 결과가 바뀔 수 있다.

```bash
bash scripts/isaac-ui.sh status
docker logs --tail 100 ros2-isaac-learning-ui
docker logs --tail 100 ros2-isaac-learning-viewer
```

| 증상 | 확인할 항목 |
| --- | --- |
| 시작 전 이미지 없음 오류 | Isaac 이미지 준비 및 viewer 빌드 여부 |
| 캐시·저장 디렉터리 권한 오류 | `setfacl`과 UID 1234 접근, 호스트 파일시스템의 ACL 지원 |
| viewer 페이지만 열리고 영상 없음 | 앱 로드 완료, 컴파일된 서버 주소, signaling·UDP 경로, 다른 연결 클라이언트 |
| 주소 변경 후 이전 서버로 연결 | viewer 재빌드와 컨테이너 재시작 여부 |
| 화면은 보이지만 로봇 토픽 없음 | 장면·ROS 그래프·Play 상태·Domain ID·QoS. 영상 수신으로 ROS 연결을 판정하지 않음 |

서버의 ROS 기본 설정은 Jazzy·Fast DDS·Domain 42다. 내부 런타임 로드 성공과 외부 ROS 컨테이너와의 실제 토픽 왕복은 별도이며, 후자는 주행 그래프 구성 단계에서 검증한다. OS·GPU 드라이버·방화벽 설정은 이 스크립트가 변경하지 않는다.
