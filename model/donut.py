from donut import DonutModel
from PIL import Image
import torch

model = DonutModel.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")

if torch.cuda.is_available():
    model.half()
    device = torch.device("cuda")
    model.to(device)
else:
    device = torch.device("cpu")
    model.encoder.to(torch.float)
    model.to(device)

model.eval() 

def process(path):
    image = Image.open(path).convert("RGB")
    output = model.inference(image=image, prompt="<s_cord-v2>")

    return output

def test():
    print("*"*3000)
