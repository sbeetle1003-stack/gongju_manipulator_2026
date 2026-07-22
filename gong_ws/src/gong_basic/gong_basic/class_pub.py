import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class M_pub(Node):
    def __init__(self):
        super().__init__("message_pub")
        self.count = 0
        self.create_timer(1, self.timer_callback)
        self.pub = self.create_publisher(String, "message", 10)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f"첫번째 프로그램입니다. {self.count}"
        self.get_logger().info(msg.data)
        self.pub.publish(msg)
        self.count += 1


def main():
    rclpy.init(args=None)
    node = M_pub()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        try:
            node.destroy_node()
        except KeyboardInterrupt:
            pass
        rclpy.try_shutdown()
    print("첫번째 프로그램입니다.")


if __name__ == '__main__':
    main()
