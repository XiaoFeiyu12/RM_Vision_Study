import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
from tf_transformations import quaternion_from_euler #欧拉角转四元数
import math


class TFBroadcaster(Node):
    def __init__(self) :
        super().__init__("tf_broadcatser")

        self.declare_parameter("target_to_map.translation.x",0.0)
        self.declare_parameter("target_to_map.translation.y",0.0)
        self.declare_parameter("target_to_map.translation.z",0.0)

        x=self.get_parameter("target_to_map.translation.x").get_parameter_value().double_value
        y=self.get_parameter("target_to_map.translation.x").get_parameter_value().double_value
        z=self.get_parameter("target_to_map.translation.x").get_parameter_value().double_value
        self.target_point=(x,y,z)

        self.broadcaster=TransformBroadcaster(self)
        self.public_tf()
        self.timer=self.create_timer(0.5,self.public_tf)

    def public_tf(self):
        transform=TransformStamped()
        transform.header.frame_id="base_link"
        transform.child_frame_id="gimbal_link"
        transform.header.stamp=self.get_clock().now().to_msg()

        transform.transform.translation.x=0.0
        transform.transform.translation.y=0.0
        transform.transform.translation.z=0.15

        yaw=math.atan2(self.target_point[1],self.target_point[0])
        q=quaternion_from_euler(0,0,yaw)

        transform.transform.rotation.x=q[0]
        transform.transform.rotation.y=q[1]
        transform.transform.rotation.z=q[2]
        transform.transform.rotation.w=q[3]

        self.broadcaster.sendTransform(transform)
        self.get_logger().info(f"已发布TF:{transform}")

def main():
    rclpy.init()
    node=TFBroadcaster()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__=="__main__":
    main()