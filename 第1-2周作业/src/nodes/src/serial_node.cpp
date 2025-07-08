#include <string>
#include <chrono>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "serial_driver/serial_driver.hpp"

using namespace std::chrono_literals;

class SerialNode : public rclcpp::Node
{
    std::vector<uint8_t> transmit_data_buffer = std::vector<uint8_t>(1024); // 发送缓冲区
    std::vector<uint8_t> receive_data_buffer = std::vector<uint8_t>(1024);  // 接收缓冲区
private:
    void receive_from_serial()
    {   

        auto port = serial_driver_->port();
        if (!port ||!port->is_open()){
            RCLCPP_WARN(this->get_logger(),"串口打开失败，无法接收数据");
            return;
        }

        try
        {
            std::vector<uint8_t> new_data;
            size_t received_size = port->receive(new_data);
            new_data.resize(received_size); // 调整大小
            //若非空转移至缓冲区
            if (!new_data.empty()){
                receive_data_buffer.insert(receive_data_buffer.end(),new_data.begin(),new_data.end());
                //处理数据
                process_rx_buffer();
            }
        }
        catch(const std::exception& e)
        {
            RCLCPP_ERROR(this->get_logger(),"串口接收错误");;
        }
    }

    void process_rx_buffer(){
        // 孩子帧头尾这块任是没学明白，只好拜托ds大人了
        // 查找帧头
        auto header_pos = std::find(receive_data_buffer.begin(), receive_data_buffer.end(), frame_header_);
        if (header_pos == receive_data_buffer.end()) {
            receive_data_buffer.clear(); // 未找到帧头，清空缓冲区
            return;
        }
        
        // 在帧头后查找帧尾
        auto trailer_pos = std::find(header_pos + 1, receive_data_buffer.end(), frame_trailer_);
        
        if (trailer_pos != receive_data_buffer.end()) {
            // 提取有效载荷（跳过帧头，到帧尾前）
            auto payload_start = header_pos + 1;
            auto payload_end = trailer_pos;
            std::vector<uint8_t> payload(payload_start, payload_end);
            
            // 发布到ROS话题
            auto msg = std_msgs::msg::String();
            msg.data.assign(payload.begin(), payload.end());
            serial_rx_pub_->publish(msg);
            
            RCLCPP_INFO(this->get_logger(), "发布串口数据: %s", msg.data.c_str());
            
            // 从缓冲区移除已处理的数据
            receive_data_buffer.erase(receive_data_buffer.begin(), trailer_pos + 1);
        }
                // 如果没有找到帧头，清空缓冲区
        if (header_pos == receive_data_buffer.end()) {
            receive_data_buffer.clear();
        }
    }


    void send2serial(const std_msgs::msg::String::SharedPtr msg)
    {   
        auto port=serial_driver_->port();
        if (!port || !port->is_open()) {
            RCLCPP_WARN(this->get_logger(), "串口未打开，无法发送数据");
            return;
        }

        try {
            // 打包数据（添加帧头帧尾）
            transmit_data_buffer.push_back(frame_header_);        // 添加帧头
            // 添加消息内容
            for (char c : msg->data) {
                transmit_data_buffer.push_back(static_cast<uint8_t>(c));
            }
            transmit_data_buffer.push_back(frame_trailer_);       // 添加帧尾
            
            // 发送数据
            size_t sent_bytes = port->send(transmit_data_buffer);
            
            RCLCPP_INFO(this->get_logger(), "发送串口数据: %s (%zu bytes)", msg->data.c_str(), sent_bytes);
        } catch (const std::exception & ex) {
            RCLCPP_ERROR(this->get_logger(), "串口发送错误: %s", ex.what());
        }
    }

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr serial_rx_pub_;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr serial_tx_sub_;
    rclcpp::TimerBase::SharedPtr timer_;
    std::shared_ptr<drivers::serial_driver::SerialDriver> serial_driver_;
    std::shared_ptr<drivers::common::IoContext> io_context_;

    //帧头尾
    uint8_t frame_header_;
    uint8_t frame_trailer_;
public:
    SerialNode():Node("serial_node")
    {   
        // 声明参数
        declare_parameter<std::string>("device_name", "/dev/ttyUSB0");
        declare_parameter<int>("baud_rate", 115200);
        declare_parameter<int>("frame_header", 0xAA);  
        declare_parameter<int>("frame_trailer", 0x55); 
        
        // 获取参数
        std::string device_name;
        int baud_rate;
        int frame_header_int, frame_trailer_int;
        
        get_parameter("device_name", device_name);
        get_parameter("baud_rate", baud_rate);
        get_parameter("frame_header", frame_header_int);
        get_parameter("frame_trailer", frame_trailer_int);
        
        // 转换为uint8_t
        frame_header_ = static_cast<uint8_t>(frame_header_int);
        frame_trailer_ = static_cast<uint8_t>(frame_trailer_int);

        // 串口配置
        // 波特率115200；不开启流控制；无奇偶效验；停止位1。
        drivers::serial_driver::SerialPortConfig config(
        baud_rate,
        drivers::serial_driver::FlowControl::NONE,
        drivers::serial_driver::Parity::NONE,
        drivers::serial_driver::StopBits::ONE);

        // 初始化串口
        try
        {
        io_context_ = std::make_shared<drivers::common::IoContext>(1);
        // 初始化 serial_driver_
        serial_driver_ = std::make_shared<drivers::serial_driver::SerialDriver>(*io_context_);
        serial_driver_->init_port(device_name, config);
        serial_driver_->port()->open();
        
        RCLCPP_INFO(this->get_logger(), "串口初始化成功");
        RCLCPP_INFO(this->get_logger(), "串口设备: %s", serial_driver_->port().get()->device_name().c_str());
        RCLCPP_INFO(this->get_logger(), "波特率: %d", config.get_baud_rate());
        }
        catch (const std::exception &ex)
        {
        RCLCPP_ERROR(this->get_logger(), "串口初始化失败: %s", ex.what());
        return;
        }

        //创建发布者(向ROS话题发布消息，从串口Serial_rx接受数据)
        serial_rx_pub_=this->create_publisher<std_msgs::msg::String>("serial_rx",10);
        //创建订阅者（从ROS话题订阅消息，向串口Serial_tx发送数据）
        serial_tx_sub_=this->create_subscription<std_msgs::msg::String>("serial_tx",10,std::bind(&SerialNode::send2serial,this,std::placeholders::_1));
        //创建定时器
        timer_=this->create_wall_timer(5ms,std::bind(&SerialNode::receive_from_serial,this));
        RCLCPP_INFO(this->get_logger(),"串口节点已开启");
    }
};

int main(int argc,char **argv)
{
    rclcpp::init(argc,argv);
    rclcpp::spin(std::make_shared<SerialNode>());
    rclcpp::shutdown();
    return 0;
}
