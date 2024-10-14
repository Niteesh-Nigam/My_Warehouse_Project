import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import ContactsState
import time
import subprocess  # Import subprocess to run CLI commands

class ContactDetector(Node):
    def __init__(self):
        super().__init__('contact_detector')
        
        # Subscription to the bumper sensor topic
        self.subscription = self.create_subscription(
            ContactsState,
            '/box/bumper_states',
            self.contact_callback,
            10)
        self.subscription  # Prevent unused variable warning

        # Track active contacts to avoid repeated detections
        self.active_contacts = set()
        self.get_logger().info('Contact Detector Node Started')

    def contact_callback(self, msg):
        new_contacts = set()

        # Collect the names of all objects currently in contact
        for state in msg.states:
            if 'sensor_collision' in state.collision1_name:
                object_name = state.collision2_name.split('::')[0]
            else:
                object_name = state.collision1_name.split('::')[0]

            new_contacts.add(object_name)

        # Detect new contacts (objects not seen in the previous state)
        new_objects = new_contacts - self.active_contacts

        if new_objects:
            for obj in new_objects:
                self.get_logger().info(f"New contact detected with object: {obj}")
                self.delete_object_cli(obj)  # Call the delete command
                time.sleep(5)  # Pause for 5 seconds

        # Update active contacts with the latest state
        self.active_contacts = new_contacts

    def delete_object_cli(self, object_name):
        """Use subprocess to run the ros2 delete command."""
        try:
            command = f"ros2 service call /delete_entity gazebo_msgs/srv/DeleteEntity \"{{name: '{object_name}'}}\""
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)

            if result.returncode == 0:
                self.get_logger().info(f"Successfully deleted {object_name}.")
            else:
                self.get_logger().error(f"Failed to delete {object_name}.")
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Error deleting {object_name}: {e.output}")

def main(args=None):
    rclpy.init(args=args)
    node = ContactDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

