# 002 — Isaac UI에서 주행 장면 구성과 실패 조건 실험

**상태: UI 중심 실험 계획. Isaac 컨테이너 호환성 검사는 통과했다. 주행 장면·Bridge·waypoint 제어기·명령 유효시간 정책·수신측 watchdog은 아직 구현/검증하지 않았다.** 화면과 최소 물리 장면의 최신 검증 상태는 [환경 안내](../environments/README.md)를 따른다. 아래 계약과 판정 기준은 제안이며 현재 로봇의 동작을 보장하지 않는다.

목표는 Isaac Sim UI에서 장면·로봇·실험 조건을 직접 구성하고, Python ROS 2 노드로 목표점 주행을 연결하며, 명령 중단·pause/resume·reset에서 무엇이 잘못되는지 관측하는 것이다. Stage·Property·Action Graph와 Viewport가 주 작업 공간이다. 이 연결은 이후 카메라 기반 모델, 상태 추정, Nav2를 붙일 기준선이 된다. `001`의 talker/listener나 기초 퀴즈 완료는 선수 조건이 아니다.

## 준비 상태와 역할

- 첫 단계는 Isaac Sim 화면과 작은 물리 장면을 실행할 수 있으면 시작한다. 지원 환경인지, 공식 지원 밖의 컨테이너 실험인지 환경 기록에 구분한다.
- ROS 주행 단계 전에 설치 버전의 Bridge와 주행 가능한 로봇·바닥·제어 그래프를 준비한다. 에이전트가 환경·연결 코드·진단을 맡고, 사용자는 UI에서 구성과 실험 조건을 직접 바꾼다.
- Isaac과 Docker ROS 노드의 도메인·전송 설정을 맞추고 실제 endpoint를 확인한다.
- 초기 장면을 저장하고 동시 이동 명령 발행자가 없는 상태에서 이동 실험을 시작한다.

현재 ROS Docker의 메시지 송수신은 검증됐다. 이 사실로 Isaac의 GUI·GPU·Bridge 연결이 검증된 것은 아니다. 환경 상태는 [환경 안내](../environments/README.md)에 기록한다.

장면 구성에는 공식 [Stage 설정](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup_tutorials/tutorial_intro_environment_setup.html), [TurtleBot 주행](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_drive_turtlebot.html), [TF·odometry](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_tf.html), [simulation clock](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_clock.html)을 기준으로 삼는다(문서 확인: 2026-11-13). 정확한 자산 경로·그래프·시작 위치는 실제 선택한 장면에 맞춰 [sim/](../sim/README.md)에 남긴다. 아래 메뉴는 6.2 공식 문서에서 확인한 경로이며 이 PC의 UI 클릭 성공을 의미하지 않는다.

## 첫 작업 — UI에서 물리 장면과 실행 상태 확인

이 작업은 이후 로봇의 비정상 움직임을 렌더링·충돌·물리 초기화 문제로 구분할 기준선을 만든다. 기본 도형만 있는 장면에서 먼저 실행하며 ROS Bridge는 아직 필요하지 않다.

1. 준비된 최소 물리 장면을 열고 Stage에서 바닥·동적 물체·Physics Scene을 찾는다. 선택한 항목의 정확한 prim 경로를 기록한다. `prim`은 이 장면 트리의 항목이며 이후 그래프가 참조하는 식별 대상이다.
2. Property에서 물체의 시작 위치와 크기, rigid body·collision 설정을 확인한다. Physics Scene에서 중력과 물리 step 설정을 읽는다. 시각적 형상이 있다는 것과 collision이 설정됐다는 것을 따로 확인한다.
3. Play로 낙하·접촉을 관찰한 뒤 Pause로 물리 진행을 멈춘다. Viewport를 이동하며 접촉 상태를 살피고 재개한다. Stop 후에는 시작 pose와 저장값을 비교한다. Stop이 모든 설정·외부 제어 상태를 복원한다고 가정하지 않는다.
4. Stop 상태에서 물체의 높이를 바꾸고 다시 실행한다. 한 번에 하나의 조건만 변경하며 바닥 관통·접촉 진동·초기 겹침이 나타나는지 본다. 다음에는 collision 설정을 바꿔 같은 화면이 서로 다른 물리 결과를 만들 수 있음을 재현한다.
5. 변경 전 값으로 복원한 뒤 장면을 저장하고 다시 열어 재현한다. 실제 화면과 선택한 속성값을 남긴다. 화면 조작은 사용자가 수행하며, 자동 실행 검증 결과와 구분한다.

현재 준비된 장면은 `File > Open`에서 `/workspace/ui-contact-lab.usda`로 연다. 메뉴 입력 전에 Viewport 안을 한 번 클릭해 브라우저 입력 포커스를 준다. 파일 대화상자의 `/workspace`에서 파일을 선택하거나 File name에 `ui-contact-lab.usda`를 입력한다. 에이전트가 이 경로와 Play·Pause·Stop을 브라우저에서 실제 실행했다.

이 장면의 대상은 `/World/TestBody`, 바닥은 `/World/Ground`, 물리 설정은 `/World/PhysicsScene`이다. 상자를 Viewport에서 클릭하면 Property의 `Transform > Translate > Z`에 초기값 `1.5`가 보인다. Stop 상태에서 `2.0`으로 바꾼 후 Play하고, 실험 뒤 Stop → `1.5`로 복원한다. 좌측 실행 버튼은 Play하면 Pause로 바뀌며, 바로 아래 사각형은 Stop이다. 상자가 바닥을 통과하는지·접촉 후 떠 있거나 떨리는지 확인하면 이후 로봇 자산의 collision과 초기 pose 문제를 분리하는 기준이 된다.

실패 조건은 Stop 상태에서 Property 검색창에 `collision`을 입력하고 `Physics > Collider > Collision Enabled`를 끄는 것으로 만든다. Play하면 시각적 상자는 남아 있어도 바닥과의 충돌이 사라져 아래로 떨어질 것으로 예상한다. 이 필드의 존재와 초기 체크 상태는 실제 UI에서 확인했으며, 비활성화 실험은 사용자가 직접 수행한다. Stop 후 다시 체크하고 검색창을 비워 복원한다.

빈 Stage에서 직접 구성한다면 6.2 문서의 `Create > Physics > Physics Scene`과 `Create > Physics > Ground Plane`을 사용한다. 준비된 장면에 이미 해당 항목이 있다면 중복 생성하지 않는다. 동적 물체의 구체적인 경로와 필드값은 선택한 장면에서 확정한다.

| 바꿀 조건 | UI에서 확인할 결과 | 기록할 값 |
| --- | --- | --- |
| 물체의 시작 높이 | 낙하·접촉 후 정착, 화면과 pose 변화 | prim 경로, 변경 전후 위치, 관측한 접촉 상태 |
| 물체의 collision 설정 | 바닥과의 접촉 여부 | 변경한 collision 필드, rigid body 설정, 복원값 |
| Play → Pause → 재개 → Stop | 진행·정지·복원 동작 | 조작 순서, 각 시점의 pose, 저장 Stage와 차이 |

## 다음 작업 — UI에서 주행 그래프 구성

### TurtleBot3 배치

최소 접촉 실험 다음에는 기존 바닥을 유지하고 로봇을 추가한다. 공식 6.2 [주행로봇 자산 목록](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/assets/usd_assets_robots_wheeled.html#turtlebot)의 Multiphysics 경로를 사용한다. 아래 최상위 USD와 base·physics·physx payload는 서버 HTTP 200 및 텍스트 내용을 확인했다. UI 로딩·물리 실행·ROS 연결은 아직 검증하지 않았다. 같은 문서의 기존 `Robots/Turtlebot/Turtlebot3/turtlebot3_burger.usd` 경로는 404를 반환했으므로 사용하지 않는다.

1. Stop하고 상자의 `Collision Enabled`를 켠다. `File > Save As`로 `/workspace/turtlebot-drive.usda`에 작업 사본을 저장한다.
2. 사본의 Stage에서 `/World/TestBody`만 삭제한다. `/World/Ground`, `/World/PhysicsScene`, 조명은 유지한다.
3. 아래 Content Browser에서 `Isaac Sim > Robots_Multiphysics > Turtlebot > Turtlebot3 > turtlebot3_burger > turtlebot3_burger.usda`를 찾아 Viewport로 끌어 넣는다. 폴더 구성이 다르면 Content Browser 주소창에서 아래 자산 폴더 URL을 사용한다. URL은 컨테이너 파일 경로가 아니라 NVIDIA 자산 서버 주소다.

   ```text
   https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.2/Isaac/Robots_Multiphysics/Turtlebot/Turtlebot3/turtlebot3_burger/
   ```

4. Stop 상태에서 로봇의 표시 여부와 추가된 루트 prim의 실제 경로를 확인하고 사본을 저장한다. 이번 단위 작업은 로봇 배치까지다.
5. 다음의 물리 설정 확인으로 이어간다. 원본의 `Physics` 선택은 비어 있고, `ROS`와 `Sensors`는 `none`이다. 화면에 모델이 보인다는 사실만으로 물리·ROS가 설정됐다고 보지 않는다.

### 로봇 물리 설정과 관절 확인

사용자가 위 자산이 화면에 표시되는 것을 확인했다(2026-11-13). 아래 UI 경로는 6.2 공식 [Property의 Variants 선택 안내](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/openusd_tuning_tutorials/tutorial_02_inspect_asset.html)를 참고했고, 관절·크기는 실제 자산 원문에서 확인했다. 이 로봇의 물리 실행은 아직 사용자 관찰을 기다리는 상태다.

1. Stop 상태에서 Stage의 로봇 최상위 `turtlebot3_burger`를 선택한다. Property 검색창을 비운다. 바퀴 링크를 개별적으로 이동하지 않고 로봇 루트의 `Transform > Translate`를 X=`0`, Y=`0`, Z=`0.05` m로 두어 바닥 바로 위에 배치한다.
2. 같은 로봇 루트를 선택한 상태에서 Property의 `Variants`를 펼쳐 `Physics`를 `physx`(PhysX)로 선택한다. 이미 선택되어 있으면 유지한다. `ROS`, `Sensors`는 `none`으로 둔다. 위치를 바꾼 뒤에도 이 선택이 유지되는지 확인한다.
3. Stage의 로봇 아래 `Physics`를 펼쳐 `wheel_left_joint`, `wheel_right_joint`를 확인한다. 로봇의 실제 루트 경로를 `<R>`이라고 하면 아래 표의 상대 구조를 사용한다.
4. Play 후 로봇 전체가 조금 내려와 바닥에 정착하는지 관찰한다. 공중에 계속 고정되거나 부품이 분리되거나 바닥을 통과하면 그 결과를 기록한다. Stop으로 초기 상태에 돌아간 뒤 저장한다. 아직 이동 명령을 연결하지 않았으므로 전진·회전은 이 단계의 판정 대상이 아니다.

| 자산 원문에서 확인한 항목 | 값/경로 |
| --- | --- |
| Articulation Root | `<R>/Geometry/base_footprint/base_link` |
| 바퀴 관절 | `<R>/Physics/wheel_left_joint`, `<R>/Physics/wheel_right_joint` |
| 바퀴 collider 반경 | `0.033 m` |
| 바퀴 중심 간격 | `0.16 m` (`y=±0.08`) |
| 바퀴 angular drive | 양쪽에 `PhysicsDriveAPI:angular`, damping=`10000000`이 작성됨 |

이는 원본 파일의 설정 확인이며 실행 중 pose·토크·제어 성능 측정값이 아니다. 일반 TurtleBot 주행 튜토리얼의 반경 `0.025`와 현재 자산의 collider `0.033`이 다르므로, 이후 Differential Controller에는 실제 사용한 자산 기준으로 치수를 확정한다. 근거 파일은 위 자산 폴더의 `payloads/base.usda`, `payloads/robot.usda`, `payloads/Physics/physics.usda`, `payloads/Physics/physx.usda`다.

이 사본은 NVIDIA 원본 자산을 참조한다. 다운받은 원본·캐시 전체를 Git에 복사하지 않고, 공개할 자체 장면에는 참조 경로와 변경값을 남긴다.

### 제어 연결

주행 가능한 로봇 자산을 로드하고 바닥 접촉과 초기 pose를 확인한다. Stage에서 로봇의 루트 prim을 선택하고 `Window > Graph Editors > Action Graph`에서 그래프를 연다. 공식 TurtleBot 예제의 prim 이름·바퀴 치수를 다른 로봇에 그대로 복사하지 않는다.

그래프에서 **ROS 입력 → 차체 속도 → 좌우 바퀴 속도 → articulation 제어**의 연결을 눈으로 따라가며 아래 설정을 실제 선택한 로봇에 맞춘다. 그래프와 로봇을 저장한 다음 Play로 연결을 검증한다.

| 대상 | UI에서 확정할 계약 |
| --- | --- |
| ROS2 Context·Twist 구독 노드 | Domain ID 또는 환경변수 사용, 실제 토픽 이름 |
| Differential Controller | 실제 바퀴 반경·간격·속도 상한, 전진/회전 입력 연결 |
| Articulation Controller | 로봇 대상 prim, 좌우 관절 이름과 배열 순서, velocity 입력 |
| 실행 연결 | 매 물리 실행에 필요한 tick 연결, 메시지가 없는 동안의 마지막 값 처리 |

수동 속도 입력은 연결 코드나 아래의 보조 CLI로 공급하고, 사용자는 UI에서 로봇 움직임·그래프·Property를 관찰한다. 발행 종료는 정지 메시지가 아니다. 정지 입력이 반영되지 않으면 UI에서 Pause하고 제어 경로를 확인한다.

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

## 보조 진단 — 실제 ROS endpoint와 수동 입력

이 단계는 UI에서 주행 장면과 그래프를 구성한 뒤 수행한다. Isaac에서 Play한 뒤 호스트의 저장소 최상위에서 `bash scripts/ros-shell.sh`를 실행한다. 컨테이너 셸에서 실제 endpoint를 확인한다. 터미널 조작은 연결 확인을 보조하며 실습의 중심은 Isaac 화면이다.

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

## waypoint 기준선과 UI에서 조건 변경

핵심 구현은 개발자가 직접 다룬다. 제공할 ROS 패키지 scaffold와 실행 명령은 아직 없다.

1. odometry에서 현재 평면 위치와 heading을 읽고, 같은 좌표계의 목표점을 사용한다.
2. 목표 방향 오차와 거리로 선속도·각속도를 계산하고 상한을 둔다. 큰 방향 오차에서 전진을 줄이는 등의 선택을 코드와 설정으로 남긴다.
3. 목표 허용 오차에 도달하면 0 속도를 보내고, 도달 시간·최종 오차·궤적을 기록한다.
4. odometry가 없거나 오래되었을 때 이동을 금지하는 조건을 만든다. 정상 종료의 정지 메시지만으로 비정상 종료를 처리할 수 있다고 보지 않는다.
5. 한 목표점에서 기준선을 얻은 뒤 Stop 상태의 Property에서 시작 pose를 바꾸고 재현한다. 목표점은 제어 설정으로 전달하며 UI에 표시할 표식의 위치와 같은 좌표인지 확인한다. 장면의 표시용 물체를 옮기는 것만으로 제어기 목표가 바뀐다고 가정하지 않는다.

제어 주기·센서 age·성능 지표에 사용한 시간 기준을 명시한다. simulator timestamp와 wall time을 그대로 빼면 지연 지표가 되지 않는다. 별도 계측 없이 메시지 수신 간격을 전체 통신 지연이라고 부르지 않는다.

## 실패 주입 — UI의 실행 상태와 물리 조건 활용

다음은 실험 계획이며, 대응 기능은 아직 없다. 각 실험을 초기 장면에서 독립 실행하고 변경 전후 결과를 남긴다.

| 조건 | 관측할 것 | 구현·검증할 대응 |
| --- | --- | --- |
| 이동 중 명령 발행 프로세스 종료 | 마지막 명령 유지 여부, 중단 후 이동 거리·정지 시간 | 발행 프로세스와 독립적인 수신측 watchdog, timeout 후 0 입력 |
| odometry 발행 중단 | 오래된 pose로 계속 주행하는지 | 관측 freshness 판정과 정지 상태 전이 |
| Isaac pause 후 resume | 제어 타이머 정지 여부, 재개 직후 오래된 명령 적용 여부 | 재개 시 관측·명령 유효성 확인 후 이동 재허용 |
| 장면 reset | pose·시간 변화, 이전 목표/누적 상태 잔존 | episode 구분, 제어 상태 초기화, 새 관측 이후 재시작 |
| UI에서 바닥 마찰·로봇 시작 pose 변경 | 동일 제어의 경로 오차·미끄러짐·정착 변화 | 실제 적용된 material·충돌 설정과 제어 성능 분리 |

[`Twist` 메시지](https://github.com/ros2/common_interfaces/blob/jazzy/geometry_msgs/msg/Twist.msg)에는 발행 시각이나 TTL 필드가 없다. 수신측의 마지막 수신 시각으로 연결 중단을 감지할 수는 있지만, 늦게 도착한 메시지의 원래 생성 시각까지 알 수는 없다. 오래된 명령 거부가 필요해지면 timestamp를 포함한 입력이나 별도 계약을 검토한다. 현재 Bridge가 이런 정책을 제공한다고 가정하지 않는다.

watchdog의 시간 기준도 명시해야 한다. ROS simulation time은 pause 동안 멈출 수 있으므로 외부 연결 단절 감지는 monotonic wall clock을 고려한다. Isaac 내부 로직이 pause 동안 실행되지 않으면 timeout이 지나도 그 즉시 액추에이터를 갱신할 수 없으므로, resume의 첫 물리 step 전에 유효성을 재평가하는 연결까지 검증한다.

Isaac의 simulation time은 공식 예제에서 기본적으로 stop/play 후에도 단조 증가한다. `resetOnStop=true`일 때는 0으로 되돌릴 수 있다. reset이 항상 시간 역행을 만든다고 가정하지 말고 실제 설정·관측을 남긴다. 시간 역행이 없더라도 pose reset에 따른 제어 상태 초기화는 필요하다. [공식 clock 동작](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_clock.html)

## 다음 확장 — UI에서 카메라 배치

주행 기준선을 확보하면 `Create > Camera`로 카메라를 추가하고, 로봇 body 아래의 적절한 prim에 붙인다. 외부 Viewport와 센서 시점을 함께 보면서 위치·방향·가림을 조정한다. 6.2 공식 문서의 `Tools > Sensors > Camera Inspector`에서 카메라를 선택해 확인할 수 있다. 실제 robot body 경로와 카메라 transform은 선택한 자산에서 정한다. [공식 카메라 UI 절차](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup_tutorials/tutorial_gui_camera_sensors.html)

카메라 시점을 움직이면 센서의 pose를 바꾸는 경우가 있으므로, 외부 관찰용 카메라와 실험 센서를 구분한다. 이후 ROS 이미지 발행과 추론 연결을 추가하며 센서 미리보기 성공을 ROS 발행 성공으로 기록하지 않는다.

## 성공 기준과 기록

- [ ] UI에서 선택한 prim·그래프·설정 필드와 변경값, 저장 Stage, Play·Pause·Stop 관측을 기록했다.
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
