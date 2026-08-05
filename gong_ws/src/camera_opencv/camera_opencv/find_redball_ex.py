import cv2
import numpy as np
import rclpy
from action_msgs.msg import GoalStatus
from control_msgs.action import (
    FollowJointTrajectory,
    FollowJointTrajectory_GetResult_Response,
    GripperCommand,
    GripperCommand_GetResult_Response,
)
from cv_bridge import CvBridge
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.task import Future
from sensor_msgs.msg import Image, JointState
from trajectory_msgs.msg import JointTrajectoryPoint


class Manipulator_pub(Node):
    def __init__(self):
        super().__init__("manipulator_pub")  # 노드 이름
        self.joint_client = ActionClient(
            self, FollowJointTrajectory, "/arm_controller/follow_joint_trajectory"
        )
        self.gripper_client = ActionClient(self, GripperCommand, "/gripper_controller/gripper_cmd")
        self.joint_state_subscription = self.create_subscription(
            JointState, "joint_states", self.joint_callback, 10
        )
        self.current_joint_position = [0.0, 0.0, 0.0, 0.0]
        self.current_gripper_position = 0.0
        self.joint_state_received = False
        self.count = True
        self.duration_sec = 1
        self.brige = CvBridge()
        self.create_subscription(Image, "/gripper_camera/image_raw", self.image_callback, 10)

    def image_callback(self, msg: Image):
        # 알고리즘
        self.get_logger().info("카메라 수신 중..")
        img_sub = self.brige.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        hsv = cv2.cvtColor(img_sub, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 40, 40], dtype=np.uint8)
        upper = np.array([10, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)  # type: ignore
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(contour)
            if area > 20:
                x, y, h, w = cv2.boundingRect(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                cv2.rectangle(img_sub, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(img_sub, (x, y), 5, (0, 255, 0), -1)
                self.get_logger().info(f"중심 좌표: x={center_x}, y={center_y}")
        cv2.imshow("img", img_sub)
        cv2.imshow("mask", mask)
        cv2.waitKey(10)
        # x 좌표를 기반으로 해서 좌우로 움직이기 joint 1
        # y 좌표를 기반으로 해서 위아래로 움직이기 joint2~4
        # joint_state subscription -> point 변화.
        # 공의 거리를 추측 area 기반으로 공의 거리를 로깅을 찍으세요.
        # self.move_gripper(-0.01) 안움직여도 됨
        # self.move_joint(point)

    def joint_callback(self, msg: JointState):
        self.current_joint_position = msg.position

    def move_gripper(self, position: float, max_effort=10.0, timeout_sec=5.0):
        if not self.gripper_client.wait_for_server(timeout_sec=timeout_sec):
            self.get_logger().info("gripper_controller Action 서버를 찾지 못햇습니다.")
        goal = GripperCommand.Goal()
        goal.command.position = float(position)
        goal.command.max_effort = float(max_effort)
        send_goal_future = self.gripper_client.send_goal_async(goal)
        send_goal_future.add_done_callback(self.goal_callback)

    def goal_callback(self, future: Future):
        self.goal_handle = future.result()  # type: ignore
        self.get_result_future = self.goal_handle.get_result_async()  # type: ignore
        self.get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(
        self,
        msg: GripperCommand.Impl.FeedbackMessage,
    ):
        feedback: GripperCommand.Feedback = msg.feedback
        self.get_logger().info(f"{feedback.position}")

    def get_result_callback(self, future: Future):
        result: GripperCommand_GetResult_Response = (
            future.result()  # type: ignore
        )
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"succeeded result: {result.result.position}")
        elif result.status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info("aborted!!")
        elif result.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("canceled!!")

    def move_joint(self, point: JointTrajectoryPoint):
        if not self.joint_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().info("joint_controller Action 서버를 찾지 못햇습니다.")
        goal = FollowJointTrajectory.Goal()
        # todo :
        goal.trajectory.header.stamp = self.get_clock().now().to_msg()
        goal.trajectory.header.frame_id = "move_manipulator"
        goal.trajectory.joint_names = ["joint1", "joint2", "joint3", "joint4"]
        goal.trajectory.points.append(point)  # type: ignore

        send_goal_future = self.joint_client.send_goal_async(goal)
        send_goal_future.add_done_callback(self.goal_joint_callback)

    def goal_joint_callback(self, future: Future):
        self.goal_handle = future.result()  # type: ignore
        self.get_result_future = self.goal_handle.get_result_async()  # type: ignore
        self.get_result_future.add_done_callback(self.get_joint_result_callback)

    def feedback_joint_callback(
        self,
        msg: FollowJointTrajectory.Impl.FeedbackMessage,
    ):
        feedback: FollowJointTrajectory.Feedback = msg.feedback
        self.get_logger().info(f"{feedback.actual.positions}")

    def get_joint_result_callback(self, future: Future):
        result: FollowJointTrajectory_GetResult_Response = (
            future.result()  # type: ignore
        )
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f"succeeded result: {result.result.error_string}")
        elif result.status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info("aborted!!")
        elif result.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("canceled!!")


def main(args=None):
    rclpy.init(args=args)  # rmw 활성화
    node = Manipulator_pub()
    try:
        rclpy.spin(node)  # 블럭 (무한 루프)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
