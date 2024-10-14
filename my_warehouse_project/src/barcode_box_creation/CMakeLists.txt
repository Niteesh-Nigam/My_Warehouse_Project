cmake_minimum_required(VERSION 3.8)
project(barcode_box_creation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)  # Ensure rclpy is found as a dependency for Python nodes

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # The following line skips the linter which checks for copyrights
  # Comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # The following line skips cpplint (only works in a git repo)
  # Comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Install Python scripts as executable nodes under lib/${PROJECT_NAME}
install(
  PROGRAMS
  barcode_box_creation/camera_cv2.py
  barcode_box_creation/generate_urdf1.py
  barcode_box_creation/main.py
  barcode_box_creation/prod_box.py
  launch/camera_launch.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files under share/${PROJECT_NAME}/launch
install(
  DIRECTORY launch barcode_box_creation
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()

