import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from rclpy.action import ActionClient
import time  # Import time for adding delays


class PickAndPlaceProcess(Node):
    def __init__(self):
        super().__init__('pick_and_place_process_node')

        # Action client for trajectory execution
        self.trajectory_client = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_position_controller/follow_joint_trajectory')

        # Service client for vacuum gripper (turn on/off)
        self.gripper_client = self.create_client(SetBool, '/switch')

        self.current_process = 0  # Track which step we're in

        # Start the first process: move down to pick up the box
        self.move_robot([0.2, 1.7, 0.0, 1.5], 4)  # Initial movement

    def move_robot(self, joint_positions, time_sec):
        self.get_logger().info(f'Moving robot to joint positions: {joint_positions}')
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ['arm_base_joint', 'shoulder_joint', 'bottom_wrist_joint', 'top_wrist_joint']

        point = JointTrajectoryPoint()
        point.positions = joint_positions
        point.time_from_start.sec = time_sec
        goal_msg.trajectory.points = [point]

        # Sending the goal to the controller
        self.future_goal_handle = self.trajectory_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        self.future_goal_handle.add_done_callback(self.trajectory_result_callback)

    def feedback_callback(self, feedback_msg):
        pass
        # self.get_logger().info('Received feedback for trajectory goal')

    def trajectory_result_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal was rejected!')
            return

        self.get_logger().info(f'Goal accepted, waiting for result...')
        self.result_future = goal_handle.get_result_async()
        self.result_future.add_done_callback(self.final_trajectory_result)

    def final_trajectory_result(self, future):
        result = future.result().result
        if result.error_code == 0:
            self.get_logger().info('Goal successfully reached')

            # Process tracking to ensure the steps progress sequentially
            if self.current_process == 0:
                # Step 1: Move down to pick up the box
                self.get_logger().info("Step 1: Moving down to pick up the box.")
                self.current_process = 1
                time.sleep(1)  # 2-second gap
                self.activate_gripper(True)  # Activate gripper
                time.sleep(3)

            elif self.current_process == 1:
                # Step 2: Gripper activated, move up with the box
                self.get_logger().info("Step 2: Moving up with the box.")
                self.current_process = 2
                time.sleep(2)  # 2-second gap
                self.move_robot([1.5, 1.5, 0.0, 1.5], 5)  # Move up

            elif self.current_process == 2:
                # Step 3: Move laterally to the new location
                self.get_logger().info("Step 3: Moving to the new location.")
                self.current_process = 3
                time.sleep(2)  # 2-second gap
                self.move_robot([2.0, 1.3, 0.0, 1.5], 4)  # Move laterally

            elif self.current_process == 3:
                # Step 4: Move down to place the box
                self.get_logger().info("Step 4: Moving down to place the box.")
                self.current_process = 4
                time.sleep(2)  # 2-second gap
                self.activate_gripper(False)  # Deactivate gripper

            elif self.current_process == 4:
                # Step 5: Return to default position
                self.get_logger().info("Step 5: Returning to the default position.")
                self.current_process = 5
                time.sleep(2)  # 2-second gap
                self.move_robot([0.0, 0.0, 0.0, 0.0], 4)  # Return to default position
                self.get_logger().info("Task completed. Robot is back to default position.")

        else:
            self.get_logger().error(f'Goal failed with error_code: {result.error_code}')

    def activate_gripper(self, activate):
        self.get_logger().info(f'{"Activating" if activate else "Deactivating"} vacuum gripper')
        while not self.gripper_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for gripper service...')

        request = SetBool.Request()
        request.data = activate
        self.gripper_future = self.gripper_client.call_async(request)
        self.gripper_future.add_done_callback(self.gripper_result_callback)

    def gripper_result_callback(self, future):
        response = future.result()
        if response.success:
            self.get_logger().info(f'Gripper {"activated" if self.current_process == 1 else "deactivated"} successfully')

            # Continue the sequence after activating/deactivating the gripper
            if self.current_process == 1:  # Gripper activated, proceed to next step
                self.move_robot([1.0, 1.0, 0.0, 1.5], 4)
            elif self.current_process == 4:  # Gripper deactivated, move to final step
                self.get_logger().info("Gripper deactivated, proceeding to move back to default position.")
                self.move_robot([0.0, 0.0, 0.0, 0.0], 4)  # Explicitly move to default here
                self.current_process = 5  # Ensure process tracking updates
        else:
            self.get_logger().error(f'Gripper operation failed: {response.message}')


def main(args=None):
    rclpy.init(args=args)
    pick_and_place_process = PickAndPlaceProcess()
    rclpy.spin(pick_and_place_process)

    # Shutdown
    pick_and_place_process.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

