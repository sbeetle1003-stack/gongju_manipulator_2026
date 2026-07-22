# gongju_manipulator_2026
공주대 ROS 로봇팔 제어 program(2026/07/20~2026/08/14) 


# 2026-07-20 수업 내용 정리(1주차)
--------------------
- 오전
- wsl 설치(Ubuntu 24.04)
- github 계정 생성 및 repository 생성
- git clone으로 repository를 wsl에 복사
- VSCode 설치 후 Remote-WSL로 접속
--------------------
- 오후
- .bashrc 개념 학습
- 터미널에서 Tab 자동완성으로 명령어 입력 확인 가능
- turtlesim_node 실행
- remap으로 이름을 바꿔서 동일 프로그램 재실행
- rqt 사용
- topic은 pub, service는 call로 실행
- topic: 계속 데이터를 흘려보내는 통신(실시간 스트리밍)
- service: 필요할 때 요청하고 한 번 응답받는 통신
- action: 시간이 걸리는 목표를 수행하는 통신
- service와 action의 차이: service는 즉각적인 수행, action은 동적인(장시간) 수행
--------------------
- 총정리
- ROS2 기본 구조(Node, Topic, Service, Action, Parameter)를 turtlesim으로 실습하며 통신 방식별 차이 학습
- rqt와 YAML 파라미터로 노드 상태 확인 및 환경 설정 적용법 학습
- ros2 run [패키지] [노드이름]
- ros2 node, topic(echo, pub, sub, bw, hz), service(call), action(send_goal), interface(proto) 명령 실습
- GUI 환경과 CLI 환경의 차이
- 파라미터 등록 시 환경변수를 주로 사용
- 교재 p.123~p.200







# 2026-07-21 수업 내용 정리(1주차)
--------------------
- 오전
- ros2의 Common Packages
- .bashrc에 워크스페이스 오버레이(source install/setup.bash), colcon 자동완성, vcstool 자동완성, colcon_cd 설정 추가
- alias 등록(cbp: colcon build --symlink-install --packages-select, killgazebo)
- ros2 pkg create --build-type ament_python [패키지명] --dependencies [의존성]으로 패키지 생성 실습
- package.xml에 지정한 의존성이 <depend> 태그로 자동 반영되는 것 확인
- setup.py의 entry_points(console_scripts)로 노드를 등록하는 방법 학습
- 함수형 퍼블리셔 노드 작성(create_timer로 주기적 콜백 실행)
- 클래스형 퍼블리셔 노드 작성(Node 상속, self.count로 카운터 관리)
- colcon build로 install 폴더를 갱신해야 ros2 run에 반영됨을 확인(재빌드 필요성)

--------------------
- 오후
- ros2 run이 install 폴더의 복사본을 실행한다는 것 학습(소스 수정 후 재빌드 필요성)
- 클래스형 퍼블리셔/구독자 노드 작성(class_pub.py, class_sub.py) 및 문법 오류·노드이름 충돌 버그 수정
- --symlink-install(cbp) 개념 학습 — 소스 수정 시 재빌드 없이 반영되는 원리
- .bashrc에 cb(전체 빌드), sb(source ~/.bashrc) alias 추가
- Header 메시지 + QoSProfile을 사용한 퍼블리셔 노드 작성(header_pub.py)
- ros2 launch 개념 학습(ros2 run과의 차이 — 여러 노드를 한 번에 실행)
- hello.launch.py 작성(class_pub, class_sub 동시 실행)
- rqt 플러그인 활용법 학습(Topic Monitor, Node Graph, Message Publisher, Console)
- DDS(Data Distribution Service) 개념 — ROS2가 사용하는 통신 미들웨어
--------------------
- 미니과제
- message1, message2, time 세 토픽으로 구분되는 5개 노드 작성
- mpub: message1·message2에 String 발행 / msub: message1 구독 / m2sub: message2 구독
- tpub: time 토픽에 Header 발행 / mtsub: message1과 time을 동시 구독
- topic.launch.py로 5개 노드 동시 실행
- 로그 출력이 너무 빨라 tpub 주기를 10배 조정(0.01초 → 0.1초)
- rclpy.shutdown() 중복 호출 버그 발견, rclpy.try_shutdown() + destroy_node 예외처리로 수정
--------------------
- 총정리




# 2026-07-22 수업 내용 정리(1주차)
--------------------
- 오전
- QoS 복습: qos_test_pub.py 문법 점검, ros2 run 실행 안 되는 원인(빌드 안 됨 vs 오타 vs 확장자) 정리
- colcon build 개념 정리: cb(--symlink-install) vs 일반 colcon build 차이, 새 파일 추가 시 빌드 필요성
- 커스텀 인터페이스 패키지(user_interface) 생성 실습: msg/UserInt.msg, srv/AddAndOdd.srv 작성
- CMakeLists.txt에 rosidl_generate_interfaces로 msg/srv를 빌드하도록 설정, package.xml에 rosidl_interface_packages 등록
- ament_export_dependencies 오타(rosidl_defualt_runtime → rosidl_default_runtime) 수정
--------------------
- 오후
- UserInt.msg에 std_msgs/Header 필드 추가 후 user_int_pub 노드 작성(퍼블리셔에서 커스텀 메시지 사용)
- AddAndOdd.srv 기반 service_server 작성 — 서비스 요청/응답(합, 홀짝 판별) 처리 실습
- service_client 작성(call_async + done_callback으로 논블로킹 서비스 호출)
- 콜백이 오래 걸리는 상황(time.sleep(10)) 재현 → MultiThreadedExecutor + ReentrantCallbackGroup + Lock으로 service_thread_server 작성, 멀티스레드 executor가 필요한 이유 학습
- KeyboardInterrupt 처리 방식을 get_logger().info()에서 print()로 전체 노드에 일괄 수정(spin 종료 후 로거 호출 시 rcl context invalid 에러 방지)
- 파라미터 실습: my_param.py(파라미터 선언 + 변경 콜백), param_async.py(AsyncParameterClient로 외부 노드 파라미터 원격 설정)
- param.launch.py + yaml 파일(my_param.yaml, my_param2.yaml)로 launch 시점에 파라미터 주입하는 방법 학습

--------------------
- 총정리
- 커스텀 msg/srv 인터페이스를 정의하고 rosidl_generate_interfaces로 빌드하는 전체 파이프라인(ament_cmake + ament_python 패키지 간 의존) 이해
- 서비스 서버/클라이언트 기본 패턴과, 콜백이 블로킹될 때 멀티스레드 executor가 왜 필요한지 체득
- 파라미터의 선언 → 콜백 감지 → 외부 원격 설정 → launch+yaml 주입까지 전체 생명주기 학습
- colcon build/symlink-install 관련 트러블슈팅 경험(빌드 캐시 충돌, 패키지 이름 불일치)으로 ROS2 빌드 시스템 동작 원리를 더 깊이 이해



# 2026-07-23 수업 내용 정리(1주차)
--------------------
- 오전

--------------------
- 오후

--------------------
- 총정리



# 2026-07-24 수업 내용 정리(1주차)
--------------------
- 오전

--------------------
- 오후

--------------------
- 총정리



