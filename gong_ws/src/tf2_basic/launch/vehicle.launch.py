# ros2 run turtlesim turtle_teleop_key --ros-args -r __ns:=/model/vehicle_test -r turtle1/cmd_vel:=cmd_vel
# ros2 launch tf2_basic vehicle.launch.py

import os

from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    pkg_ros_tf2_basic = get_package_share_directory("tf2_basic")
    world_path = os.path.join(pkg_ros_tf2_basic, "world", "building_robot.sdf")
    robot_model_path = os.path.join(pkg_ros_tf2_basic, "models", "vehicle_test", "model.sdf")
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")),
        launch_arguments={"gz_args": f"-r {world_path}"}.items(),
    )
    spawn_robot_1 = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-file",
            robot_model_path,
            "-name",
            "vehicle_1",
            "-x",
            "0.0",
            "-y",
            "2.0",
            "-z",
            "0.35",
        ],
    )
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/model/vehicle_test/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/model/vehicle_test/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/model/vehicle_1/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/model/vehicle_1/odometry@nav_msgs/msg/Odometry@gz.msgs.Odometry",
        ],
        parameters=[
            {
                "qos_overrides./model/vehicle_test.subscriber.reliability": "reliable",
                "qos_overrides./model/vehicle_1.subscriber.reliability": "reliable",
            }
        ],
    )
    return LaunchDescription([gz_sim, spawn_robot_1, bridge])
