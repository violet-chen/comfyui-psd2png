from .nodes.psd2png import NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS 
import os
import shutil
import folder_paths
current_path = os.path.dirname(os.path.abspath(__file__))
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
gun_pngs = os.listdir(os.path.join(current_path,"images"))
gun_pngs_path = [os.path.join(current_path,"images",x) for x in gun_pngs]
input_folder_path = folder_paths.get_input_directory()
for gun_png_path in gun_pngs_path:
    print(gun_png_path)
    gun_png_name = os.path.split(gun_png_path)[1]
    input_gun_png_path = os.path.join(input_folder_path,gun_png_name)
    if os.path.exists(input_gun_png_path):
        os.remove(input_gun_png_path)
        shutil.copy2(gun_png_path,input_gun_png_path)
    else:
        shutil.copy2(gun_png_path,input_gun_png_path)