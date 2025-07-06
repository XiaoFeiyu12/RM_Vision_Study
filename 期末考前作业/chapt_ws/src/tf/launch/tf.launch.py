from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        Node(
            package="tf",
            name="tf_broadcaster",
            executable="tf_broadcaster",
            output="screen",
            parameters=["config/camera_to_gimbal.yaml"]
        ),
        Node(
            package="tf",
            name="gimbal_to_base",
            executable="gimbal_to_base",
            output="screen",
            parameters=["config/target_to_map.yaml"]
        )
    ])

'''
colcon build
source install/setup.bash
ros2 launch tf tf.launch.py
'''