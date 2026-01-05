import torch
import numpy as np
from PIL import Image
import folder_paths
import os
import random
import json

class SimpleDisplayNode:
    """
    A ComfyUI node that inspects any input and displays its details (metadata, shape, etc.)
    and a preview if it is an image tensor.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any_input": ("*",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text_info",)
    FUNCTION = "analyze_and_display"
    CATEGORY = "Learning/Debug"
    OUTPUT_NODE = True

    def analyze_and_display(self, any_input):
        # 1. Analyze the text/metadata
        text_info = self._get_details(any_input)

        # 2. Prepare the UI payload
        ui_payload = {"text": [text_info]}

        # 3. Check if it is an image/video and save a preview
        if isinstance(any_input, torch.Tensor):
            # Check if it looks like an image [B, H, W, C]
            # Heuristic: 4 dims, last dim is 1, 3, or 4 (channels)
            if any_input.ndim == 4 and any_input.shape[-1] in [1, 3, 4]:
                preview_filename = self._save_preview(any_input)
                if preview_filename:
                    # Append image data to the payload
                    ui_payload["images"] = [{
                        "filename": preview_filename,
                        "type": "temp",
                        "subfolder": ""
                    }]

        return {"ui": ui_payload, "result": (text_info,)}

    @staticmethod
    def _save_preview(tensor):
        try:
            # Convert Tensor (0.0-1.0) to Numpy (0-255 uint8)
            # Clip values to ensure valid color range
            img_np = 255. * tensor.cpu().numpy()
            img_np = np.clip(img_np, 0, 255).astype(np.uint8)

            # Convert to PIL Images
            images = []
            for i in range(img_np.shape[0]):
                # Handle 1-channel (grayscale) images
                if img_np.shape[-1] == 1:
                    img = Image.fromarray(img_np[i].squeeze(-1), mode="L")
                else:
                    img = Image.fromarray(img_np[i])
                images.append(img)

            if not images:
                return None

            # Generate a random filename in the temp folder
            output_dir = folder_paths.get_temp_directory()
            filename = f"debug_preview_{random.randint(100000, 999999)}.webp"
            file_path = os.path.join(output_dir, filename)

            # Save: If batch size > 1, save as animated WEBP (Video)
            if len(images) > 1:
                images[0].save(
                    file_path,
                    save_all=True,
                    append_images=images[1:],
                    duration=100,  # 100ms per frame = 10fps
                    loop=0,
                    format="WEBP"
                )
            else:
                images[0].save(file_path, format="WEBP")

            return filename
        except Exception as e:
            print(f"SimpleDisplayNode: Failed to save preview: {e}")
            return None

    @staticmethod
    def _get_details(data):
        try:
            if isinstance(data, torch.Tensor):
                info = (
                    f"Type: torch.Tensor\n"
                    f"Shape: {list(data.shape)}\n"
                    f"Dtype: {data.dtype}\n"
                    f"Device: {data.device}\n"
                    f"Range: {data.min():.2f} to {data.max():.2f}\n"
                    f"Mean: {data.mean():.2f}, Std: {data.std():.2f}"
                )
                return info
            
            elif isinstance(data, (int, float, bool, str)):
                return f"Type: {type(data).__name__}\nValue: {data}"
            
            elif isinstance(data, list):
                return f"Type: List\nLength: {len(data)}\nSample: {str(data)[:200]}..."
            
            elif isinstance(data, dict):
                return f"Type: Dict\nKeys: {list(data.keys())}\nSample: {str(data)[:200]}..."
            
            elif data is None:
                return "Type: NoneType\nValue: None"
            
            else:
                # Fallback for other objects
                return f"Type: {type(data).__name__}\nString Rep: {str(data)[:500]}"
                
        except Exception as e:
            return f"Error analyzing data: {e}"
