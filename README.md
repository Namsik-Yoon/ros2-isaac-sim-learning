# ROS 2 · Isaac Sim 실습 노트

숙련된 AI/ML 개발자가 ROS 2와 Isaac Sim으로 주행로봇·드론 시스템을 만드는 한국어 실험 저장소입니다. ROS 경험은 전제하지 않으며, 필요한 로보틱스 개념을 실제 구현과 실패 분석에 연결합니다. 장면 구성·로봇 배치·센서·그래프 편집·실행과 관찰은 **Isaac Sim UI**를 중심으로 진행합니다. Python은 제어·추론·ROS 연결에 사용하며, 하루 60분 이상의 작업을 재현 가능한 결과로 남깁니다.

**첫 목표:** Python 제어기와 Isaac Sim 주행로봇을 연결해 목표 지점 추종을 구현하고, 명령 중단·시뮬레이션 정지/재개 시 동작을 측정하기. ROS Docker 통신, 브라우저 편집기 조작, 최소 장면의 낙하·접촉·Pause·Stop을 검증했습니다. 로봇 주행과 ROS 제어 연결은 다음 단계입니다.

## Isaac Sim 화면에서 시작하기

실행 환경이 준비되어 있으면 다른 PC의 Chrome/Edge에서 `http://<Isaac 서버 주소>:8210`에 접속합니다. 전체 Isaac Sim 편집기를 스트리밍하므로 Stage·Property·Action Graph와 Play/Pause/Stop을 브라우저에서 직접 조작합니다. 브라우저 탭 하나만 연결합니다.

서버 시작·종료, 접속 설정과 장면 저장 위치는 [UI 실행 안내](environments/isaac-ui.md)를 참고합니다. 첫 작업은 [002 UI 실험](lessons/002-first-motion.md)입니다. ROS CLI 예제를 먼저 완료할 필요는 없습니다.

## 다른 PC에서 개발 환경 재현하기

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

# 호스트에서 통신 점검 (이미 검증했다면 생략)
bash scripts/check-ros.sh

# ROS 셸 열기
bash scripts/ros-shell.sh
```

ROS 셸에서 `exit`하면 호스트로 돌아옵니다. 이미 이미지를 빌드하고 점검했다면 반복할 필요는 없습니다. Isaac Sim 실행 준비 상태는 [환경 안내](environments/README.md)를 확인합니다.

기본 경로는 **환경 준비 → [002 UI 장면과 주행 실험](lessons/002-first-motion.md)**입니다. [000 환경 점검](lessons/000-environment.md)·[001 ROS 통신](lessons/001-ros2-topics.md)은 선택 참고자료이며 선수 퀴즈가 아닙니다. 002의 최소 접촉 장면은 에이전트가 실행했고, 주행 제어·실패 대응은 아직 설계·실행 계획입니다.

## 작업 이어가기

이 프로젝트 폴더에서 `이어서 진행`, `이 실패를 재현해줘`, `설계 선택을 비교해줘`, `오늘 결과 기록`처럼 요청하면 현재 상태와 다음 실행 가능한 작업을 이어갑니다. 핵심 제어·실험 코드는 직접 수정해 볼 수 있게 작은 단위로 구성합니다.

[AGENTS.md](AGENTS.md)가 프로젝트 지침이며 [튜터 규칙](tutor/rules.md)과 개인 `.learning/` 기록을 읽도록 지정합니다. Codex는 실행 시작 시 프로젝트 지침을 발견하므로 새 대화에서도 이 프로젝트를 작업 위치로 사용하세요. 다른 프로젝트나 일반 채팅으로 자동 전파되는 전역 설정은 아닙니다. [OpenAI 공식 안내](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

매 단계 기초 확인 질문을 하지 않습니다. 필요한 ROS 개념, 실제 실패 원인, 측정과 설계 판단에 집중합니다. 에이전트의 환경 시험과 사용자의 실제 실험을 구분해 기록합니다. 개인 기록은 Git에 올라가지 않으므로 다른 PC에서는 별도로 옮겨야 합니다.

## 찾아보기

| 위치 | 내용 |
| --- | --- |
| [CURRICULUM.md](CURRICULUM.md) | 주행 → 센서·추론 → 자율주행 → 드론 개발 계획 |
| [lessons/](lessons/README.md) | 재현 가능한 실험과 측정 기준 |
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
