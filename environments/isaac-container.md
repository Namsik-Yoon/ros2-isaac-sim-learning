# Isaac Sim 컨테이너 실행 검사

기준 버전은 `nvcr.io/nvidia/isaac-sim:6.2.0`이다. 현재 Ubuntu 20.04 호스트는 공식 지원 OS 목록 밖이지만, 설치되어 있는 NVIDIA Container Toolkit을 이용해 실제 실행 가능성을 검사한다. 검사 통과가 호스트 공식 지원이나 로봇 장면·ROS Bridge 검증을 뜻하지는 않는다.

## 현재 확인한 범위

- 기존 ROS 이미지에 GPU를 전달해 `nvidia-smi` 실행 성공.
- Isaac 6.2 headless Compatibility Checker에서 Vulkan GPU 인식, `PASSED`, 종료 코드 0 확인. 전체 장면의 물리·RTX 출력은 별도 검증 필요.
- 현재 에이전트 셸은 DISPLAY가 없으므로 headless 검사 후 WebRTC 화면 연결을 검토한다.
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

## 다음 검증

Compatibility Checker는 통과했다. 다음은 최소 물리 장면·렌더링 → WebRTC 화면 → ROS Bridge → 주행 장면 순으로 진행한다. WebRTC 포트와 캐시 권한은 해당 구성에서 명시한다. 장면이 보이기 전에는 GUI 준비 완료로 기록하지 않는다.

공식 참고: [시스템 요구사항](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/requirements.html), [컨테이너 설치](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/install_container.html), [WebRTC 클라이언트](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/manual_livestream_clients.html).
