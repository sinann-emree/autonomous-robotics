import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('patrol_robot')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(pkg_share, 'urdf', 'patrol_robot.urdf.xacro')
    world_file = os.path.join(pkg_share, 'worlds', 'patrol_world.sdf')
    robot_description = Command(['xacro ', xacro_file])

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r ' + world_file}.items())

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-string', robot_description,
                   '-name', 'patrol_robot',
                   '-z', '0.15'],
        output='screen')

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '--ros-args',
            '-p', 'qos_overrides./clock.publisher.reliability:=best_effort',
            '-p', 'qos_overrides./clock.publisher.depth:=1',
            '-p', 'override_timestamps_with_wall_time:=true',
        ],
        output='screen')

    scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '--ros-args',
            '-p', 'qos_overrides./scan.publisher.reliability:=best_effort',
            '-p', 'qos_overrides./scan.publisher.depth:=1',
        ],
        output='screen')

    robot_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/model/patrol_robot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '--ros-args',
            '-p', 'qos_overrides./odom.publisher.reliability:=best_effort',
            '-p', 'qos_overrides./odom.publisher.depth:=1',
        ],
        remappings=[('/model/patrol_robot/tf', '/tf')],
        output='screen')

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': ParameterValue(robot_description, value_type=str),
            'use_sim_time': True,
        }],
        output='screen')

    lidar_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "--x", "0", "--y", "0", "--z", "0",
            "--roll", "0", "--pitch", "0", "--yaw", "0",
            "--frame-id", "lidar_link",
            "--child-frame-id", "patrol_robot/base_link/lidar_sensor",
        ],
        output="screen")

    watchdog = Node(
        package='patrol_robot',
        executable='cmd_vel_watchdog',
        parameters=[{'use_sim_time': True, 'timeout_sec': 0.5}],
        output='screen')

    return LaunchDescription([
        SetEnvironmentVariable('GZ_TRANSPORT_TOPIC_STATISTICS', '0'),
        SetEnvironmentVariable('GZ_IP', '127.0.0.1'),
        SetEnvironmentVariable('GZ_TRANSPORT_BUFFER_SIZE', '1048576'),
        SetEnvironmentVariable('GZ_TRANSPORT_SOCKET_TIMEOUT', '5000'),
        gz_sim,
        clock_bridge,
        scan_bridge,
        robot_bridge,
        watchdog,
        robot_state_publisher,
        lidar_static_tf,
        TimerAction(period=6.0, actions=[spawn_robot]),
    ])
