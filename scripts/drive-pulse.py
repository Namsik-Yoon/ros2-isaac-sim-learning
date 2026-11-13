#!/usr/bin/env python3
"""A short simulated drive command followed by zero; not a receiver watchdog."""
import argparse
import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.duration import Duration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--linear', type=float, default=0.05, help='m/s, abs <= 0.1')
    parser.add_argument('--angular', type=float, default=0.0, help='rad/s, abs <= 0.3')
    parser.add_argument('--seconds', type=float, default=2.0, help='wall seconds, 0 < value <= 5')
    args = parser.parse_args()
    if not all(math.isfinite(v) for v in (args.linear, args.angular, args.seconds)):
        parser.error('All command values must be finite')
    if abs(args.linear) > 0.1 or abs(args.angular) > 0.3 or not 0 < args.seconds <= 5:
        parser.error('Lab limits: abs(linear)<=0.1, abs(angular)<=0.3, 0<seconds<=5')

    rclpy.init()
    node = rclpy.create_node('turtlebot_ui_probe')
    publisher = node.create_publisher(Twist, '/cmd_vel', 10)
    commands_started = False

    def send_for(linear, angular, seconds):
        message = Twist()
        message.linear.x = linear
        message.angular.z = angular
        end = time.monotonic() + seconds
        count = 0
        while rclpy.ok() and time.monotonic() < end:
            publisher.publish(message)
            count += 1
            rclpy.spin_once(node, timeout_sec=0.1)
        print(f'linear={linear} angular={angular} count={count}', flush=True)

    try:
        deadline = time.monotonic() + 8.0
        while publisher.get_subscription_count() < 1 and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
        matched = publisher.get_subscription_count()
        print(f'matched_subscribers={matched}', flush=True)
        if matched != 1 or node.count_publishers('/cmd_vel') != 1:
            raise RuntimeError('Expected one subscriber and this publisher only; no motion pulse sent')
        commands_started = True
        send_for(0.0, 0.0, 1.0)
        if not publisher.wait_for_all_acked(Duration(seconds=2.0)):
            raise RuntimeError('Initial zero not acknowledged; no motion pulse sent')
        print('initial_zero_acknowledged=True', flush=True)
        send_for(args.linear, args.angular, args.seconds)
    finally:
        try:
            if commands_started and rclpy.ok():
                send_for(0.0, 0.0, 1.0)
                acknowledged = publisher.wait_for_all_acked(Duration(seconds=2.0))
                print(f'final_zero_acknowledged={acknowledged}', flush=True)
                if not acknowledged:
                    raise RuntimeError('Final zero not acknowledged; check simulator and use UI Stop')
        finally:
            node.destroy_node()
            rclpy.try_shutdown()


if __name__ == '__main__':
    main()
