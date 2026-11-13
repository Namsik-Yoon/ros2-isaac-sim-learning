# 001 — 두 프로그램이 메시지를 주고받는 모습 보기

목표는 노드, 토픽, 메시지를 실제 실행 결과와 연결하는 것입니다. 예상 시간은 60분이며 조건 변경 실험은 선택 20분입니다. 이 수업은 Isaac Sim 없이 진행합니다.

공식 문서와 예제 소스 확인: 2026-11-13. 실제 환경의 통신 검증 결과는 [환경 안내](../environments/README.md)에서 별도로 관리합니다.

## 선행 조건과 시작 상태

- [000](000-environment.md)의 컨테이너 셸을 열고 닫을 수 있어야 합니다.
- ROS 2 Jazzy 학습 이미지에 `demo_nodes_py`가 설치되어 있어야 합니다.
- 호스트 터미널 A·B·C를 각각 저장소 최상위에서 엽니다. A·B는 통신용, C는 관찰용입니다.
- 각 터미널에서 `bash scripts/ros-shell.sh`를 실행합니다. 아래 `ros2` 명령은 모두 열린 컨테이너 셸에서 실행합니다.

노드는 로봇 시스템의 역할 하나를 담당하는 실행 단위입니다. 이 수업에서는 메시지를 보내는 `talker`와 받는 `listener`를 각각 실행합니다. 토픽은 메시지가 흐르는 이름 있는 통로이고, 메시지 타입은 전달할 데이터의 형식을 정합니다.

```text
/talker  ── /chatter (std_msgs/msg/String) ──▶  /listener
보내는 노드          문자열 메시지                 받는 노드
```

## 직접 실행

### 1. 보내는 프로그램과 받는 프로그램 시작하기

터미널 A:

```bash
ros2 run demo_nodes_py talker
```

터미널 B:

```bash
ros2 run demo_nodes_py listener
```

A에서는 숫자가 붙은 `Hello World` 메시지가 발행되고, B에서는 수신한 메시지가 표시될 것으로 예상합니다. B가 늦게 시작하면 첫 수신 번호가 0이 아닐 수 있습니다. 이는 메시지를 받기 시작한 시점이 다르기 때문입니다. 이 예제의 이름과 동작은 [ROS 2 공식 talker 소스](https://github.com/ros2/demos/blob/jazzy/demo_nodes_py/demo_nodes_py/topics/talker.py)와 [listener 소스](https://github.com/ros2/demos/blob/jazzy/demo_nodes_py/demo_nodes_py/topics/listener.py)를 참고했습니다.

### 2. 통신 구조 관찰하기

A·B를 계속 실행한 채, 터미널 C에서 한 명령씩 실행합니다.

```bash
ros2 node list
ros2 topic list -t
ros2 topic info /chatter
ros2 node info /talker
ros2 interface show std_msgs/msg/String
ros2 topic echo /chatter --once
```

찾아볼 결과는 다음과 같습니다.

| 명령 | 찾을 내용 |
| --- | --- |
| `node list` | `/talker`, `/listener` |
| `topic list -t` | `/chatter`와 `std_msgs/msg/String` |
| `topic info` | 발행자와 구독자 개수 |
| `node info /talker` | `/chatter`가 발행 목록에 있는지 |
| `interface show` | 문자열을 담는 `data` 필드 |
| `topic echo --once` | 현재 흐르는 메시지 한 개 |

`echo`도 메시지를 받는 도구입니다. 다른 관찰 도구를 실행하면 노드나 구독자 수가 늘어날 수 있으므로 전체 개수를 정답으로 외우지 않습니다. 명령의 의미는 [ROS 2 Jazzy 토픽 교재 원문](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.rst)을 참고합니다.

### 3. 한 가지 조건 바꾸기

**먼저 예상:** B의 listener만 종료하면 A의 출력도 멈출지 한 문장으로 적습니다.

B에서 `Ctrl+C`를 누르고 A를 관찰합니다. C에서 다시 `ros2 topic info /chatter`를 실행한 뒤, B에서 listener를 다시 실행합니다. 실제 결과를 예상과 비교합니다. 노드가 사라진 사실이 도구에 반영되기까지 잠시 걸릴 수 있습니다.

선택 실험: A를 계속 켜 둔 채 B의 listener를 종료하고 다음 명령으로 다시 시작합니다.

```bash
ros2 run demo_nodes_py listener --ros-args -r chatter:=other_chatter
```

이는 listener가 사용할 토픽 이름을 바꾸는 명령입니다. C에서 두 토픽의 발행자·구독자를 살펴보고 B가 조용한 이유를 설명합니다. 종료 후 원래 listener 명령으로 복원합니다.

## 성공 기준

- [ ] 사용자가 A·B에서 발행·수신을 확인했다.
- [ ] 노드 이름, 토픽 이름, 메시지 타입을 각각 찾아 적었다.
- [ ] listener 종료 전 예상과 실제 결과를 비교했다.
- [ ] “메시지 발행 성공”과 “다른 노드가 수신함”을 구분해 설명했다.

실행 로그는 짧은 일부만 남기고, 아직 사용자가 실행하지 않았다면 체크하지 않습니다. 이후 Python 발행자 수업에서는 토픽 선택, 메시지 작성, 타이머와 `publish` 호출을 사용자가 직접 구현합니다. 이 수업의 기본 예제 실행을 직접 개발 완료로 기록하지 않습니다.

## 초기화와 흔한 오류

A·B에서 `Ctrl+C`를 누르고 원래 talker/listener 명령을 다시 실행하면 초기 상태가 됩니다. 셸을 끝낼 때는 `exit`를 사용합니다.

| 증상 | 확인 순서 |
| --- | --- |
| `demo_nodes_py`를 찾지 못함 | 학습 이미지와 `ROS_DISTRO` 확인 |
| A에는 출력이 있지만 B에는 없음 | 두 터미널의 `printenv ROS_DOMAIN_ID`, 토픽 이름, 실행 중인 노드 확인 |
| `/other_chatter`가 보임 | 선택 실험의 이름 변경을 원래대로 복원했는지 확인 |
| 종료한 노드가 계속 보임 | 잠시 뒤 재확인하고, 필요하면 관찰 터미널에서 `ros2 daemon stop` 후 다시 조회 |
| `echo --once`가 끝나지 않음 | talker가 실행 중인지 확인; `Ctrl+C`로 빠져나올 수 있음 |

## 이해 확인 — 한 질문씩

튜터는 다음 질문 하나를 묻고 답을 기다립니다.

> listener를 종료했는데도 talker의 출력이 계속되었다면, talker의 출력만 보고 “누군가 메시지를 받았다”고 말할 수 있을까요? 관찰한 근거로 설명해 주세요.

다음 수업은 Isaac Sim 선행 조건이 준비되면 [002 첫 이동](002-first-motion.md)입니다. 준비 전에는 오늘의 통신 구조를 자신의 그림으로 다시 그려봅니다.
