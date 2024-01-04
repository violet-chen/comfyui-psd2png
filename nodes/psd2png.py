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
                "filename":(sorted(img_files),{"psd_upload": True})
                },
        }
    
    RETURN_TYPES= ("IMAGE","IMAGE","IMAGE","MASK",)
    RETURN_NAMES = ("image","top_image","bottom_image","mask",)
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
        image = canvas_image_obj.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if 'A' in canvas_image_obj.getbands():
            mask = np.array(canvas_image_obj.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
        mask_out = mask.unsqueeze(0)
        return image,mask_out

    def psd2png(self,filename):
        file_path = folder_paths.get_annotated_filepath(filename)
        i = Image.open(file_path)
        i = ImageOps.exif_transpose(i)
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        top_image = None
        bottom_image = None
        mask_out = None
        if filename.endswith(".psd"):  
            psd_image= PSDImage.open(file_path)
            layer_list=[layer for layer in psd_image.descendants() if isinstance(layer, Layer)]
            if len(layer_list) == 1:
                top_image,mask_out = bottom_image,mask_out = self.get_image_and_mask(psd_image,layer_list,0)
                top_image = self.get_image_and_mask(psd_image,layer_list,0)[0]
                bottom_image = top_image
                mask_out = self.get_image_and_mask(psd_image,layer_list,0)[1]
            elif len(layer_list) > 1:
                top_layer_number = len(layer_list) - 1
                top_image,mask_out = self.get_image_and_mask(psd_image,layer_list,top_layer_number)
                bottom_image = self.get_image_and_mask(psd_image,layer_list,0)[0]
        else:
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            mask_out = mask.unsqueeze(0)

        return(image,top_image,bottom_image,mask_out)
    
NODE_CLASS_MAPPINGS  = {
    "Psd2Png":Psd2PngNode
    }
NODE_DISPLAY_NAME_MAPPINGS  = {
    "Psd2Png":"Psd2Png"
    }

