#!/usr/bin/env python

import rclpy
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import pandas as pd
from pyzbar import pyzbar
import os

# Load the CSV file containing barcode and product details
csv_file_path = "/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/barcode_product_list.csv"
product_data = pd.read_csv(csv_file_path)

# Global flag to show window
View_window = True

class CameraSubscriber(Node):

    def __init__(self):
        super().__init__('camera_1_node')
        self.subscription = self.create_subscription(
            Image,
            '/camera_sensor/image_raw',
            self.image_callback,
            10)  # Queue size
        self.subscription  # Prevent unused variable warning
        self.bridge = CvBridge()

    def image_callback(self, data):
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(data, desired_encoding='bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge Error: {e}')
            return

        # Process the image for barcode detection
        barcode = self.decode_barcode(cv_image)

        if barcode:
            product_details = self.get_product_details(barcode)
            if product_details:
                # Display both the barcode and the product details (Products column)
                product_info = f"Barcode: {barcode} | Product: {product_details['Product']}"
                cv2.putText(cv_image, product_info, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                # Display the barcode with a "Product not found" message
                cv2.putText(cv_image, f"Barcode: {barcode} | Product not found", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Display the image with the product details or the resized image
        if View_window:
            cv2.imshow("Camera output resized", cv_image)
            # Wait for a key event for 3 milliseconds
            cv2.waitKey(3)

    def decode_barcode(self, frame):
        """Decode the barcode from an image frame."""
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            if barcode_type == "CODE39":  # Only process CODE39 barcodes
                return barcode_data
        return None

    def get_product_details(self, barcode):
        """Retrieve product details from the CSV using the barcode."""
        # Ensure the barcode is treated as a string for matching
        barcode_str = str(barcode).strip()

        # Convert 'Barcode' column to string and strip whitespace
        product_data['Barcode'] = product_data['Barcode'].astype(str).str.strip()

        # Find the product by barcode
        product = product_data.loc[product_data['Barcode'] == barcode_str]

        if not product.empty:
            # Return the product details as a dictionary (using the "Products" column)
            return {'Product': product.iloc[0]['Products']}
        return None


def main(args=None):
    # Initialize the rclpy library
    rclpy.init(args=args)

    # Create an instance of the CameraSubscriber node
    camera_node = CameraSubscriber()

    # Spin the node so its callbacks are called
    try:
        rclpy.spin(camera_node)
    except KeyboardInterrupt:
        camera_node.get_logger().info('Shutting down gracefully')

    # Clean up and destroy the node
    camera_node.destroy_node()

    # Shutdown rclpy
    rclpy.shutdown()

    # Destroy all OpenCV windows
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
