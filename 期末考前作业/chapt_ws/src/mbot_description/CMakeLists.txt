cmake_minimum_required(VERSION 3.8)
project(mbot_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf meshes launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
