import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from rclpy.qos import QoSProfile


class T_pub(Node):
    def __init__(self):
        super().__init__('tpub')
        self.qos_profile = QoSProfile(depth=10)
        self.publisher = self.create_publisher(Header, 'time', self.qos_profile)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        msg = Header()
        msg.stamp = self.get_clock().now().to_msg()
        self.publisher.publish(msg)
        self.get_logger().info(f'Published time: {msg.stamp}')


def main(args=None):
    rclpy.init(args=args)
    node = T_pub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('키보드 인터럽트')
    finally:
        try:
            node.destroy_node()
        except KeyboardInterrupt:
            pass
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
