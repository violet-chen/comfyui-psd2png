from PIL import Image,ImageOps
import os
import folder_paths
from psd_tools.api.layers import Layer
from psd_tools import PSDImage
import numpy as np
import torch
class Psd2PngNode:
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        img_files = []
        for input_file in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, input_file)):
                img_files.append(input_file)
        return{
            "required":{
                "image":(sorted(img_files),{"psd_upload": True})
                },
        }
    
    RETURN_TYPES= ("IMAGE","MASK",)

    FUNCTION = "psd2png"
    CATEGORY = "image"

    def psd2png(self,image):
        if image.endswith(".psd"):
            psd_path = folder_paths.get_annotated_filepath(image)
            i = Image.open(psd_path)
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            psd_image= PSDImage.open(psd_path)
            layer_list=[layer for layer in psd_image.descendants() if isinstance(layer, Layer)]
            if len(layer_list) > 0:
                layer_number = len(layer_list) - 1
                top_layer_image=layer_list[layer_number].compose()
                top_layer = layer_list[layer_number]
                # 创建一个空白画布，
                canvas_size =(int(psd_image.width), int(psd_image.height))
                canvas_image = Image.new('RGBA',canvas_size , (0, 0, 0, 0))
                # 将 "遮罩” 层复制到这个新的空白画布上 
                top_layer_bbox = top_layer.bbox
                offset=(top_layer_bbox[0], top_layer_bbox[1])
                canvas_image.paste(top_layer_image ,offset)             
                if 'A' in canvas_image.getbands():
                    mask = np.array(canvas_image.getchannel('A')).astype(np.float32) / 255.0
                    mask = 1. - torch.from_numpy(mask)
                else:
                    mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
                mask_out = mask.unsqueeze(0)
        else:
            image_path = folder_paths.get_annotated_filepath(image)
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            mask_out = mask.unsqueeze(0)

        return(image,mask_out)
    
NODE_CLASS_MAPPINGS  = {
    "Psd2Png":Psd2PngNode
    }
NODE_DISPLAY_NAME_MAPPINGS  = {
    "Psd2Png":"Psd2Png"
    }

