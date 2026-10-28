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

## SLAM (2D Mapping)

This project uses slam_toolbox (online_async) for 2D mapping from /scan and /odom.

Terminal 1 - simulation:

```
ros2 launch patrol_robot sim.launch.py
```

Terminal 2 - SLAM:

```
ros2 launch patrol_robot slam.launch.py
```

Terminal 3 - activate:

```
ros2 lifecycle set /slam_toolbox configure
ros2 lifecycle set /slam_toolbox activate
```

Terminal 4 - visualize in RViz2 (Fixed Frame: map, add Map + LaserScan + RobotModel + TF):

```
rviz2
```

Terminal 5 - drive the robot:

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel_raw
```

Save the map:

```
ros2 run nav2_map_server map_saver_cli -f ~/patrol_map --ros-args -p use_sim_time:=true
```


## Troubleshooting

### WSL2 system clock stalls gz-transport (7s periodic gaps)

Symptom: /clock, /scan, /odom show 6.5-7.0s gaps every ~1.5s. ros2 topic hz reports negative min intervals.

Root cause: WSL2 systemd-timesyncd periodically jumps the system clock forward by 6.5-7.0s, freezing ZeroMQ timers inside gz-transport.

Evidence: gz topic -e -t /clock -n 5 shows system time jumping +6.58s while sim time advances only +0.01s.

Fix:

```
sudo systemctl stop systemd-timesyncd
sudo systemctl disable systemd-timesyncd
sudo timedatectl set-ntp false
```

Then from Windows PowerShell: wsl --shutdown

Defense-in-depth: sim.launch.py sets GZ_IP=127.0.0.1, GZ_TRANSPORT_TOPIC_STATISTICS=0, GZ_TRANSPORT_BUFFER_SIZE=1048576, applies best_effort QoS on /clock and /scan. .wslconfig sets autoMemoryReclaim=disabled and vmIdleTimeout=-1.


## Update: Latest Verified Status

The Current Status section above is now outdated. Since that writing, the following are verified working:

- Odometry, TF bridging, and joint_states are flowing.
- /scan (LiDAR) is published and visible in RViz2.
- cmd_vel_watchdog stops the robot on command timeout.
- slam_toolbox online_async builds a 2D OccupancyGrid at ~1 Hz.
- Map saved (patrol_map.pgm, 164x126, resolution 0.05 m/px) and reloaded successfully.
- WSL2 systemd-timesyncd stall diagnosed and fixed (see Troubleshooting).

Still pending: Nav2 navigation, simulated camera, anomaly detection, event logging.

