#!/usr/bin/python3

# ===================================== COPYRIGHT ===================================== #
#                                                                                       #
#  IFRA (Intelligent Flexible Robotics and Assembly) Group, CRANFIELD UNIVERSITY        #
# ===================================== COPYRIGHT ===================================== #

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    # Define the path to the SDF file for the object
    object_path = '/home/nitzz/Warehouse_Automation/src/Conveyor_belt/conveyorbeltt_gazebo/models/conveyorbeltt/conveyorbeltt.sdf'

    # Command to spawn the object using `spawn_entity.py` in the already running Gazebo instance
    spawn_object = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'gazebo_ros', 'spawn_entity.py',
            '-entity', 'conveyor_belt',  # Name of the entity
            '-file', object_path,  # Path to the SDF file
            '-x', '0', '-y', '0', '-z', '0'  # Position arguments
        ],
        output='screen'
    )

    # Return the launch description containing only the spawn process
    return LaunchDescription([
        spawn_object,
    ])

