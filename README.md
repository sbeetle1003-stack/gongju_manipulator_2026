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

--------------------
- 총정리




# 2026-07-22 수업 내용 정리(1주차)
--------------------
- 오전

--------------------
- 오후

--------------------
- 총정리



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



