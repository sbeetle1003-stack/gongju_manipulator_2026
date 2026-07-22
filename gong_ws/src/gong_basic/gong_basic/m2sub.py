import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class M2_sub(Node):
    def __init__(self):
        super().__init__('m2sub')
        self.create_subscription(String, 'message2', self.sub_callback, 10)

    def sub_callback(self, msg: String):
        self.get_logger().info(msg.data)


def main(args=None):
    rclpy.init(args=args)
    node = M2_sub()
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
