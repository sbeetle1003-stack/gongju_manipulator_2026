import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Header


class MT_sub(Node):
    def __init__(self):
        super().__init__('mtsub')
        self.create_subscription(String, 'message1', self.message_callback, 10)
        self.create_subscription(Header, 'time', self.time_callback, 10)

    def message_callback(self, msg: String):
        self.get_logger().info(msg.data)

    def time_callback(self, msg: Header):
        self.get_logger().info(f'time: {msg.stamp}')


def main(args=None):
    rclpy.init(args=args)
    node = MT_sub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('키보드 인터럽트')
    finally:
        try:
            node.destroy_node()
        except KeyboardInterrupt:
            pass
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
