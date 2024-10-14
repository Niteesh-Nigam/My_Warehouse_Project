import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import ContactsState
import subprocess
import time

from warehouse_py_pkg.robot_process import PickAndPlaceProcess
  # Import robot process class

class IntegratedNode(Node):
    def __init__(self):
        super().__init__('integrated_node')

        # Subscriptions to both sensors
        self.sensor1_sub = self.create_subscription(
            ContactsState,
            '/red_plane/bumper_states',
            self.sensor1_callback,
            10)

        self.sensor2_sub = self.create_subscription(
            ContactsState,
            '/box/bumper_states',
            self.sensor2_callback,
            10)

        # Track active contacts to avoid redundant processing
        self.active_contacts_sensor1 = set()
        self.active_contacts_sensor2 = set()

        # Robot process initialization but not started yet
        self.robot_process = None  
        self.robot_active = False  # Track if robot process is running

        self.get_logger().info('Integrated Node Started')

    def sensor1_callback(self, msg):
        """Sensor 1 detects new objects and triggers robot process."""
        new_contacts = self.extract_contacts(msg, self.active_contacts_sensor1)

        if new_contacts and not self.robot_active:
            for obj in new_contacts:
                self.get_logger().info(f"Sensor 1 detected: {obj}. Activating robot process.")
                
                # Initialize and start the robot process
                self.robot_process = PickAndPlaceProcess()
                self.robot_active = True  # Mark the process as active

                # Perform the robot's initial task (customize as needed)
                self.robot_process.move_robot([0.0, 1.6, 0.0, 1.5], 4)  
                time.sleep(2)

        self.active_contacts_sensor1.update(new_contacts)

    def sensor2_callback(self, msg):
        """Sensor 2 detects contacts and deletes objects."""
        new_contacts = self.extract_contacts(msg, self.active_contacts_sensor2)

        if new_contacts:
            for obj in new_contacts:
                self.get_logger().info(f"Sensor 2 detected: {obj}. Deleting object.")
                self.delete_object(obj)
                time.sleep(2)  # Avoid rapid re-detections

        self.active_contacts_sensor2.update(new_contacts)

    def extract_contacts(self, msg, active_contacts):
        """Extract new contacts that were not previously detected."""
        new_contacts = set()
        for state in msg.states:
            if 'sensor_collision' in state.collision1_name:
                object_name = state.collision2_name.split('::')[0]
            else:
                object_name = state.collision1_name.split('::')[0]

            if object_name not in active_contacts:
                new_contacts.add(object_name)

        return new_contacts

    def delete_object(self, object_name):
        """Use subprocess to delete an object from the simulation."""
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
    node = IntegratedNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

