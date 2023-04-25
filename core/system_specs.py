from typing import Dict
import torch
import torchvision


def get_specs() -> Dict[str, str]:
    return {
        "pytorch": torch.__version__,
        "torchvision": torchvision.__version__,
        "CUDA": torch.cuda.is_available()
    }
