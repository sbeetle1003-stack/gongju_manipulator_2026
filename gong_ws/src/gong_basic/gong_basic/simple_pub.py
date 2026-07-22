import rclpy
from rclpy.node import Node
from std_msgs.msg import String

def timer_callback():
    print("첫번째 프로그램입니다.")

def main():
    rclpy.init(args=None)
    node = Node("message_pub")
    #타이머 등록
    node.create_timer(1, timer_callback)
    pub = node.create_publisher(String, "message", 10)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("키보드 인터럽트")
    finally:
        node.destroy_node()
    print("첫번째 프로그램입니다.")

if __name__ == '__main__':
    main()