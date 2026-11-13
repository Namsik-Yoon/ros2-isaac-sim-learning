# Isaac Sim 장면과 실행 계약

이 폴더는 장면 설정·생성 스크립트와 재현 정보를 관리한다. **Isaac 컨테이너 호환성 검사는 통과했으나, 화면·장면·ROS Bridge 구동은 아직 검증하지 않았다.** 현재 실제 USD 장면, 생성 스크립트, waypoint 제어기, 명령 유효시간 정책, 수신측 watchdog은 없다.

첫 장면은 평평한 바닥의 주행로봇이다. `/cmd_vel` 입력, `/odom` 상태, `/clock` 시간으로 Python waypoint 제어를 연결하고 명령 중단·pause/resume·reset을 실험한다. 상세 계획은 [002](../lessons/002-first-motion.md)를 따른다. 토픽 이름·타입은 제안이며 실제 선택한 로봇과 그래프에서 확정한다.

장면을 구성할 때 다음 정보를 함께 저장한다.

| 항목 | 기록할 내용 |
| --- | --- |
| 버전·자산 | Isaac·Bridge 버전, 원본 자산 출처/경로, 저장 USD 또는 생성 방법 |
| 물리·좌표 | 단위, 물리 step, 로봇 기준 방향, 시작 pose, 바퀴/관절 설정 |
| 통신 | 토픽·타입·QoS·주기, namespace·도메인·전송 설정 |
| 관측 출처 | simulator 참값인지 센서/추정인지, odom 원점·frame·timestamp |
| 시간 | `/clock` 발행 위치·주기, `use_sim_time`, pause 및 `resetOnStop` 설정 |
| 제어 실패 처리 | 명령 중단 시 실제 동작, watchdog의 위치·시간 기준·timeout, 재개 조건 |
| 재현 | 초기화 절차, 목표점·속도 상한, 로그 수집 방법, 실제 측정값 |

먼저 공식 [TurtleBot 주행 예제](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_drive_turtlebot.html)와 [TF·odometry](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_tf.html), [Clock](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/ros2_tutorials/tutorial_series/tutorial_ros2_clock.html)에서 실제 사용할 연결을 검증한다. 예제의 존재를 이 저장소에서의 실행 성공으로 기록하지 않는다.

큰 NVIDIA 원본 자산·설치 파일·캐시·녹화 파일은 복사해 커밋하지 않는다. 출처·버전·다운로드/생성 절차와 작은 설정 파일을 남긴다. 드론 장면은 Isaac·PX4·추가 확장 조합을 별도로 검증한 뒤 추가한다.
