# gong_manipulator_20206
- 로보티즈의 매니퓰레이터를 실습하는 수업
- [교육생공유슬라이드](https://docs.google.com/presentation/d/1u1cTo7-lzOgn1OTffYmj8k5heEegl7OFczK4jscYZt8/edit?usp=sharing)
- [figma 수업자료](https://www.figma.com/board/0D2JCa1DB0eAV3bslSQIiS/gong_manipulator_20206?node-id=0-1&t=y2PgePJHPb9SdQ8G-1)
- [사전사후평가](https://forms.gle/8AmhKaho7VugqqrDA)

---

## 2026-07-20

---

- wsl 을 설치 (Ubuntu 24.04)
- github 아이디를 만들고 repository를 생성
- git clone 을 해서 wsl 에 복사
- Vscode 설치 해서 remote wsl 로 접속
- github 계정 연동
- ros2 설치 - jazzy
- turtlesim 실습
- ros2 cli 실습
  - node: list, info
  - topic: list, info ,echo, pub, sub, bw, hz
  - service: list, info, call
  - interface: proto
- rqt 실습: rqt_graph, topic monitor,

```bash
ros2 topic pub --rate 1 /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}"

```

---

## 2026-07-21

---

- 1교시: 복습, ros2 common package
- 2교시: 중요 컨셉(DDS, node spin, state)
- 3교시: RMW architecture
- 4교시: Node, Topic, Service, Action 개념
- 5교시: 패키지 작성 ( ros2 pkg create)
- 6교시: simple node 작성(publisher, subscriber)
- 7교시: Header class time pub 작성, 5개 노드 실습
- 8교시: 터틀심 움직이기

---

## 2026-07-22

---

- 1교시: 복습
- 2교시: DDS wsl 에서 설정해야 할 내용 설명
- 3교시: interface 정의, msg, srv 작성
- 4교시: service thread server 작성
- 5교시: service client 작성()
- 6교시: parameter (add_on_set_parameter_callback)
- 7교시: 외부 노드에서 parameter 변경 AsyncParameterClient
- 8교시: launch 에서의 parameter 설정 Node(parameters=[])

---

## 2026-07-23

---

- 1교시: 복습
- 2교시: action interface 정의, action IDL fibonacci 작성
- 3교시: topic, service, action 의 차이점
- 4교시: action server 작성, action client 작성
- 5교시: action thread server 작성( cancel, abort 구현)
- 6교시: namespace 적용 launch 작성
- 7교시: static tf 발행
- 8교시: dynamic tf 발행

---

## 2026-07-24

---

- 1교시: 복습
- 2교시: tf2 설명 tf2 패키지 작성
- 3교시: tf2 listener 작성, tf2 listener 에서 transform 받아오기
- 4교시: 실습[터틀심 listener]
- 5교시: turtlesim 에서 tf2 적용
- 6교시: urdf 설명, urdf 패키지 작성
- 7교시: xacro 실습
- 8교시: urdf 실습

---

## 2026-07-27

---

- 1교시: 복습
- 2교시: 하드웨어 연결 및 dynamixel wizard 설치 및 작동 테스트
- 3교시: manipulator-X 패키지 설치 및 작동 실습
- 4교시: descriptor 실행 및 tf-tree 확인
- 5교시: bringup launch 실행 - robot_state_publisher, joint_state_publisher_gui, rviz2 실행
- 6교시: teleo_keyboard 로 manipulator-X 제어 실습
- 7교시: node 작성 trajectory_joint_state 로 manipulator-X 제어 실습
- 8교시: 과제 - 춤추는 로봇 팔 만들기

---

## 2026-07-28

---

- 1교시: 복습
- 2교시: joint state action code 작성
- 3교시: [실습] 춤추는 로봇팔 만들기
- 4교시: teach manipulator 노드 작성 joint_states 구독
- 5교시: teach manipulator 노드 작성 키보드 인식 코드, yaml 저장 파일
- 6교시: play_recorded_dance 노드 작성
- 7교시: pick and place 실습 (traching data 활용)
- 8교시: moveit 실습

---

## 2026-07-29

---

- 1교시: 복습, moveit node class 작성
- 2교시: moveit srdf 수정
- 3교시: moveit position control 실습
- 4교시:
- 5교시:
- 6교시:
- 7교시:
- 8교시:

## 추가 해야 할 작업
- service 교안 부재
- action 교안 부재
- launch 교안 부재
- tf 교안 부재