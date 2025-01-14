import os

from ament_index_python.packages import get_package_share_directory
from ament_index_python import get_package_prefix

from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    RegisterEventHandler,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

#models_path = os.path.join('/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/models')
#extend_gazebo_models_path = SetEnvironmentVariable(
#    name='GAZEBO_MODEL_PATH',
#)

def launch_setup(context, *args, **kwargs):

    pkg_share_path = os.pathsep + os.path.join(get_package_prefix('pick_and_place_description'), 'share')
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += pkg_share_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] =  pkg_share_path

    # General arguments
    use_gazebo = LaunchConfiguration("use_gazebo")
    use_ignition = LaunchConfiguration("use_ignition")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")

    # xacro command for model generation
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare('pick_and_place_description'),
                 "urdf", "robot_arm.xacro"]
            ),
            " ",
            "use_gazebo:=",
            use_gazebo,
            " ",
            "use_ignition:=",
            use_ignition,
            " ",
            "use_fake_hardware:=",
            use_fake_hardware
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("pick_and_place_description"),
         "rviz", "visualize_robot.rviz"]
    )

    world_path = PathJoinSubstitution(
                [FindPackageShare('pick_and_place_simulation'),
                 "world", "conveyorbeltt.world"])

    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description, {'use_sim_time': True}],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[{'use_sim_time': True}]
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster",
                   "--controller-manager", "/controller_manager"],
        parameters=[{'use_sim_time': True}]
    )

    delay_rviz_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[rviz_node],
        )
    )

    initial_joint_controller_spawner_started = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_position_controller", "-c", "/controller_manager"],
        parameters=[{'use_sim_time': True}]
    )

    initial_joint_controller_spawner_stopped = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_position_controller", "-c",
                   "/controller_manager", "--stopped"],
        parameters=[{'use_sim_time': True}]
    )

    start_gazebo_server_cmd = IncludeLaunchDescription(
      PythonLaunchDescriptionSource([os.path.join(
        get_package_share_directory('gazebo_ros'), 'launch'), '/gzserver.launch.py']),
      launch_arguments={'world': world_path}.items())
 
    start_gazebo_client_cmd = IncludeLaunchDescription(
     PythonLaunchDescriptionSource([os.path.join(
        get_package_share_directory('gazebo_ros'), 'launch'), '/gzclient.launch.py']))

    spawn_entity_node = Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    arguments=[
        '-topic', 'robot_description',
        '-entity', 'robot_arm',
        '-x', '0',
        '-y', '-0.169733',
        '-z', '0.63',
        '-R', '0.0',
        '-P', '0.0',
        '-Y', '0.0'
    ],
    output='screen'
)
    

    static_transform_publisher_for_camera = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments = ["0", "0", "1.2", "1.57", "3.14", "0.0", "base_link", "camera_link"],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    delay_stfpublisher_after_gazebo_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity_node,
            on_exit=[static_transform_publisher_for_camera],
        )
    )

    nodes_to_start = [
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        delay_rviz_after_joint_state_broadcaster_spawner,
        initial_joint_controller_spawner_stopped,
        initial_joint_controller_spawner_started,
        start_gazebo_server_cmd,
        start_gazebo_client_cmd,
        spawn_entity_node,
        delay_stfpublisher_after_gazebo_spawner,
    ]

    return nodes_to_start


def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "use_gazebo",
            default_value="true",
            description="Switch to enable gazebo control hardware plugin or not",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "use_ignition",
            default_value="false",
            description="Switch to enable ignition control hardware plugin or not",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="false",
            description="Switch to enable fake hardware hardware plugin or not",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
