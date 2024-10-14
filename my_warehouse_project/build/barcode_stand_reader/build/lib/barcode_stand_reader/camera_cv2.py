import rclpy
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import pandas as pd
from pyzbar import pyzbar
import os
from std_srvs.srv import Trigger

csv_file_path = "/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/barcode_product_list.csv"
product_data = pd.read_csv(csv_file_path)

View_window = True

class CameraSubscriber(Node):

    def __init__(self):
        super().__init__('camera_1_node')

        self.subscription = self.create_subscription(
            Image,
            '/camera_sensor/image_raw',
            self.image_callback,
            10)  # Queue size

        self.bridge = CvBridge()

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
            cv2.waitKey(3)

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
        """Start the conveyor belt by calling the ROS2 service."""
        os.system('ros2 service call /CONVEYORPOWER conveyorbelt_msgs/srv/ConveyorBeltControl "{power: 20}"')

def main(args=None):
    rclpy.init(args=args)
    camera_node = CameraSubscriber()

    try:
        rclpy.spin(camera_node)
    except KeyboardInterrupt:
        camera_node.get_logger().info('Shutting down gracefully')

    camera_node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
