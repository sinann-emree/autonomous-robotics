# Autonomous Robotics

A simulation-first autonomous patrol robot project focused on robotics, navigation, and computer vision.

## Project Goals

- Explore and map a simulated environment.
- Navigate autonomously between target locations.
- Detect and avoid obstacles.
- Identify predefined visual anomalies using a simulated camera.
- Record detected events and trigger appropriate responses.

## Development Approach

The project will be developed and tested in simulation before moving to physical hardware.

Safety-related detections (for example fire or a fallen person) are explored at prototype and simulation level only. No claim is made about real-world safety performance.

## Technology Stack

| Component | Choice |
|---|---|
| Host OS | Windows 11 with WSL2 |
| Linux distribution | Ubuntu 24.04 LTS |
| Robot middleware | ROS 2 Jazzy |
| Simulator | Gazebo Harmonic (Gazebo Sim 8) |
| Visualization | RViz 2 |
| SLAM | slam_toolbox |
| Navigation | Nav2 |
| Language | Python |

ROS 2 Jazzy with Gazebo Harmonic is the officially recommended pairing. Gazebo is installed through the ROS vendor packages (`ros-jazzy-ros-gz`).

## Repository Layout

```text
autonomous-robotics/
└── ros2_ws/
    └── src/
        └── patrol_robot/   # ROS 2 Python package
            ├── urdf/       # Robot model (Xacro)
            └── launch/     # Launch files
```

## Build

```bash
cd ros2_ws
colcon build
source install/setup.bash
```

## Run the Simulation

```bash
cd ros2_ws
colcon build --packages-select patrol_robot
source install/setup.bash
ros2 launch patrol_robot sim.launch.py
```

This starts Gazebo (empty world) and the ROS-to-Gazebo `/cmd_vel` bridge, then spawns the robot after a short delay. In a second terminal, drive it with the keyboard:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p speed:=0.2 -p turn:=0.5
```

The robot keeps its last velocity command until a new one arrives (press `k` to stop). A command timeout is not implemented yet.

## Current Status

Verified so far:

- ROS 2 Jazzy installed; talker/listener communication works.
- Gazebo Harmonic opens and runs a sample world, also via `ros2 launch ros_gz_sim gz_sim.launch.py`.
- Gazebo-to-ROS 2 `/clock` bridge works.
- RViz 2 opens.
- `patrol_robot` package skeleton builds with `colcon build`.
- Differential-drive robot model (Xacro) spawns in Gazebo and rests stably on the ground.
- The robot moves forward and rotates in place via the Gazebo DiffDrive plugin, driven from ROS 2 through `/cmd_vel` and keyboard teleop.
- `ros2 launch patrol_robot sim.launch.py` starts the simulation with a single command.

Installed but not yet tested:

- slam_toolbox and Nav2.

Not started yet:

- Odometry and TF bridging to ROS 2, command timeout (watchdog).
- Simulated LiDAR and camera.
- Mapping and autonomous navigation.
- Visual anomaly detection and event logging.
- End-to-end tests and measurements.
