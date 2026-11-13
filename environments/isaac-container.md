# Isaac Sim 컨테이너 실행 검사

기준 버전은 `nvcr.io/nvidia/isaac-sim:6.2.0`이다. 현재 Ubuntu 20.04 호스트는 공식 지원 OS 목록 밖이지만, 설치되어 있는 NVIDIA Container Toolkit을 이용해 실제 실행 가능성을 검사한다. 검사 통과가 호스트 공식 지원이나 로봇 장면·ROS Bridge 검증을 뜻하지는 않는다.

## 현재 확인한 범위

- 기존 ROS 이미지에 GPU를 전달해 `nvidia-smi` 실행 성공.
- Isaac 6.2 headless Compatibility Checker에서 Vulkan GPU 인식, `PASSED`, 종료 코드 0 확인.
- 후속 UI 서버에서 `Full Streaming App is loaded`와 같은 서버의 headless Chrome에서 1920×1080 비디오 수신 확인. 호스트 DISPLAY 없이 WebRTC로 편집기 화면을 전달한다.
- 내부 Jazzy `rclpy` 로드 성공. UI 입력·장면 물리·다른 PC 접속·외부 ROS와 실제 토픽 왕복은 검증 범위를 구분한다. 최신 결과는 [UI 실행 안내](isaac-ui.md)에 기록한다.
- 드라이버·OS 변경 없이 컨테이너로 검사한다. `/mnt` 등 데이터 경로는 실제 mount 상태를 확인한 후 선택한다.

## 이미지와 검사

호스트 저장소 최상위에서 실행한다. 처음 이미지 다운로드가 필요하며, 확인 당시 amd64 압축 레이어는 약 9.92 GiB였다. 압축 해제·캐시·자산 공간은 별도다.

```bash
docker pull nvcr.io/nvidia/isaac-sim:6.2.0
ACCEPT_EULA=Y bash scripts/check-isaac.sh
```

`ACCEPT_EULA=Y`는 NVIDIA 이미지 라이선스 동의를 뜻한다. 실행 전에 [공식 컨테이너 설치 문서의 라이선스 안내](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_container.html)를 확인한다. 선택적 데이터 수집 변수 `PRIVACY_CONSENT`는 설정하지 않는다.

검사 스크립트는 자동 다운로드를 하지 않는다. 5분 제한을 두고 자체 임시 컨테이너만 종료하며, 로그·이미지 ID·종료 코드를 Git 제외 `.learning/isaac-check.*/`에 남긴다. 최초 검사는 호스트 캐시나 프로젝트를 컨테이너에 마운트하지 않는다.

프로세스 종료 코드와 `System checking result: PASSED` 출력이 모두 있어야 검사 통과다. 실패 시 원문에서 OS·GPU·드라이버·Vulkan·렌더러 중 실패한 항목을 확인한다. 실제 사용한 이미지 ID/digest는 실행별 `image.txt`에 기록한다. 특정 이미지를 재현하려면 `ISAAC_IMAGE`로 로컬에 준비한 digest 참조를 지정할 수 있다.

## UI 실행으로 이어가기

Compatibility Checker와 같은 서버의 브라우저 영상 수신을 확인했다. 실제 실습은 [UI 실행 안내](isaac-ui.md)에 따라 편집기에 접속해 진행한다. 이 안내에서 WebRTC 포트, 캐시 권한, 시작·종료, 저장 장면 경로를 명시한다. 최소 물리 장면의 입력·실행, 사용자 PC 접속, ROS 왕복과 주행 제어는 각각의 결과를 [검증 기록](validation.md)에 추가한다.

공식 참고: [시스템 요구사항](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/requirements.html), [컨테이너 설치](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_container.html), [WebRTC 클라이언트](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/manual_livestream_clients.html).
