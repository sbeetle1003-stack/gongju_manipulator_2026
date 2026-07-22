import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class M_pub(Node):
    def __init__(self):
        super().__init__('mpub')
        self.count1 = 0
        self.count2 = 0
        self.pub1 = self.create_publisher(String, 'message1', 10)
        self.pub2 = self.create_publisher(String, 'message2', 10)
        self.create_timer(1, self.timer_callback)

    def timer_callback(self):
        msg1 = String()
        msg1.data = f'message1: {self.count1}'
        self.pub1.publish(msg1)
        self.get_logger().info(msg1.data)
        self.count1 += 1

        msg2 = String()
        msg2.data = f'message2: {self.count2}'
        self.pub2.publish(msg2)
        self.get_logger().info(msg2.data)
        self.count2 += 1


def main(args=None):
    rclpy.init(args=args)
    node = M_pub()
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
