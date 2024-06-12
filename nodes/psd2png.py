from PIL import Image,ImageOps
import os
import folder_paths
from psd_tools.api.layers import Layer
from psd_tools import PSDImage
import numpy as np
import torch
import hashlib
from pathlib import Path

class Psd2PngNode:
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return{
            "required":{
                "image": (sorted(files), {"image_upload": True}),
                "psd_path": ("STRING",{"default": "C:/example.psd"}),
                "layer_index": ("INT",{"default": 0,"min": 0,"max": 999,"step": 1}),
            },
        }
    
    RETURN_TYPES= ("IMAGE","IMAGE","IMAGE","MASK","FLOAT",)
    RETURN_NAMES = ("image","top_image","bottom_image","mask","is_exist_layer",)
    FUNCTION = "psd2png"
    CATEGORY = "image"

    def get_image_and_mask(self,psd_image,layer_list,layer_number):
        mask_out = None
        layer_image = layer_list[layer_number].compose()
        layer_obj = layer_list[layer_number]
        # 创建一个空白画布
        canvas_size = (int(psd_image.width),int(psd_image.height))
        canvas_image_obj = Image.new('RGBA',canvas_size,(0,0,0,0))
        # 将图层复制到新画布上
        layer_bbox = layer_obj.bbox
        offset = (layer_bbox[0],layer_bbox[1])
        canvas_image_obj.paste(layer_image,offset)
        image_out = canvas_image_obj.convert("RGBA")
        image_out = np.array(image_out).astype(np.float32) / 255.0
        image_out = torch.from_numpy(image_out)[None,]
        if 'A' in canvas_image_obj.getbands():
            mask = np.array(canvas_image_obj.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
        mask_out = mask.unsqueeze(0)
        return image_out,mask_out

    def psd2png(self,image,psd_path,layer_index):
        if psd_path == "C:/example.psd":
            file_path = Path(folder_paths.get_annotated_filepath(image))
        else:
            file_path = Path(psd_path)
        i = Image.open(file_path)
        input_image = i.convert("RGB")
        input_image = np.array(input_image).astype(np.float32) / 255.0
        input_image = torch.from_numpy(input_image)[None,]
        top_image = None
        bottom_image = None
        mask_out = None
        is_exist_layer = 1.0
        if file_path.suffix == ".psd":  
            psd_image= PSDImage.open(file_path)
            layer_list=[layer for layer in psd_image.descendants() if isinstance(layer, Layer)]
            top_layer_number = len(layer_list) - 1
            if layer_index == 0:
                image_out = input_image
                mask_out = torch.zeros((64,64), dtype=torch.float32, device="cpu").unsqueeze(0)
                top_image = self.get_image_and_mask(psd_image,layer_list,top_layer_number)[0]
                bottom_image = self.get_image_and_mask(psd_image,layer_list,0)[0]
            elif len(layer_list) == 1:
                top_image,mask_out = bottom_image,mask_out = self.get_image_and_mask(psd_image,layer_list,0)
                bottom_image = top_image
                image_out = top_image
            elif len(layer_list) > 1:
                top_image,mask_out = self.get_image_and_mask(psd_image,layer_list,top_layer_number)
                bottom_image = self.get_image_and_mask(psd_image,layer_list,0)[0]
                if (layer_index-1) > top_layer_number:
                    image_out = top_image
                    is_exist_layer = 0.0
                else:
                    image_out,mask_out = self.get_image_and_mask(psd_image,layer_list,layer_index-1)
        else:
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            image_out = input_image
            mask_out = mask.unsqueeze(0)

        return(image_out,top_image,bottom_image,mask_out,is_exist_layer)
    
    @classmethod
    def IS_CHANGED(s, image,psd_path,layer_index):
        if psd_path == "C:/example.psd":
            file_path = Path(folder_paths.get_annotated_filepath(image))
        else:
            file_path = Path(psd_path)
        m = hashlib.sha256()
        with open(file_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()
    
NODE_CLASS_MAPPINGS  = {
    "Psd2Png":Psd2PngNode,
    }
NODE_DISPLAY_NAME_MAPPINGS  = {
    "Psd2Png":"Psd2Png",
    }

