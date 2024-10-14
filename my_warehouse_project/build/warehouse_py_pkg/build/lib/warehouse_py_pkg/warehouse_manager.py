import rclpy
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import pandas as pd
from pyzbar import pyzbar
import os
from std_srvs.srv import Trigger
from gazebo_msgs.msg import ContactsState
import time
import subprocess
from threading import Thread

csv_file_path = "/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/barcode_product_list.csv"
product_data = pd.read_csv(csv_file_path)
product_data_str = pd.read_csv(csv_file_path, dtype={'Barcode': str})

View_window = True

class WarehouseManager(Node):
    def __init__(self):
        super().__init__('warehouse_manager')
        
        self.row_index = 0
        self.box_spawner()

        self.subscription_image = self.create_subscription(
            Image,
            '/camera_sensor/image_raw',
            self.image_callback,
            10)  # Queue size

        # Subscriptions to different contact sensors
        self.subscription_red_plane_contacts = self.create_subscription(
            ContactsState,
            '/red_plane/bumper_states',
            self.red_plane_contact_callback,
            10)
        self.subscription_box_contacts = self.create_subscription(
            ContactsState,
            '/box/bumper_states',
            self.box_contact_callback,
            10)

        self.bridge = CvBridge()
        self.active_red_plane_contacts = set()
        self.active_box_contacts = set()

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, desired_encoding='bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge Error: {e}')
            return

        barcode = self.decode_barcode(cv_image)
        if barcode:
            product_details = self.get_product_details(barcode)
            if product_details:
                self.get_logger().info(f"Starting conveyor for barcode: {barcode}")
                self.start_conveyor_belt()
                product_info = f"Barcode: {barcode} | Product: {product_details['Product']}"
                cv2.putText(cv_image, product_info, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(cv_image, f"Barcode: {barcode} | Product not found", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        if View_window:
            cv2.imshow("Camera output resized", cv_image)
            cv2.waitKey(1)

    def red_plane_contact_callback(self, msg):
        self.process_contacts(msg, self.active_red_plane_contacts, self.handle_red_plane_contact)

    def box_contact_callback(self, msg):
        self.process_contacts(msg, self.active_box_contacts, self.handle_box_contact)

    def process_contacts(self, msg, active_contacts, handler):
        new_contacts = set()

        for state in msg.states:
            if 'sensor_collision' in state.collision1_name:
                object_name = state.collision2_name.split('::')[0]
            else:
                object_name = state.collision1_name.split('::')[0]

            new_contacts.add(object_name)

        new_objects = new_contacts - active_contacts
        for obj in new_objects:
            handler(obj)

        active_contacts.update(new_contacts)

    def handle_red_plane_contact(self, object_name):
        self.get_logger().info(f"Contact on red plane with object: {object_name}")
        self.stop_conveyor_belt()
        self.run_robot_process()

    def handle_box_contact(self, object_name):
        self.get_logger().info(f"Contact on box with object: {object_name}")
        self.delete_object_cli(object_name)

    def stop_conveyor_belt(self):
        os.system('ros2 service call /CONVEYORPOWER conveyorbelt_msgs/srv/ConveyorBeltControl "{power: 0}"')

    def run_robot_process(self):
        Thread(target=self.run_robot_process_thread).start()

    def run_robot_process_thread(self):
        self.get_logger().info("Running robot process...")
        try:
            subprocess.run(
                ['python3', '/home/nitzz/my_warehouse_project/src/warehouse_py_pkg/warehouse_py_pkg/robot_process.py'],
                check=True
            )
            self.get_logger().info("Robot process completed successfully.")
        except subprocess.CalledProcessError as e:
            self.get_logger().error(f"Robot process failed: {e}")

    def delete_object_cli(self, object_name):
        command = f"ros2 service call /delete_entity gazebo_msgs/srv/DeleteEntity \"{{name: '{object_name}'}}\""
        subprocess.run(command, shell=True)
        self.row_index += 1  # Increment index after deleting
        self.box_spawner()
        
        
    def box_spawner(self):
        if self.row_index < len(product_data_str):
            barcode = product_data_str.loc[self.row_index, 'Barcode'].strip()
            try:
                subprocess.run([
                    'ros2', 'run', 'gazebo_ros', 'spawn_entity.py',
                    '-entity', barcode,
                    '-file', f'/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/models/{barcode}/{barcode}.sdf'
                ], check=True)
                print(f'Spawning entity for barcode: {barcode}')
               # return row_index + 1  # Return the next row index to be processed
            except subprocess.CalledProcessError as e:
                print(f"Failed to spawn entity for barcode {barcode}: {e}")
        else:
            print("No more items to spawn.")
            return None  # No more rows to process
        

    def decode_barcode(self, frame):
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            if barcode.type == "CODE39":
                return barcode_data
        return None

    def get_product_details(self, barcode):
        barcode_str = str(barcode).strip()
        product_data['Barcode'] = product_data['Barcode'].astype(str).str.strip()
        product = product_data.loc[product_data['Barcode'] == barcode_str]

        if not product.empty:
            return {'Product': product.iloc[0]['Products']}
        return None

    def start_conveyor_belt(self):
        os.system('ros2 service call /CONVEYORPOWER conveyorbelt_msgs/srv/ConveyorBeltControl "{power: 20}"')

def main(args=None):
    rclpy.init(args=args)
    node = WarehouseManager()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down gracefully')

    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

