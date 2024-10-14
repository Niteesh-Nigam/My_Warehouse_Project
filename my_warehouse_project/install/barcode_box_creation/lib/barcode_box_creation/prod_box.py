import pandas as pd
import barcode
from barcode.writer import ImageWriter
import os
import re
import random
from barcode import Code39

def select_random_products(file_path, number_of_products):
    # Load the product data
    data = pd.read_csv(file_path)
    
    # Randomly select four products
    selected_products = data.sample(number_of_products)
    
    # Retrieve and return the selected product details
    product_details = selected_products[['Product', 'Width (m)', 'Length (m)', 'Height (m)', 'Weight (kg)']]
    return product_details


def create_box_dim(selected_products):
    # Calculate the required dimensions for the box
    total_width = selected_products['Width (m)'].sum()
    max_length = selected_products['Length (m)'].max()
    max_height = selected_products['Height (m)'].max()
    total_weight = selected_products['Weight (kg)'].sum()

    # Return the dimensions
    return total_width, max_length, max_height,total_weight


# def generate_barcode(existing_barcodes):
#     # Generate a random 12-digit barcode number
#     while True:
#         random_barcode = str(random.randint(1000000000000, 9999999999999))  # 12-digit number
#         if random_barcode not in existing_barcodes:
#             break

#     # Ensure the barcode class is available
#     hr = barcode.get_barcode_class('code39')
#     # if hr is None:
#     #     raise ValueError("Failed to load the 'code39' barcode class.")
    
#     # Create the barcode object
#     barcode_obj = hr(random_barcode, writer=ImageWriter(), add_checksum=False)
    
#     # # Save the barcode image (optional)
#     barcode_obj.save(random_barcode)

#     return random_barcode
def save_barcode(random_barcode, barcode_obj,textures_directory):

    barcode_image_path = os.path.join(textures_directory, f"{random_barcode}")
    
    # Save the barcode image in the textures directory
    barcode_obj.save(barcode_image_path)

def create_barcode_and_append_csv(product_names, output_csv):
    # Check if CSV file exists and read existing barcodes
    if os.path.exists(output_csv):
        existing_data = pd.read_csv(output_csv)
        existing_barcodes = set(existing_data['Barcode'])
    else:
        existing_barcodes = set()
    
    # Generate a random 12-digit barcode number
    while True:
        random_barcode = str(random.randint(1000000000000, 9999999999999))  # 12-digit number
        if random_barcode not in existing_barcodes:
            break

    # Ensure the barcode class is available
    hr = barcode.get_barcode_class('code39')
    # if hr is None:
    #     raise ValueError("Failed to load the 'code39' barcode class.")
    
    # Create the barcode object
    barcode_obj = hr(random_barcode, writer=ImageWriter(), add_checksum=False)
    
    # barcode_image_path = os.path.join(textures_directory, f"{random_barcode}")
    
    # # Save the barcode image in the textures directory
    # barcode_obj.save(barcode_image_path)
    
    # Create the new data to be appended
    barcode_data = {
        'Barcode': [random_barcode],
        'Products': [", ".join(product_names)]
    }
    
    # Convert to DataFrame
    df_new_entry = pd.DataFrame(barcode_data)
    
    # Append to the existing CSV or create a new one
    if os.path.exists(output_csv):
        df_new_entry.to_csv(output_csv, mode='a', header=False, index=False)
    else:
        df_new_entry.to_csv(output_csv, index=False)
    
    return random_barcode, barcode_obj

def generate_material_script(barcode_number, script_directory):
    # Define the material script content
    material_script = f"""material {barcode_number}
{{
    technique
    {{
        pass
        {{
            texture_unit
            {{
                texture {barcode_number}.png
            }}
        }}
    }}
}}
"""
    material_file_path = os.path.join(script_directory, f"{barcode_number}.material")

    # Write the material script to the file
    with open(material_file_path, "w") as file:
        file.write(material_script)

def generate_config(barcode_number, config_path):
    # Define the material script content
    config_script = f"""<?xml version="1.0" ?>
<model>
  <name>{barcode_number}</name>
  <version>1.0</version>
  <sdf version="1.6">{barcode_number}.sdf</sdf>
  <author>
    <name>Niteesh Nigam</name>
    <email>niteesh.nigam99@gmail.com</email>
  </author>
  <description>
    Delivery box texture config
  </description>
</model>
"""
    config_file_path = os.path.join(config_path, f"{barcode_number}.config")

    # Write the material script to the file
    with open(config_file_path, "w") as file:
        file.write(config_script)