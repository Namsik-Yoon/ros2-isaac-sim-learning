# 002 — UI에서 ROS 2 주행 그래프 연결

상태: 사용자가 TurtleBot3의 직접 바퀴 구동 후 정상적으로 움직인다고 보고했다. 아래 그래프는 설치된 Isaac Sim 6.2.0 소스와 공식 문서로 확인한 구성 절차이며, 현재 사용자 장면에서 생성·실행한 결과는 아직 확인하지 않았다.

## 목표와 입출력

차체의 전진 속도와 회전 속도를 ROS로 받아 바퀴 구동에 연결한다. 나중에 Nav2나 모델 기반 제어기가 같은 입력을 공급할 수 있다.

```text
/cmd_vel (geometry_msgs/msg/Twist)
    linear.x [m/s], angular.z [rad/s]
          ↓ ROS2 Subscribe Twist → Break 3-Vector 2개
    Differential Controller
          ↓ 좌우 바퀴 속도 [rad/s]
    Articulation Controller → wheel_left_joint, wheel_right_joint
```

입력: ROS domain `42`, 절대 토픽 `/cmd_vel`, `geometry_msgs/msg/Twist`.
출력: 바퀴 구동과 차체 움직임. 이 단계는 odometry·clock 발행이나 위치 제어를 포함하지 않는다.

## 준비

- [직접 바퀴 속도 실험](002-first-motion.md#ui에서-바퀴-속도-직접-입력)을 마친 장면을 사용한다.
- Stop 상태에서 양쪽 `Angular Drive > Target Velocity`를 `0`으로 복원하고 현재 장면을 저장한다.
- `Physics=physx`, `ROS=none`, `Sensors=none`을 유지한다. 이번에는 ROS variant 대신 아래 그래프로 연결한다.
- 같은 로봇을 제어하는 그래프를 중복 생성하지 않는다. 아래 생성 도구는 중복 제어 여부를 검사하지 않는다.

## 1. UI 도구로 제어 그래프 생성

**Tools > Robotics > OmniGraph Controllers > Differential Controller**를 연다. 설치된 `isaacsim.robot.wheeled_robots.ui`의 `menu_graphs.py`와 [공식 shortcut 문서](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/omnigraph/omnigraph_shortcuts.html#differential-controller)에서 확인한 메뉴다.

| 폼 필드 | 입력값 |
| --- | --- |
| Add to an existing graph? | 해제 |
| graph path | `/Graphs/turtlebot_drive` |
| Robot Prim | 현재 Stage의 최상위 `turtlebot3_burger` 선택 |
| wheel radius | `0.033` m |
| distance between wheels | `0.16` m |
| Left Joint Name | `wheel_left_joint` |
| Right Joint Name | `wheel_right_joint` |
| Left Joint Index / Right Joint Index | 둘 다 `-1` 유지 |
| Use Keyboard Control (WASD) | 해제 |

OK로 생성한다. 이 도구는 로봇 하위에서 Articulation Root를 찾아 대상 경로를 설정한다. 현재 자산에서는 `<로봇 루트>/Geometry/base_footprint/base_link`가 해당한다. 이름과 인덱스를 동시에 지정하면 인덱스가 우선하므로, 이 절차는 인덱스를 `-1`로 두고 이름으로 지정한다.

**Window > Graph Editors > Action Graph**를 열고 방금 만든 `/Graphs/turtlebot_drive`를 편집한다. 이미 그래프가 있으면 새로 만들지 말고 기존 것을 연다. 생성 결과는 다음 연결을 포함한다.

- On Playback Tick → Differential Controller의 `execIn`
- On Playback Tick → Articulation Controller의 `execIn`
- Differential Controller의 `velocityCommand` → Articulation Controller의 `velocityCommand`
- ArrayNames의 `[wheel_left_joint, wheel_right_joint]` → Articulation Controller의 `jointNames`

Differential Controller에서 `Max Linear Speed=0.1`, `Max Angular Speed=0.3`으로 설정한다. `Desired Linear Velocity`, `Desired Angular Velocity`는 처음에는 모두 `0`이다. 바퀴 반경은 이 프로젝트가 확인한 실제 collider 치수이며, 다른 TurtleBot 튜토리얼의 `0.025`를 복사하지 않는다.

## 2. ROS 입력 노드 연결

Action Graph 왼쪽 검색 목록에서 다음 노드를 끌어 넣는다.

- **ROS2 Context** 1개
- **ROS2 Subscribe Twist** 1개
- **Break 3-Vector** 2개 — 하나는 선속도용, 다른 하나는 각속도용

노드의 **제목 부분**을 클릭해 선택하고, 별도의 **Property 패널**에서 값을 편집한다. 그래프 안의 색깔 포트 옆 글자는 연결할 항목의 이름이다. Property 검색창에 이전 실험의 `Target Velocity` 같은 검색어가 남아 있으면 지운다. `Inputs`가 접혀 있으면 펼친 다음 아래 값을 설정하고 문자열 입력은 Enter로 확정한다.

Property가 보이지 않으면 **Window > Property**로 연다(설치된 6.2 메뉴 소스에서 확인). 그래프 선택이 Property에 반영되지 않으면 Stage에서 해당 그래프를 펼쳐 같은 노드를 선택해도 된다. [공식 노드 Property 편집 절차](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/introduction/quickstart_isaacsim_robot.html#control-the-robot)

| 노드 | 필드 | 값 |
| --- | --- | --- |
| ROS2 Context | Use Domain ID Env Var | 체크: 서버의 `ROS_DOMAIN_ID=42` 사용 |
| ROS2 Subscribe Twist | Topic Name | `/cmd_vel` |
| ROS2 Subscribe Twist | Node Namespace | `/` |

`Node Namespace=/`로 루트 namespace를 명시한다. 설치된 6.2 Bridge는 이 필드가 비어 있으면 상위 prim의 `isaac:namespace`를 수집하며, Topic Name 앞의 `/`만으로 그 접두사를 무시하지 않는다. 실제 토픽 이름은 아래 endpoint 조회로 확인한다.

Break 3-Vector 두 개에는 따로 상수값을 입력하지 않는다. ROS 노드에서 들어오는 벡터를 연결하고 필요한 출력 성분을 사용한다. 사용자 첨부 화면에서는 이 노드의 입력이 **Vector**로 표시되며, 노드 정의의 내부 이름은 `tuple`이다.

각 노드의 출력 포트에서 입력 포트로 선을 연결한다. 아래 표는 화면 표시명과 내부 이름을 함께 적었다.

| 출력 포트 | 연결할 입력 포트 |
| --- | --- |
| On Playback Tick: `tick` | ROS2 Subscribe Twist: `execIn` |
| ROS2 Context: `context` | ROS2 Subscribe Twist: `context` |
| ROS2 Subscribe Twist: `linearVelocity` (Linear Velocity) | 선속도용 Break 3-Vector: **Vector** (`tuple`) |
| 선속도용 Break 3-Vector: `x` | Differential Controller: `linearVelocity` (Desired Linear Velocity) |
| ROS2 Subscribe Twist: `angularVelocity` (Angular Velocity) | 각속도용 Break 3-Vector: **Vector** (`tuple`) |
| 각속도용 Break 3-Vector: `z` | Differential Controller: `angularVelocity` (Desired Angular Velocity) |

생성 도구가 만든 두 controller의 Tick 연결은 유지한다. Subscribe Twist의 `execOut`으로 대체하지 않는다. 컨트롤러는 새 ROS 메시지가 없는 프레임에도 실행해야 한다. 현재 장면은 `metersPerUnit=1`이므로 선속도 수치에 추가 스케일 변환을 하지 않는다. [공식 ROS 주행 그래프 설명](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_drive_turtlebot.html#graph-explained)

## 3. Play와 연결 확인

저장한 뒤 **Play**한다. 새로 생성한 그래프와 0 목표값에서는 ROS 명령 전까지 정지해 있는 것이 예상 결과다. 사용자는 UI를 관찰하고, 에이전트는 서버에서 아래 보조 명령으로 실제 수신 endpoint와 타입을 확인한다. 직접 실행할 때도 저장소 최상위의 호스트 셸에서 시작한다.

```bash
bash scripts/ros-shell.sh ros2 topic list --no-daemon --spin-time 2
bash scripts/ros-shell.sh ros2 topic info /cmd_vel --verbose
```

`/cmd_vel`에 `geometry_msgs/msg/Twist` 구독 endpoint가 있어야 다음 주행 명령을 보낸다. 토픽이 보이거나 구독자가 있다는 사실만으로 로봇이 메시지를 받아 움직였다고 판정하지 않는다. 이 문서 작성 시점에는 그래프 생성 전이므로 `/parameter_events`, `/rosout`만 조회됐고 `/cmd_vel`은 없었다.

속도 명령과 0 속도 복원은 [보조 ROS 입력 절차](002-first-motion.md#보조-진단--실제-ros-endpoint와-수동-입력)를 따른다. 먼저 0 명령, 다음 낮은 속도의 직진·회전, 다시 0 명령 순서로 UI 결과를 확인한다. 아직 이 장면의 ROS 주행 성공이나 전송 지연을 측정한 것은 아니다.

## 실패 조건과 복원

- `/cmd_vel`이 없으면 Play·Context domain·Subscribe Twist의 Tick 연결을 확인한다.
- 메시지는 도착하지만 움직이지 않으면 그래프의 목표값, 실제 articulation 대상, 관절 이름과 배열 순서를 비교한다. 직접 바퀴 구동 성공을 비교 기준으로 사용한다.
- 발행을 중단해도 마지막 속도가 유지될 수 있다. 기본 Subscribe Twist에는 수신 timeout으로 정지시키는 로직이 없다. **발행 중단은 정지 명령이 아니다.** 이 실패 주입은 0 속도 복원 경로를 확인한 뒤 별도로 수행한다.
- 실험 종료 시 0 속도 메시지로 실제 정지를 확인하고 Stop한다. 두 바퀴의 직접 drive 목표값도 0인지 확인한 뒤 저장한다. reset 이후 이전 메시지·목표값이 남는지는 다음 실험에서 확인한다.

기록할 결과: 그래프 경로·관절 순서·실제 토픽과 타입, 직진·회전·정지 관찰, 실패 시 노드별 입력/출력값. 예상 속도나 문서·소스 점검을 실제 주행 결과로 기록하지 않는다.
