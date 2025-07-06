import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
from tf_transformations import quaternion_from_euler #欧拉角转四元数


class StaticTFBroadcaster(Node):
    def __init__(self) :
        super().__init__("static_tf_broadcatser")

        # 声明参数(这里本来想用python自带文件open方法的，但发现路径汇报错)
        self.declare_parameter("camera_to_gimbal.translation.x", 0.0)
        self.declare_parameter("camera_to_gimbal.translation.y", 0.0)
        self.declare_parameter("camera_to_gimbal.translation.z", 0.0)
        self.declare_parameter("camera_to_gimbal.rotation.roll", 0.0)
        self.declare_parameter("camera_to_gimbal.rotation.pitch", 0.0)
        self.declare_parameter("camera_to_gimbal.rotation.yaw", 0.0)

        # 读取参数
        tx = self.get_parameter("camera_to_gimbal.translation.x").get_parameter_value().double_value
        ty = self.get_parameter("camera_to_gimbal.translation.y").get_parameter_value().double_value
        tz = self.get_parameter("camera_to_gimbal.translation.z").get_parameter_value().double_value
        roll = self.get_parameter("camera_to_gimbal.rotation.roll").get_parameter_value().double_value
        pitch = self.get_parameter("camera_to_gimbal.rotation.pitch").get_parameter_value().double_value
        yaw = self.get_parameter("camera_to_gimbal.rotation.yaw").get_parameter_value().double_value

        self.translation = (tx, ty, tz)
        self.rotation = (roll, pitch, yaw)
        #roll:绕x旋转，pitch:绕y旋转,yaw:绕z旋转

        self.broadcaster=StaticTransformBroadcaster(self)
        self.static_tf_broadcastser()

    def static_tf_broadcastser(self):
        transform=TransformStamped()
        transform.header.frame_id="gimbal_link"
        transform.child_frame_id="camera_link"
        transform.header.stamp=self.get_clock().now().to_msg()

        transform.transform.translation.x=self.translation[0]
        transform.transform.translation.y=self.translation[1]
        transform.transform.translation.z=self.translation[2]

        q=quaternion_from_euler(self.rotation[0],self.rotation[1],self.rotation[2])

        transform.transform.rotation.x=q[0]
        transform.transform.rotation.y=q[1]
        transform.transform.rotation.z=q[2]
        transform.transform.rotation.w=q[3]

        self.broadcaster.sendTransform(transform)
        self.get_logger().info(f"已发布静态TF:{transform}")

def main():
    rclpy.init()
    node=StaticTFBroadcaster()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__=="__main__":
    main()