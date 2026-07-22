from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(package="gong_basic", executable="mpub"),
            Node(package="gong_basic", executable="tpub"),
            Node(package="gong_basic", executable="msub"),
            Node(package="gong_basic", executable="m2sub"),
            Node(package="gong_basic", executable="mtsub"),
        ]
    )
