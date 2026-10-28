import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class CmdVelWatchdog(Node):
    def __init__(self):
        super().__init__('cmd_vel_watchdog')

        self.declare_parameter('timeout_sec', 0.5)
        self.timeout_sec = self.get_parameter(
            'timeout_sec').get_parameter_value().double_value

        if self.timeout_sec <= 0.0:
            raise ValueError('timeout_sec must be greater than zero')

        self.cmd_vel_pub = self.create_publisher(
            Twist, '/cmd_vel', 10)
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel_raw', self.command_callback, 10)

        self.last_command_time = None
        self.timed_out = True

        # Baslangicta guvenli durum: sifir hiz komutu.
        self.cmd_vel_pub.publish(Twist())

        self.timer = self.create_timer(0.1, self.check_timeout)
        self.get_logger().info(
            f'Watchdog started; timeout={self.timeout_sec:.2f} s')

    def command_callback(self, msg):
        self.last_command_time = self.get_clock().now()
        self.cmd_vel_pub.publish(msg)

        if self.timed_out:
            self.get_logger().info(
                'Command stream received; timeout monitoring reset')
            self.timed_out = False

    def check_timeout(self):
        if self.last_command_time is None or self.timed_out:
            return

        elapsed = (
            self.get_clock().now() - self.last_command_time
        ).nanoseconds / 1e9

        if elapsed <= self.timeout_sec:
            return

        self.cmd_vel_pub.publish(Twist())
        self.timed_out = True
        self.get_logger().warning(
            f'No command for {elapsed:.2f} s; zero velocity published')


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelWatchdog()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_vel_pub.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
