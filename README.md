# ROS 2 · Isaac Sim 실습 노트

Python으로 직접 코드를 작성하고 가상 주행로봇과 드론의 움직임을 관찰하는 한국어 학습 프로젝트입니다. ROS 2·Isaac Sim 입문자를 대상으로 하루 60분, 선택 실습 30분씩 진행합니다.

**첫 목표:** 내 Python 프로그램으로 주행로봇을 전진·회전·정지시키고, 실제 관측과 원리를 설명하며 다른 사람이 따라 할 수 있게 기록하기.

## 지금 시작하기

Linux, Python 3.8+, 실행 가능한 Docker가 필요합니다. 이 저장소의 스크립트가 호스트 Ubuntu나 GPU 드라이버를 바꾸지는 않습니다. 다른 PC에서는 아래 환경 안내를 먼저 확인하세요.

처음 시작한다면 저장소를 내려받습니다. 이미 프로젝트 폴더가 있다면 이 단계는 생략합니다.

```bash
git clone https://github.com/Namsik-Yoon/ros2-isaac-sim-learning.git
cd ros2-isaac-sim-learning
```

이후 명령은 저장소 최상위 폴더의 호스트 터미널에서 실행합니다.

```bash
# 처음 내려받은 저장소에서 개인 기록 준비 (기존 파일은 유지)
mkdir -p .learning
cp -n tutor/templates/profile.json tutor/templates/progress.json .learning/

# 환경을 직접 관찰
python3 scripts/doctor.py

# 학습 이미지가 없다면 한 번 준비
bash scripts/build-ros.sh

# ROS 셸 열기
bash scripts/ros-shell.sh
```

컨테이너 안에서는 `printenv ROS_DISTRO`와 `ros2 --help`를 실행합니다. `exit`로 호스트에 돌아옵니다. 로컬 설정 담당자가 이미 이미지를 빌드했다면 다시 빌드할 필요는 없습니다.

수업은 [000 환경 이해](lessons/000-environment.md) → [001 노드·토픽](lessons/001-ros2-topics.md) → [002 Isaac 첫 이동](lessons/002-first-motion.md) 순서입니다. 002는 Isaac GUI·장면 준비 이후 진행하는 초안입니다.

## 튜터와 이어서 공부하기

이 프로젝트 폴더를 연 Codex 대화에서 `오늘 수업 시작`, `힌트만 줘`, `왜 이렇게 되는지 설명해줘`, `오늘 수업 마무리`라고 요청할 수 있습니다.

[AGENTS.md](AGENTS.md)가 프로젝트 지침이며 [튜터 규칙](tutor/rules.md)과 개인 `.learning/` 기록을 읽도록 지정합니다. Codex는 실행 시작 시 프로젝트 지침을 발견하므로 새 대화에서도 이 프로젝트를 작업 위치로 사용하세요. 다른 프로젝트나 일반 채팅으로 자동 전파되는 전역 설정은 아닙니다. [OpenAI 공식 안내](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

튜터는 한 번에 질문 하나를 하고, 학습자의 실행과 설명을 구분해 기록합니다. 에이전트가 수행한 환경 시험은 학습자의 수업 완료로 기록하지 않습니다. 개인 기록은 Git에 올라가지 않으므로 다른 PC에서는 별도로 옮기거나 새로 시작해야 합니다.

## 찾아보기

| 위치 | 내용 |
| --- | --- |
| [CURRICULUM.md](CURRICULUM.md) | 주행 → 센서 → 자율주행 → 드론 학습 계획 |
| [lessons/](lessons/README.md) | 직접 따라 할 수업과 성공 기준 |
| [environments/](environments/README.md) | 검증된 ROS 환경과 Isaac 준비 상태 |
| `ros2_ws/src/` | 직접 개발할 ROS 2 패키지 |
| [sim/](sim/README.md) | 장면 준비와 재현 원칙 |
| [study-log/TEMPLATE.md](study-log/TEMPLATE.md) | 공개 학습일지 양식 |
| `.learning/` | 개인 진도·답변·환경 보고서 (Git 제외) |
| [GitHub 시작 안내](environments/github.md) | 저장소 연결과 공개 전 기록 구분 |

## 프로젝트 검증

```bash
python3 -m unittest discover -s tests -v
bash scripts/check-ros.sh
```

첫 명령은 진단 도구의 판단·오류 처리를 검사합니다. 두 번째는 서로 다른 컨테이너 사이의 실제 ROS 메시지 송수신을 검사하고 자신의 임시 컨테이너를 정리합니다. Isaac Sim 구동이나 학습자의 이해를 검사하는 명령은 아닙니다.

큰 설치 파일·다운로드 자산·캐시·ROS 빌드·센서 녹화 파일은 Git에 넣지 않습니다. 실행 절차, 버전, 출처, 짧은 관찰 결과를 남깁니다.
