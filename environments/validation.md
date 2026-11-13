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
| Isaac Sim 화면·주행·ROS Bridge | 아직 검증하지 않음 |
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

검사에 표시된 Ubuntu 24.04.3은 컨테이너 환경이다. 호스트 Ubuntu 20.04의 공식 지원을 뜻하지 않는다. 검사 도구의 최소치·용량 집계는 설치 요구사항이나 실제 호스트 파일시스템 여유 공간을 대체하지 않는다. 실제 GUI/스트리밍, 물리 장면, ROS Bridge는 후속 검증 항목이다.

검사 로그에 OmniHub 자식 프로세스 시작 실패 경고가 있었으나 검사는 정상 완료했다. 자산 로딩 단계에서 재현 여부를 확인한다. 현재 CPU governor 경고와 display 없음도 기록했으며 호스트 설정은 바꾸지 않았다.
