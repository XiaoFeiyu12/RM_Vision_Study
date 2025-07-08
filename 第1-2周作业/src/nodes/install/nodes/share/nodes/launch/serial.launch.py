# 导入库
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    serial_node = Node(
        package="nodes",
        executable="serial_node",
        parameters=['config/params.yaml'],
        name="serial_node"
        )
    publisher_node = Node(
        package="nodes",
        executable="publisher_node",
        name="publisher_node",
    )
    # 创建LaunchDescription对象launch_description,用于描述launch文件
    launch_description = LaunchDescription(
        [serial_node, publisher_node])
    # 返回让ROS2根据launch描述执行节点
    return launch_description
