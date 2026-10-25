import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('patrol_robot')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(pkg_share, 'urdf', 'patrol_robot.urdf.xacro')
    robot_description = Command(['xacro ', xacro_file])

    # Gazebo: bos dunya, simulasyon otomatik baslar (-r)
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r empty.sdf'}.items())

    # Robotu Gazebo'ya ekle
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-string', robot_description,
                   '-name', 'patrol_robot',
                   '-z', '0.15'],
        output='screen')

    # ROS /cmd_vel -> Gazebo /cmd_vel koprusu
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'],
        output='screen')

    # Gazebo'nun acilmasini beklemek icin robotu 6 saniye gecikmeyle ekle
    return LaunchDescription([
        gz_sim,
        bridge,
        TimerAction(period=6.0, actions=[spawn_robot]),
    ])
