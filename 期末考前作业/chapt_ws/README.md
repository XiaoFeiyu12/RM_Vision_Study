# 7.5作业
## 代码说明
### URDF
本次作业云台设计为：底座<--云台<--相机。

其他的没什么想说的，就是有一点，一开始找到的参考文章教程都是基于ROS1的系统，导致在编译上浪费了不少时间。好在后面翻到了鱼香肉丝的视频也算顺利完成了。（要是这个建模能直接拖动就好了）  

目前是将机器人模型描述和TF节点控制放在两个不同功能包，还不知道如何同时启动两个包，所以只能单独启动调试了

``` 
cd ~/chapt_ws/src/mbot_description
colcon build
source install/setup.bash
ros2 launch mbot_description mbot_base.launch.py

```

### TF节点

这次采用python写，相较C++感觉清新多了（）。 

首先是yaml参数调用,我在这上面浪费最多时间，一直提示路径报错，最开始本想用python自带的  
`with open("param.yaml","r") as f`
结果经常找不到，于是只得采用`declare_parameter()`和 `get_parameter()`来声明和获得参数。例如：  
```python
self.declare_parameter("target_to_map.translation.x",0.0)
self.declare_parameter("target_to_map.translation.y",0.0)
self.declare_parameter("target_to_map.translation.z",0.0)

        x=self.get_parameter("target_to_map.translation.x").get_parameter_value().double_value
        y=self.get_parameter("target_to_map.translation.x").get_parameter_value().double_value
        z=self.get_parameter("target_to_map.translation.x").get_parameter_value().double_value
```
其次是参考鱼香肉丝的教程，将欧拉角转为四元数，并通过`gimbal_to_base`节点发布修改云台与底盘坐标系夹角从而控制云台转向。  
至于这个夹角欧拉角，可通过`yaw=math.atan2(y,x)`获取目标点极坐标系下的幅角。  
此外，目标节点可通过 .yaml文件修改

## 四轮机器人
不是很会设计且时间有限，仅写出了个底盘加四轮。