# 002 — Isaac 주행로봇 폐루프 제어와 실패 조건

**상태: 설계·실행 준비 문서. Isaac Sim 설치, 장면 실행, waypoint 제어기, 명령 유효시간 정책, 수신측 watchdog은 아직 구현/검증하지 않았다.** 아래 계약과 판정 기준은 제안이며 현재 로봇의 동작을 보장하지 않는다.

목표는 Python ROS 2 노드가 Isaac Sim의 주행로봇을 목표점으로 보내고, 명령 중단·pause/resume·reset에서 무엇이 잘못되는지 관측하는 것이다. 이 연결은 이후 카메라 기반 모델, 상태 추정, Nav2를 붙일 기준선이 된다. `001`의 talker/listener나 기초 퀴즈 완료는 선수 조건이 아니다.

## 선행 조건과 시작 상태

- Isaac Sim 화면과 작은 물리 장면을 실제 실행했다. 지원 환경인지, 공식 지원 밖의 컨테이너 실험인지 환경 기록에 구분한다.
- 설치 버전의 ROS 2 Bridge와 주행 가능한 로봇·바닥·제어 연결이 준비됐다.
- Isaac과 Docker ROS 노드의 도메인·전송 설정을 맞추고 실제 endpoint를 확인했다.
- 초기 장면을 저장했으며, 동시 이동 명령 발행자가 없다.

현재 ROS Docker의 메시지 송수신은 검증됐다. 이 사실로 Isaac의 GUI·GPU·Bridge 연결이 검증된 것은 아니다. 환경 상태는 [환경 안내](../environments/README.md)에 기록한다.

장면 구성에는 공식 [TurtleBot 주행](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_drive_turtlebot.html), [TF·odometry](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_tf.html), [simulation clock](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_clock.html)을 기준으로 삼는다(확인: 2026-11-13). 정확한 자산 경로·그래프·시작 위치는 실제 장면을 구성하며 [sim/](../sim/README.md)에 남긴다. 아직 자동으로 실행할 장면 스크립트는 없다.

## 만들 연결과 제안 계약

```text
목표점 → Python 제어기 → /cmd_vel → Isaac Bridge → 바퀴/물리
                    ↑                             │
                    └──────── /odom ───────────────┘
Isaac simulation time ──────── /clock → 제어기·기록
```

| 인터페이스 | 제안 | 연결 때 확인할 사항 |
| --- | --- | --- |
| `/cmd_vel` | `geometry_msgs/msg/Twist`, 전진 `linear.x`, 회전 `angular.z` | 실제 타입·구독 endpoint·좌표·단위·동시 발행자 |
| `/odom` | `nav_msgs/msg/Odometry`, 목표점과 같은 기준 좌표 사용 | `header.frame_id`, `child_frame_id`, timestamp, pose/velocity의 출처 |
| `/clock` | `rosgraph_msgs/msg/Clock`, 제어·관측 노드에 `use_sim_time=true` | 발행자 하나, pause/stop/reset 시 동작, 시간 역행 여부 |
| 시작 설정 | 제어 10 Hz, 속도 상한 0.1 m/s·0.3 rad/s | 물리 step·odom 발행률과 함께 기록; 성능 보장 수치 아님 |
| 목표 판정 | 예: 위치 오차 0.10 m 이하에서 정지 | 실제 로봇 크기·관측 노이즈에 맞춰 확정; 최종 방향은 첫 실험에서 제외 |

첫 `/odom`은 시뮬레이터 pose에서 생성하는 참값 기반 데이터를 사용할 수 있다. 이는 바퀴 인코더·IMU로 추정한 odometry와 다르다. 사용한 출처를 기록하고, 이 기준선 결과를 실제 센서 기반 주행 성능으로 해석하지 않는다. ROS frame 이름만 같다고 장면의 world 원점과 odom 원점이 같다고 가정하지 않는다.

## 첫 60분 — 연결과 수동 기준선

Isaac에서 준비한 장면을 Play한 뒤 호스트의 저장소 최상위에서 `bash scripts/ros-shell.sh`를 실행한다. 컨테이너 셸에서 실제 endpoint를 확인한다.

```bash
ros2 topic list -t
ros2 topic type /cmd_vel
ros2 topic info /cmd_vel --verbose
ros2 interface show geometry_msgs/msg/Twist
```

아래 명령은 실제 입력이 `/cmd_vel`, `geometry_msgs/msg/Twist`인 경우에만 적용한다. `TwistStamped`나 다른 이름을 쓰는 장면이면 명령과 계약을 수정한다. 관찰용 구독자가 있다는 사실만으로 Isaac의 수신 연결이 확인되지는 않는다.

먼저 정지 입력을 보내고 실제 상태를 확인한다.

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'
```

발행을 `Ctrl+C`로 끝낸 뒤, 짧은 전진 입력을 보낸다.

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.1, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'
```

다시 `Ctrl+C` 후 위의 **0 속도 명령을 즉시 발행**해 정지시킨다. 회전 기준선도 같은 정지 절차로 실행한다.

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.3}}'
```

명령 문법은 [ROS 2 Jazzy 공식 문서](https://github.com/ros2/ros2_documentation/blob/jazzy/source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.rst)를 따른다. 발행 종료는 정지 메시지가 아니다. 정지 입력이 반영되지 않으면 Isaac을 pause하고 제어 경로를 확인한다.

이 회차의 산출물은 실제 토픽·타입·QoS·frame·주기, 장면/버전, 전진/회전/정지 화면과 대응하는 odometry 관측이다. odometry와 clock의 구체적인 수집 절차는 장면 연결을 검증한 뒤 추가한다. 현재 문서만으로 폐루프 제어가 완료되지는 않는다.

## 다음 60분 — waypoint 기준선 구현

핵심 구현은 개발자가 직접 다룬다. 제공할 ROS 패키지 scaffold와 실행 명령은 아직 없다.

1. odometry에서 현재 평면 위치와 heading을 읽고, 같은 좌표계의 목표점을 사용한다.
2. 목표 방향 오차와 거리로 선속도·각속도를 계산하고 상한을 둔다. 큰 방향 오차에서 전진을 줄이는 등의 선택을 코드와 설정으로 남긴다.
3. 목표 허용 오차에 도달하면 0 속도를 보내고, 도달 시간·최종 오차·궤적을 기록한다.
4. odometry가 없거나 오래되었을 때 이동을 금지하는 조건을 만든다. 정상 종료의 정지 메시지만으로 비정상 종료를 처리할 수 있다고 보지 않는다.
5. 한 목표점에서 기준선을 얻은 뒤 시작 방향이나 목표점 하나를 바꾸어 재현한다.

제어 주기·센서 age·성능 지표에 사용한 시간 기준을 명시한다. simulator timestamp와 wall time을 그대로 빼면 지연 지표가 되지 않는다. 별도 계측 없이 메시지 수신 간격을 전체 통신 지연이라고 부르지 않는다.

## 실패 주입 — 정상 동작 뒤 별도 60분

다음은 실험 계획이며, 대응 기능은 아직 없다. 각 실험을 초기 장면에서 독립 실행하고 변경 전후 결과를 남긴다.

| 조건 | 관측할 것 | 구현·검증할 대응 |
| --- | --- | --- |
| 이동 중 명령 발행 프로세스 종료 | 마지막 명령 유지 여부, 중단 후 이동 거리·정지 시간 | 발행 프로세스와 독립적인 수신측 watchdog, timeout 후 0 입력 |
| odometry 발행 중단 | 오래된 pose로 계속 주행하는지 | 관측 freshness 판정과 정지 상태 전이 |
| Isaac pause 후 resume | 제어 타이머 정지 여부, 재개 직후 오래된 명령 적용 여부 | 재개 시 관측·명령 유효성 확인 후 이동 재허용 |
| 장면 reset | pose·시간 변화, 이전 목표/누적 상태 잔존 | episode 구분, 제어 상태 초기화, 새 관측 이후 재시작 |

[`Twist` 메시지](https://github.com/ros2/common_interfaces/blob/jazzy/geometry_msgs/msg/Twist.msg)에는 발행 시각이나 TTL 필드가 없다. 수신측의 마지막 수신 시각으로 연결 중단을 감지할 수는 있지만, 늦게 도착한 메시지의 원래 생성 시각까지 알 수는 없다. 오래된 명령 거부가 필요해지면 timestamp를 포함한 입력이나 별도 계약을 검토한다. 현재 Bridge가 이런 정책을 제공한다고 가정하지 않는다.

watchdog의 시간 기준도 명시해야 한다. ROS simulation time은 pause 동안 멈출 수 있으므로 외부 연결 단절 감지는 monotonic wall clock을 고려한다. Isaac 내부 로직이 pause 동안 실행되지 않으면 timeout이 지나도 그 즉시 액추에이터를 갱신할 수 없으므로, resume의 첫 물리 step 전에 유효성을 재평가하는 연결까지 검증한다.

Isaac의 simulation time은 공식 예제에서 기본적으로 stop/play 후에도 단조 증가한다. `resetOnStop=true`일 때는 0으로 되돌릴 수 있다. reset이 항상 시간 역행을 만든다고 가정하지 말고 실제 설정·관측을 남긴다. 시간 역행이 없더라도 pose reset에 따른 제어 상태 초기화는 필요하다. [공식 clock 동작](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_clock.html)

## 성공 기준과 기록

- [ ] 실제 장면에서 명령·odometry·clock 경로를 확인하고 연결 설정을 기록했다.
- [ ] waypoint 제어 코드와 실행 방법을 커밋하고, 제안한 목표 허용 오차에 대한 실제 결과를 남겼다.
- [ ] 명령 중단·pause/resume·reset의 재현 절차와 관측값을 남겼다. 자동 정지 기능이 없으면 그대로 실패/미구현으로 표시했다.
- [ ] 수신측 watchdog을 구현한 경우, 발행 프로세스가 사라져도 작동하는지 별도 검증했다.
- [ ] 초기 상태에서 다시 실행할 수 있고, 성공하지 못한 조건과 사용한 시간 기준을 기록했다.

질문은 결과를 검토할 때 필요한 설계 판단에 한해 한다. 예를 들어 “pause 중 timeout이 발생했을 때 resume 시 이전 명령을 적용할지, 새 명령을 기다릴지”는 시스템 정책이다. 답변을 기초 퀴즈로 요구하거나 실행을 막는 관문으로 삼지 않는다.

## 초기화와 진단

발행 프로세스를 종료하고 0 속도로 실제 정지를 확인한 뒤 시뮬레이션을 정지한다. 초기 장면을 다시 열고 pose·clock 정책·남은 발행자를 확인한다. 제어기 상태 초기화 절차는 구현과 함께 추가한다.

| 증상 | 먼저 구분할 원인 |
| --- | --- |
| 토픽 또는 Isaac endpoint가 없음 | Play 여부, Bridge 활성화, 도메인·전송 설정, 이름 |
| 메시지는 보이지만 움직이지 않음 | 실제 수신 endpoint·QoS, 바퀴/관절 연결, 지면 접촉 |
| 목표 반대 방향으로 움직임 | 좌표·heading 변환, frame 원점, 바퀴 부호, 중복 발행 |
| 화면은 맞는데 제어기가 정지/발산 | odometry timestamp·출처, 제어/관측 주기, simulation time |
| 발행 종료 후 계속 움직임 | 수신측 timeout의 존재와 실행 위치; 0 명령 또는 pause로 중단 |
| reset 후 갑자기 움직임 | 이전 명령·목표·누적 상태 잔존, pose/시간 점프 처리 |
