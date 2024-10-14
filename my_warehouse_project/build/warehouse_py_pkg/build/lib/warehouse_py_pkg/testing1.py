import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import ContactsState
import os
import subprocess

class ContactDetector(Node):
    def __init__(self):
        super().__init__('contact_detector')

        # Subscribe to the bumper sensor topic
        self.subscription = self.create_subscription(
            ContactsState,
            '/red_plane/bumper_states',
            self.contact_callback,
            10)

        # Track which objects are detected
        self.active_contacts = set()
        self.current_obj = None

        self.get_logger().info('Contact Detector Node Started')

    def contact_callback(self, msg):
        """Callback triggered when the sensor detects an object."""
        new_contacts = set()

        # Extract object names from the message
        for state in msg.states:
            if 'sensor_collision' in state.collision1_name:
                object_name = state.collision2_name.split('::')[0]
            else:
                object_name = state.collision1_name.split('::')[0]

            new_contacts.add(object_name)

        # Process new contacts (objects that were not previously detected)
        new_objects = new_contacts - self.active_contacts

        if new_objects:
            for obj in new_objects:
                self.get_logger().info(f"New contact detected with object: {obj}")

                # Store the current object
                self.current_obj = obj

                # Stop the conveyor belt and start the robot process
                self.stop_conveyor_belt()
                self.run_robot_process()

                # Delete the object after processing
                self.delete_object(obj)

                # Spawn the next object
                self.spawn_next_object()

        # Update active contacts
        self.active_contacts = new_contacts

    def stop_conveyor_belt(self):
        """Stop the conveyor belt."""
        self.get_logger().info("Stopping conveyor belt...")
        os.system('ros2 service call /CONVEYORPOWER conveyorbelt_msgs/srv/ConveyorBeltControl "{power: 0}"')

    def run_robot_process(self):
        """Run the robot process using subprocess."""
        self.get_logger().info("Running robot process...")
        try:
            subprocess.run(
                ['python3', '/home/nitzz/my_warehouse_project/src/warehouse_py_pkg/warehouse_py_pkg/robot_process.py'],
                check=True
            )
            self.get_logger().info("Robot process completed successfully.")
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Robot process failed: {e}")

    def delete_object(self, object_name):
        """Delete the detected object via ROS2 service."""
        self.get_logger().info(f"Deleting object: {object_name}")
        try:
            command = f"ros2 service call /delete_entity gazebo_msgs/srv/DeleteEntity \"{{name: '{object_name}'}}\""
            subprocess.run(command, shell=True, check=True)
            self.get_logger().info(f"Successfully deleted {object_name}.")
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Failed to delete {object_name}: {e}")

    def spawn_next_object(self):
        """Spawn the next object by calling testing.py."""
        self.get_logger().info("Spawning the next object...")
        try:
            subprocess.run(
                ['python3', '/home/nitzz/my_warehouse_project/src/warehouse_py_pkg/warehouse_py_pkg/testing.py'],
                check=True
            )
            self.get_logger().info("Next object spawned successfully.")
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Failed to spawn the next object: {e}")

        # Reset state for the next detection cycle
        self.active_contacts.clear()

def main(args=None):
    """Main function to start the ROS2 node."""
    rclpy.init(args=args)
    node = ContactDetector()

    try:
        rclpy.spin(node)  # Keep the node spinning to detect new events
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

