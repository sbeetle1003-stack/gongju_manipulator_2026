import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class M_sub(Node):
    def __init__(self):
        super().__init__("message_sub")
        #subscription callback 등록
        self.create_subscription(String, "message", self.sub_callback, 10)


    def sub_callback(self, msg: String):
        self.get_logger().info(msg.data)




def main():
    rclpy.init(args=None)
    node = M_sub()

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
