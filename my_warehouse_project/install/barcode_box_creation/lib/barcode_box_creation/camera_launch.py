from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Declare the use_sim_time argument for simulation time
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),

        # Node for the camera
        Node(
            package='barcode_box_creation',
            executable='camera_node',
            name='camera_node',
            output='screen',
            parameters=[{'use_sim_time': True}],
            remappings=[
                ('/camera_sensor/image_raw', '/camera/image_raw')
            ]
        ),
    ])

