
# Warehouse Automation Project

![Warehouse Simulation](<INSERT_IMAGE_URL_1>)

This repository contains the source code, configuration files, and simulation setups for a **warehouse automation system**. The project simulates automated pick-and-place operations, barcode scanning, and warehouse management using **ROS2** and **Gazebo**.

---

## **Overview**

The **Warehouse Automation Project** brings together a simulated environment where a robot performs:
- Barcode scanning using a camera system.
- Conveyor belt operations.
- Pick-and-place tasks using **MoveIt** and **ROS2 controllers**.
- Warehouse management through Python scripts.

The project integrates multiple ROS2 packages and Gazebo simulation to provide an end-to-end system for managing warehouse processes.

---

## **Key Features**

- **Barcode scanning**: Dynamically generates URDF models with barcodes.
- **Pick-and-place operations**: Automates moving objects between locations using robot arms.
- **Conveyor belt integration**: Controls the conveyor to manage object flow.
- **Real-time simulations**: Uses Gazebo for realistic visualizations.
- **Object detection**: Uses point cloud and camera data to identify and move objects.

---

## **Installation Instructions**

### 1. **Install Required System Packages**
```bash
sudo apt update
sudo apt install python3-colcon-common-extensions
sudo apt install python3-pip
sudo apt-get install ros-humble-cv-bridge
```

### 2. **Install Required Python Packages**
```bash
pip install Jinja2 PyYAML typeguard catkin_pkg pandas pillow python-barcode lxml opencv-python pyzbar numpy==1.23.5
```

---

## **Notes to Reproduce the Environment**

After installing the dependencies, ensure the following environment variables are correctly set:

```bash
export PYTHONPATH=/home/nitzz/Warehouse_Project/lib/python3.10/site-packages:$PYTHONPATH
export GAZEBO_PLUGIN_PATH=$GAZEBO_PLUGIN_PATH:/path/to/models/folder
```

---

## **How to Run the Simulation**

1. **Launch the Gazebo Simulation:**
   ```bash
   ros2 launch my_warehouse_bringup2 my_warehouse_gazebo.launch.xml
   ```

2. **Control the Robot with Pick-and-Place Commands:**
   ```bash
   ros2 launch pick_and_place start_pick_and_place.launch.py
   ```

3. **Start Barcode Scanning:**
   ```bash
   ros2 run warehouse_py_pkg camera_cv2.py
   ```

---

## **Project Structure**

- **barcode_box_creation**: Scripts to generate barcodes and product dimensions.
- **my_conveyorbelt**: Launch files to manage the conveyor belt in Gazebo.
- **my_warehouse_bringup2**: Warehouse simulation environment configurations.
- **warehouse_camera**: Camera URDF files and RViz setup.
- **warehouse_py_pkg**: Python scripts for warehouse management and object handling.
- **pick_and_place**: ROS2 nodes and launch files to control the robot.

---

## **How It Works**

1. **Barcode Creation and Box Spawning**:
   - Generates barcodes dynamically.
   - Spawns corresponding boxes in the simulation.

2. **Pick-and-Place Workflow**:
   - Robot picks objects using a gripper.
   - Moves them to designated areas and releases them.

3. **Object Detection and Conveyor Control**:
   - Camera detects objects using **OpenCV** and **PyZbar**.
   - Conveyor belt is controlled via ROS2 services.

---

## **Visualization and Monitoring**

- **RViz**: Visualize the robot's state, joint movements, and object positions.
- **Gazebo**: Simulate the entire warehouse environment with conveyor belts and shelves.

![Pick and Place Robot](<INSERT_IMAGE_URL_2>)

---

## **Demo Video**

Here is a video demonstration of the system in action:

[![Watch the video](<INSERT_IMAGE_URL_3>)](<VIDEO_URL>)

---

## **References**

This project makes use of concepts and references from the IFRA Conveyor Belt system. You can explore the original project here:  
[https://github.com/IFRA-Cranfield/IFRA_ConveyorBelt](https://github.com/IFRA-Cranfield/IFRA_ConveyorBelt)

---

## **Contributing**

Feel free to contribute to the project by:
- Reporting issues
- Suggesting improvements
- Submitting pull requests

---

## **License**



---
