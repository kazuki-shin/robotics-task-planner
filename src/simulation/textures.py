import numpy as np
from PIL import Image
import os

def create_checker_texture(color=(0, 0, 255), size=512):
    """Create a checker pattern texture"""
    # Create checker pattern
    pattern = np.zeros((size, size, 3), dtype=np.uint8)
    cell_size = size // 8
    
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 0:
                pattern[i*cell_size:(i+1)*cell_size, 
                       j*cell_size:(j+1)*cell_size] = color
    
    return pattern

def ensure_textures():
    """Ensure texture files exist"""
    textures_dir = os.path.join(os.path.dirname(__file__), 'textures')
    os.makedirs(textures_dir, exist_ok=True)
    
    # Create blue checker texture if it doesn't exist
    texture_path = os.path.join(textures_dir, 'checker_blue.png')
    if not os.path.exists(texture_path):
        pattern = create_checker_texture()
        img = Image.fromarray(pattern)
        img.save(texture_path) 