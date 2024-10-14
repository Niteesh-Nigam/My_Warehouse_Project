import os
import time
import pandas as pd
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Find barcode_generator package directory
    barcode_generator_pkg = get_package_share_directory('barcode_generator')

    # Source the environment
    source_env_cmd = [
        'bash', '-c', 'source ~/Warehouse_Project/bin/activate && source ~/Warehouse_Project/install/setup.bash && export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:' + os.path.join(barcode_generator_pkg, 'models/')
    ]

    # Load barcodes from CSV located in the barcode_generator package
    output_csv = os.path.join(barcode_generator_pkg, 'barcode_product_list.csv')
    if not os.path.exists(output_csv):
        print(f"CSV file not found at {output_csv}")
        return LaunchDescription()

    # Read the CSV
    df = pd.read_csv(output_csv)
    barcodes = df['Barcode'].tolist()

    # List of spawning commands
    spawn_commands = []

    for barcode in barcodes:
        sdf_file = os.path.join(barcode_generator_pkg, 'models', barcode, f"{barcode}.sdf")
        spawn_cmd = ExecuteProcess(
            cmd=['ros2', 'run', 'gazebo_ros', 'spawn_entity.py', '-entity', barcode, '-file', sdf_file],
            output='screen'
        )
        spawn_commands.append(spawn_cmd)
        spawn_commands.append(ExecuteProcess(cmd=['sleep', '10']))  # Add a delay between spawns

    return LaunchDescription([
        ExecuteProcess(
            cmd=source_env_cmd,
            shell=True,
            output='screen'
        ),
        *spawn_commands  # Execute all spawn commands after setting up the environment
    ])

if __name__ == '__main__':
    from launch import LaunchService
    ld = generate_launch_description()
    ls = LaunchService()
    ls.include_launch_description(ld)
    ls.run()

