def generate_urdf(box_width, box_length, box_height, total_weight, sdf_file,barcode_number):

  box_mass = total_weight/9.8
    
  ixx=(box_mass/12) * (box_height*box_height + box_length*box_length)
  ixy=0
  ixz=0
  iyy=(box_mass/12) * (box_width*box_width + box_length*box_length)
  iyz=0
  izz=(box_mass/12) * (box_width*box_width + box_height*box_height)

  urdf_template = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="{barcode_number}">
    <static>false</static>  <!-- Ensure the model is dynamic -->

    <link name="box_link">
      <!-- Inertial properties -->
      <inertial>
        <mass>0.0843</mass>
        <inertia>
          <ixx>0.000020352</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.000031373</iyy>
          <iyz>0</iyz>
          <izz>0.000036967</izz>
        </inertia>
      </inertial>

      <!-- Collision Properties -->
      <collision name="box_collision">
        <pose>0 0 0 0 0 0</pose>  <!-- Aligned with the box -->
        <geometry>
          <box>
            <size>0.229751 0.162283 0.113616</size>  <!-- Same size as the box -->
          </box>
        </geometry>
        <surface>
          <friction>
            <ode>
              <mu>1.0</mu>
              <mu2>1.0</mu2>
            </ode>
          </friction>
          <contact>
            <ode>
              <soft_cfm>0.0</soft_cfm>
              <soft_erp>0.2</soft_erp>
            </ode>
          </contact>
        </surface>
      </collision>

      <!-- Visual for the Box -->
      <visual name="box_visual">
        <pose>0 0 0 0 0 0</pose>  <!-- Align with collision -->
        <geometry>
          <box>
            <size>{box_width/4} {box_length/4} 0.113616</size>
          </box>
        </geometry>
        <material>
          <ambient>1 0.5 0 1</ambient>  <!-- Orange color -->
          <diffuse>1 0.5 0 1</diffuse>
        </material>
      </visual>

      <!-- Barcode Visual (Slightly Above Top Face to Avoid Interference) -->
      <visual name="barcode_visual">
        <pose>0 0 0.057 0 0 0</pose>  <!-- Slightly offset to avoid z-fighting -->
        <geometry>
          <plane>
            <size>0.2 0.15</size>  <!-- Adjust size to fit box top -->
          </plane>
        </geometry>
        <material>
          <script>
            <uri>model://{barcode_number}/materials/scripts</uri>
            <uri>model://{barcode_number}/materials/textures</uri>
            <name>{barcode_number}</name>
          </script>
        </material>
      </visual>

      <!-- Physics Settings -->
      <gravity>1</gravity>
      <self_collide>false</self_collide>  <!-- No self-collision -->
      <kinematic>false</kinematic>  <!-- Make the object dynamic -->
      <enable_wind>false</enable_wind>
    </link>

    <!-- Model Configuration -->
    <pose>-1.0 0.4 0.8 0 0 3.14</pose>  <!-- Initial spawn location -->
    <allow_auto_disable>false</allow_auto_disable>  <!-- Keep physics active -->
  </model>
</sdf>
"""
    
    # Write the URDF content to a file
  with open(sdf_file, "w") as file:
      file.write(urdf_template)

  print(f"URDF file written to {sdf_file}")


# # Example usage:
# box_width = 0.68  # Replace with actual width from your Python code
# box_length = 1.2  # Replace with actual length from your Python code
# box_height = 0.4  # Replace with actual height from your Python code
# box_mass = 5.0    # Replace with actual mass from your Python code

# # sdf_file = "box_model.urdf"
# # generate_urdf(box_width, box_length, box_height, box_mass, sdf_file)
