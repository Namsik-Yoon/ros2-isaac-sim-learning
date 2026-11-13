# Isaac Sim 장면과 실행 계약

이 폴더는 UI에서 사용할 장면 설정과 재현 정보를 관리한다. **Isaac 컨테이너 호환성 검사는 통과했다.** 화면·최소 물리 장면의 최신 검증 상태는 [환경 안내](../environments/README.md)를 따른다. ROS 주행 장면·Bridge·waypoint 제어기·명령 유효시간 정책·수신측 watchdog은 아직 검증하지 않았다.

먼저 최소 물리 장면으로 UI와 접촉·정지·재개를 확인하고, 평평한 바닥의 주행로봇으로 확장한다. `/cmd_vel` 입력, `/odom` 상태, `/clock` 시간으로 Python waypoint 제어를 연결하고 명령 중단·pause/resume·reset을 실험한다. 상세 계획은 [002](../lessons/002-first-motion.md)를 따른다. 토픽 이름·타입은 제안이며 실제 선택한 로봇과 그래프에서 확정한다.

Stage에서 대상을 선택하고 Property에서 위치·물리·센서를 바꾸며, Action Graph에서 ROS와 제어 연결을 구성한다. Play·Pause·Stop과 장면 다시 열기가 기본 실험 조작이다. Python은 제어·추론·계측과 반복 실행을 맡는다. 자동 생성한 장면도 UI에서 수정·저장할 수 있게 구성한다.

첫 실행 파일은 [`scenes/ui-contact-lab.usda`](scenes/ui-contact-lab.usda)다. [UI 시작 스크립트](../environments/isaac-ui.md)가 최초 사본을 `/workspace/ui-contact-lab.usda`에 제공한다. 상자 낙하·접촉·Pause·Stop은 에이전트가 브라우저 UI로 확인했다. 사용자가 변경한 장면은 `/workspace/`에 저장하고 원본과 비교한다.

장면을 구성할 때 다음 정보를 함께 저장한다.

| 항목 | 기록할 내용 |
| --- | --- |
| 버전·자산 | Isaac·Bridge 버전, 원본 자산 출처/경로, 저장 USD 또는 생성 방법 |
| UI 재현 | 대상 prim/그래프의 정확한 경로, Property 필드·변경 전후 값, 메뉴 확인 근거, 저장 위치 |
| 물리·좌표 | 단위, 물리 step, 로봇 기준 방향, 시작 pose, 바퀴/관절 설정 |
| 센서·화면 | 카메라·센서 prim, 로봇에 대한 transform, 센서 Viewport와 외부 Viewport, 영상/ROS 발행 검증 구분 |
| 통신 | 토픽·타입·QoS·주기, namespace·도메인·전송 설정 |
| 관측 출처 | simulator 참값인지 센서/추정인지, odom 원점·frame·timestamp |
| 시간 | `/clock` 발행 위치·주기, `use_sim_time`, pause 및 `resetOnStop` 설정 |
| 제어 실패 처리 | 명령 중단 시 실제 동작, watchdog의 위치·시간 기준·timeout, 재개 조건 |
| 재현 | 초기화 절차, 목표점·속도 상한, 로그 수집 방법, 실제 측정값 |

먼저 공식 [TurtleBot 주행 예제](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_drive_turtlebot.html)와 [TF·odometry](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_tf.html), [Clock](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_clock.html)에서 실제 사용할 연결을 검증한다. 예제의 존재를 이 저장소에서의 실행 성공으로 기록하지 않는다.

공식 [Stage 설정](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup_tutorials/tutorial_intro_environment_setup.html)과 [카메라 UI 절차](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/robot_setup_tutorials/tutorial_gui_camera_sensors.html)를 메뉴 참고자료로 사용한다. 클릭 경로를 문서에서 확인한 상태, 에이전트가 실제 실행한 상태, 사용자가 UI에서 실행한 상태를 분리해 기록한다. UI 배치가 달라지면 같은 prim과 속성을 기준으로 절차를 수정한다.

큰 NVIDIA 원본 자산·설치 파일·캐시·녹화 파일은 복사해 커밋하지 않는다. 출처·버전·다운로드/생성 절차와 작은 설정 파일을 남긴다. 드론 장면은 Isaac·PX4·추가 확장 조합을 별도로 검증한 뒤 추가한다.
