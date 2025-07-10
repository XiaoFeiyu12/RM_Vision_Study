import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/xiaofeiyu/桌面/study/RM_Vision_Study/期末考前作业/chapt_ws/src/tf/install/tf'
