import numpy as np
from prod_box import *
import os
from generate_urdf1 import *
import pandas as pd

number_of_orders = 8
number_of_products = 4
inventory_path = os.path.join('/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/inventory_list.csv')
output_csv = '/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/barcode_product_list.csv'
# textures_directory = "/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/materials/textures/"
# script_directory = "/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/materials/scripts/"

if not os.path.exists(output_csv):
    # If the file doesn't exist, set existing_entries to 0
    print(f"{output_csv} does not exist. Setting existing_entries to 0.")
    existing_entries = 0
else:
    # If the file exists, read it and set existing_entries based on its length
    df = pd.read_csv(output_csv)
    existing_entries = len(df)


for i in range(number_of_orders):  # Let's say you want 5 orders
    selected_products = select_random_products(inventory_path,number_of_products)
    print("Selected Products:\n", selected_products)
    
    product_names = selected_products['Product'].tolist()

    random_barcode , barcode_obj= create_barcode_and_append_csv(product_names, output_csv)
    textures_directory = f"/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/models/{random_barcode}/materials/textures/"
    os.makedirs(textures_directory, exist_ok=True)
    # random_barcode , barcode_obj= create_barcode_and_append_csv(product_names, output_csv,textures_directory)
    save_barcode(random_barcode, barcode_obj,textures_directory)

    # textures_directory = f"/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/models/{random_barcode}/materials/textures/"
    script_directory = f"/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/models/{random_barcode}/materials/scripts/"
    
    # Create the directories if they don't exist
    # os.makedirs(textures_directory, exist_ok=True)
    os.makedirs(script_directory, exist_ok=True)

    total_width, max_length, max_height, total_weight = create_box_dim(selected_products)
    print(f"New Order Created \n Barcode: {random_barcode}:, Box dimensions - Width: {total_width} m, Length: {max_length} m, Height: {max_height} m, Weight: {total_weight}kg")

    generate_material_script(random_barcode, script_directory)
    
    sdf_file = f"/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/models/{random_barcode}/{random_barcode}.sdf"
    generate_urdf(total_width, max_length, max_height, total_weight, sdf_file,random_barcode)

    config_path = f"/home/nitzz/my_warehouse_project/src/barcode_box_creation/barcode_box_creation/models/{random_barcode}"
    generate_config(random_barcode, config_path)
