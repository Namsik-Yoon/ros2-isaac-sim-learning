# 002 — UI에서 위치·속도·시뮬레이션 시간 관측

상태: 외부 ROS 명령에 따른 전진·정지는 사용자 관찰로 확인했다. 아래 Odometry/Clock 생성 절차는 설치된 Isaac Sim 6.2 소스와 공식 문서로 확인했으며, 아직 사용자 장면의 발행·수신 결과는 검증하지 않았다. 준비 시점의 외부 토픽 목록에는 `/cmd_vel`, `/parameter_events`, `/rosout`만 있었다.

## 목표와 계약

화면에서 움직이는 로봇의 위치·속도를 ROS에서 읽고, 이후 명령한 속도와 비교한다. 이번 odometry는 시뮬레이터 상태에서 계산한 참값 기반 출력이다. 인코더·IMU를 이용한 추정기의 드리프트·잡음을 검증한 결과로 해석하지 않는다.

| 항목 | 이번 실험의 계약 |
| --- | --- |
| 위치·자세·속도 | `/odom`, `nav_msgs/msg/Odometry` |
| 프레임 | `header.frame_id=odom`, `child_frame_id=base_link` |
| 시뮬레이션 시간 | `/clock`, `rosgraph_msgs/msg/Clock` |
| 시간 초기화 | 두 그래프의 ReadSimTime에서 `Reset On Stop=true` |
| ROS 연결 | domain `42`, 외부 노드는 `scripts/isaac-ros-shell.sh` |
| 현재 로봇 body와 articulation root | `/World/turtlebot3_burger/Geometry/base_footprint/base_link` |

시간·프레임·QoS는 실제 메시지를 받아 다시 확인한다. Odometry의 pose는 `header.frame_id`, twist는 `child_frame_id` 기준으로 해석한다. 이번에는 변위 차이를 먼저 비교하고 `world`와 `odom` 원점이 같다고 가정하지 않는다.

## 1. Odometry 생성

로봇이 정지한 상태에서 **Stop**한다. **Tools > Robotics > ROS 2 OmniGraphs > Odometry Publisher**를 연다. 아래 경로는 이 프로젝트의 저장된 로봇 이름에 맞춘 값이다. 다른 장면에서 재현할 때는 실제 Stage 경로로 바꾼다.

| 폼 필드 | 값 |
| --- | --- |
| Add to an existing graph? | 해제 |
| Graph Path | `/Graph/ROS_Odometry` |
| Node Namespace | `/` |
| Publish Robot's TF? | 해제 |
| Robot Articulation Root | `/World/turtlebot3_burger/Geometry/base_footprint/base_link` |
| Chassis Link Prim | `/World/turtlebot3_burger/Geometry/base_footprint/base_link` |

**OK**로 생성한다. 두 prim 필드는 같은 body를 지정한다. 설치된 생성 코드에서 ComputeOdometry의 측정 대상은 Robot Articulation Root에서, 메시지의 child frame 이름은 Chassis Link Prim의 마지막 이름에서 가져온다. 이번처럼 두 필드가 같은 body이면 이 둘이 일치한다.

이 생성 도구는 Tick·Context·ReadSimTime·ComputeOdometry·PublisherOdometry와 raw TF 노드들을 연결한다. Publish Robot's TF 해제는 로봇 전체 링크 TF 확장을 생략하는 옵션이며 모든 TF 출력을 없애지는 않는다. 생성되는 `TFWorld2Odom`의 원점·회전은 추후 따로 검증하며, 현재 단계에서는 그 연결을 Nav2나 위치 추정의 검증 근거로 사용하지 않는다. [공식 Odometry 생성 메뉴](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_tf.html#graph-shortcuts)

## 2. Clock 생성

**Tools > Robotics > ROS 2 OmniGraphs > Clock**를 열어 **Graph Path=`/Graph/ROS_Clock`**으로 생성한다. 같은 역할의 Clock 그래프가 이미 있으면 재사용하고 중복 생성하지 않는다. [공식 Clock 생성 메뉴](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_clock.html#graph-shortcut)

## 3. Property에서 값 확인

Stage에서 각 그래프를 펼쳐 노드를 선택한다. Property가 없으면 **Window > Property**로 열고 검색어를 비운 뒤 **Inputs**를 펼친다.

| 대상 | 확인할 입력값 |
| --- | --- |
| 두 그래프의 `Context` | Use Domain ID Env Var 체크: 서버 domain `42` 사용 |
| 두 그래프의 `ReadSimTime` | Reset On Stop 체크 |
| Odometry의 `PublisherOdometry` | Topic Name=`/odom`, Node Namespace=`/`, Odom Frame Id=`odom`, Chassis Frame Id=`base_link` |
| Clock의 `PublishClock` | Topic Name=`/clock`, Node Namespace=`/` |

두 생성 도구는 설치된 6.2 소스에서 Reset On Stop을 true로 설정한다. Read Simulation Time 노드 자체의 기본값에 의존하지 말고 생성 결과를 확인한다. 두 시간 공급원이 다른 reset 정책을 쓰면 `/clock`과 odometry stamp가 어긋날 수 있다.

**File > Save → Play**한다. 새 위치·시간 그래프 자체는 이동 명령을 만들지 않으므로, 0 속도 기준선에서는 로봇이 정지해 있는 것이 예상 상태다.

## 4. 수신과 다음 실험

사용자는 UI를 관찰하고 에이전트는 아래 보조 명령으로 실제 endpoint와 첫 샘플을 확인한다. 직접 실행할 경우 호스트의 저장소 최상위에서 사용한다.

```bash
bash scripts/isaac-ros-shell.sh ros2 topic info /odom --verbose
bash scripts/isaac-ros-shell.sh ros2 topic info /clock --verbose
timeout 15s bash scripts/isaac-ros-shell.sh ros2 topic echo /odom nav_msgs/msg/Odometry --once
timeout 15s bash scripts/isaac-ros-shell.sh ros2 topic echo /clock rosgraph_msgs/msg/Clock --once
```

수신 전에는 이동 펄스를 추가하지 않는다. 샘플을 확인한 뒤 UI에서 다음 실험을 수행한다.

1. **정지:** pose가 안정적인지, 속도가 0 근처인지 확인한다. 수치 허용 오차는 실제 샘플과 물리 settling을 본 뒤 정한다.
2. **저속 전진:** 기존 ROS 펄스를 보내고 화면 움직임과 odometry 변위·속도를 함께 기록한다. body의 `linear.x`와 world/odom 축의 `position.x` 변화가 항상 같지는 않으므로 로봇 자세를 함께 본다.
3. **Pause → 재개:** odometry stamp와 `/clock` 증가가 멈추고 재개되는지 관찰한다. 관측용 timeout은 monotonic wall time으로 둬 pause 중에도 결과를 종료할 수 있게 한다.
4. **Stop → Play:** 시간이 0부터 다시 시작하는지, pose가 어떻게 초기화되는지 기록한다. 시간 역행 전후를 같은 궤적의 연속 구간으로 합치지 않는다.

기존 펄스의 `--seconds`는 벽시계 시간이다. `0.05 m/s × 5초 = 0.25 m`를 실제 이동 거리로 단정하지 않는다. 명령 적용 구간의 시뮬레이션 시간과 pose 변화를 측정해야 한다. 서로 다른 시계의 timestamp를 빼서 통신 지연으로 보고하지 않는다.

## 실패 조건과 복원

- 토픽이 없으면 Play, 생성된 Context domain, namespace, Tick 연결을 확인한다.
- 토픽은 있지만 샘플이 없으면 publisher/subscriber QoS와 전송 설정을 확인한다. 앞선 주행에서 검증한 UDP + SUBNET 셸을 사용한다.
- 움직이는데 odometry가 고정되면 ComputeOdometry의 측정 대상이 로봇 body인지 확인한다.
- `/clock` 또는 odometry publisher가 중복되면 어떤 그래프가 발행하는지 확인하고 같은 역할의 중복 생성을 해소한다.
- 종료 전 0 속도로 실제 정지를 확인하고 Stop한다. 저장된 그래프는 유지하며 실행 때마다 다시 만들지 않는다.

산출물: 실제 토픽·타입·QoS·frame, 첫 정지 샘플, 전진 중 pose/속도, Pause·Stop 전후 시뮬레이션 시간. 아직 이 단원의 실제 수신·계측 결과는 없다.
