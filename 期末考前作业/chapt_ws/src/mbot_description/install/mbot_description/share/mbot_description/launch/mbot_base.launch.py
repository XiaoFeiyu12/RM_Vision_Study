from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
import os

#在查询如何启动launch文件的时候chatgpt告诉我说教程里的是ROS1，ros2需要py文件
def generate_launch_description():
    pkg_share = FindPackageShare('mbot_description').find('mbot_description')
    
    urdf_file = os.path.join(pkg_share, 'urdf', 'robot.urdf')
    # rviz_config_file = os.path.join(pkg_share, 'config', 'mbot_urdf.rviz') 

    return LaunchDescription([
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[{'use_gui': True}],
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': ParameterValue(
                    Command(['cat ', urdf_file]),
                    value_type=str
                )
            }]
        ),
        # Node(
        #     package='rviz2',
        #     executable='rviz2',
        #     name='rviz2',
        #     output='screen',
        # ),
    ])
'''
colcon build
source install/setup.bash
ros2 launch mbot_description mbot_base.launch.py
'''