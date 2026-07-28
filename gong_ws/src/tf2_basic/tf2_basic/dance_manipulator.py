import random
from pathlib import Path

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class DanceManipulator(Node):
    def __init__(self):
        super().__init__("dance_manipulator")
        self.pub = self.create_publisher(JointTrajectory, "arm_controller/joint_trajectory", 10)
        self.joint_names = ["joint1", "joint2", "joint3", "joint4"]
        self.joint_limits = self.load_joint_limits()
        # 한 사이클(트래젝토리 메시지 1개)에 들어가는 경유점 개수와, 경유점 사이 간격
        self.waypoints_per_cycle = 5
        self.segment_duration = 0.8
        self.publish_dance_cycle()
        cycle_duration = self.waypoints_per_cycle * self.segment_duration
        self.create_timer(cycle_duration, self.publish_dance_cycle)

    def load_joint_limits(self) -> dict:
        config_path = (
            Path(get_package_share_directory("tf2_basic")) / "config" / "dance_joint_limits.yaml"
        )
        with open(config_path) as f:
            return yaml.safe_load(f)

    def random_pose(self) -> list:
        return [
            random.uniform(self.joint_limits[name]["min"], self.joint_limits[name]["max"])
            for name in self.joint_names
        ]

    def publish_dance_cycle(self):
        waypoints = [self.random_pose() for _ in range(self.waypoints_per_cycle)]

        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "dance_manipulator"
        msg.joint_names = self.joint_names

        for index, positions in enumerate(waypoints):
            point = JointTrajectoryPoint()
            point.positions = positions

            # 시작점과 끝점은 속도 0, 중간 경유점은 앞뒤 차분으로 속도를 줘서
            # 경유점마다 멈추지 않고 흐르듯 이어지는 동작을 만든다.
            if index == 0 or index == len(waypoints) - 1:
                point.velocities = [0.0] * len(self.joint_names)
            else:
                previous_positions = waypoints[index - 1]
                next_positions = waypoints[index + 1]
                point.velocities = [
                    (next_positions[j] - previous_positions[j]) / (2 * self.segment_duration)
                    for j in range(len(self.joint_names))
                ]

            seconds = self.segment_duration * (index + 1)
            point.time_from_start.sec = int(seconds)
            point.time_from_start.nanosec = int((seconds - int(seconds)) * 1_000_000_000)

            msg.points.append(point)  # type: ignore

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DanceManipulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
