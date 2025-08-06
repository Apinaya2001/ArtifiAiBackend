# import torch
# from torch import nn
# from PIL import Image
# from torchvision import transforms
# import os

# # ✅ 1. Define a dummy model matching the checkpoint (example structure)
# class SimpleGhibliModel(nn.Module):
#     def __init__(self):
#         super(SimpleGhibliModel, self).__init__()
#         # This is a placeholder. You MUST match the actual model used in training.
#         self.conv = nn.Conv2d(3, 3, kernel_size=3, padding=1)

#     def forward(self, x):
#         return self.conv(x)

# # ✅ 2. Load the state_dict into the model
# def load_ghibli_model():
#     model = SimpleGhibliModel()  # Replace with actual architecture if known
#     state_dict = torch.load("styletransfer/model/ghibli-diffusion-v1.ckpt", map_location="cpu")
    
#     if "state_dict" in state_dict:
#         state_dict = state_dict["state_dict"]
    
#     # Optionally remove "model." prefix if exists
#     new_state_dict = {}
#     for k, v in state_dict.items():
#         new_k = k.replace("model.", "") if k.startswith("model.") else k
#         new_state_dict[new_k] = v

#     model.load_state_dict(new_state_dict, strict=False)
#     model.eval()
#     return model

# # ✅ 3. Run inference
# def run_ghibli_style_transfer(input_path, output_path):
#     model = load_ghibli_model()

#     image = Image.open(input_path).convert("RGB")
#     transform = transforms.Compose([
#         transforms.Resize((512, 512)),
#         transforms.ToTensor(),
#     ])
#     input_tensor = transform(image).unsqueeze(0)

#     with torch.no_grad():
#         output_tensor = model(input_tensor)[0]

#     output_image = transforms.ToPILImage()(output_tensor.clamp(0, 1))
#     output_image.save(output_path)
#     print(f"✅ Ghibli-style image saved to: {output_path}")

# # ✅ 4. Test
# if __name__ == "__main__":
#     input_img = "media/input/0ff0c406302f4da09eadbfc7dd539664_anime_raw.jpg"  # Replace with real image path
#     output_img = "media/output/ghibli_output.jpg"
#     os.makedirs("media/output", exist_ok=True)
#     run_ghibli_style_transfer(input_img, output_img)

# styletransfer/ghibli_inference.py

from diffusers import StableDiffusionPipeline
from PIL import Image
import torch
import os

def run_ghibli_style(prompt: str, output_path: str = "media/output/ghibli_output.jpg"):
    # Load the Ghibli Diffusion model
    print("🔄 Loading Ghibli Diffusion pipeline...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "nitrosocke/Ghibli-Diffusion",
        torch_dtype=torch.float32
    ).to("cpu")

    # Generate image from prompt
    print(f"🖌️ Generating image for prompt: '{prompt}'")
    image = pipe(prompt).images[0]

    # Save output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)
    print(f"✅ Ghibli-style image saved to: {output_path}")


if __name__ == "__main__":
    # Example usage
    prompt = "A cute child in studio ghibli style, vibrant colors, beautiful background"
    run_ghibli_style(prompt)
