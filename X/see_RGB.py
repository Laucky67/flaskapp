import time
import cv2
import os
import matplotlib.pyplot as plt
import tifffile
import torch
from PIL import Image
from tifffile import imread
import numpy as np
import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2
from X.net import unet_x


# 去黑边函数
def remove_the_blackborder(image):
    image = cv2.imread(image)  # 读取图片
    img = cv2.medianBlur(image, 5)  # 中值滤波，去除黑色边际中可能含有的噪声干扰
    b = cv2.threshold(img, 3, 255, cv2.THRESH_BINARY)  # 调整裁剪效果
    binary_image = b[1]  # 二值图--具有三通道
    binary_image = cv2.cvtColor(binary_image, cv2.COLOR_BGR2GRAY)
    # print(binary_image.shape)     #改为单通道

    edges_y, edges_x = np.where(binary_image == 255)  ##h, w
    bottom = min(edges_y)
    top = max(edges_y)
    height = top - bottom

    left = min(edges_x)
    right = max(edges_x)
    height = top - bottom
    width = right - left

    res_image = image[bottom:bottom + height, left:left + width]

    plt.figure()
    plt.subplot(1, 2, 1)
    plt.imshow(image)
    plt.subplot(1, 2, 2)
    plt.imshow(res_image)
    # plt.savefig(os.path.join("res_combine.jpg"))
    plt.show()
    return res_image


# 预测函数
def split_and_reconstruct_rgb(image_path, block_size, step_size, model):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # pth = r"C:\Users\xmy_2\Desktop\fsdownload\model--AttU_Net-150-2024-03-09-21_54_04.pth"
    pth = r"X/pth/model--UNet_X-best-2024-03-23-16_37_32.pth"
    model = unet_x.UNet_X(3, 7 + 1).cuda()
    model.load_state_dict(torch.load(pth))
    model = model.to(device)
    model.eval()  # 将模型设置为评估模式
    # 读取图像
    input_image = Image.open(image_path)  # 替换成你的输入图像文件名
    print("input_image:", input_image)
    # 检查图像模式，如果是RGBA
    if input_image.mode == 'RGBA':
        # 转换为RGB模式，丢弃Alpha通道
        img_rgb = input_image.convert('RGB')
    else:
        # 图像已经是RGB或者某种其他非RGBA模式，无需转换
        img_rgb = input_image
    image = np.array(img_rgb)

    # 图像的原始宽度和高度
    original_h, original_w, _ = image.shape

    # 计算需要增加的宽度和高度
    padding_right = block_size[0] - (original_w % block_size[0]) if original_w % block_size[0] != 0 else 0
    padding_bottom = block_size[1] - (original_h % block_size[1]) if original_h % block_size[1] != 0 else 0

    # 创建一个用于填充的新数组
    pad_width = ((0, padding_bottom), (0, padding_right), (0, 0))
    image = np.pad(image, pad_width=pad_width, mode='constant', constant_values=0)

    # 图像的宽度和高度
    h, w, _ = image.shape

    # 计算水平和垂直方向上可以切分的块数
    x_blocks = (w - block_size[0]) // step_size + 1
    y_blocks = (h - block_size[1]) // step_size + 1
    number = y_blocks * x_blocks
    num = 0
    print(f"the number is {h}")
    print(f"the number is {w}")
    print(f"the number is {x_blocks}")
    print(f"the number is {y_blocks}")
    print(f"the number is {number}")
    # 初始化一个新的图像来存放重构的图像
    reconstructed_image = np.zeros_like(image).astype(np.uint8)
    # 创建一个掩码来跟踪哪些像素已经被赋值
    assigned_mask = np.zeros_like(reconstructed_image, dtype=bool)
    # 遍历每个块并重构图像
    for i in range(y_blocks):
        for j in range(x_blocks):
            # 计算当前块的位置
            x_start = j * step_size
            y_start = i * step_size
            x_end = x_start + block_size[0]
            y_end = y_start + block_size[1]
            print(y_start, y_end, x_start, x_end)
            # 获取当前块
            # block = image[y_start:y_end, x_start:x_end]
            # 获取当前块
            block = image[y_start:y_end, x_start:x_end]
            print(block.shape)
            # block = block.transpose((2, 0, 1))  # 将通道维度从最后移到第一，变为(channels, height, width)
            # print("newBlock:", block.shape)
            colour_i = "  "
            classes = ["None", "Background", "Building", "Road", "Water", "Barren", "Forest", "Agriculture"]
            colormap = [[0, 0, 0], [255, 255, 255], [180, 30, 30], [100, 100, 100], [0, 0, 255], [220, 220, 220],
                        [34, 139, 34], [255, 215, 0],
                        ]

            transform = A.Compose([
                A.Resize(512, 512),
                A.Normalize(),
                ToTensorV2(),
            ])

            input_image = transform(image=block)
            input_image = input_image['image'].unsqueeze(0).to(device)
            output = model(input_image)
            output = torch.sigmoid(output)
            output = torch.argmax(output, dim=1)
            output_np = output.cpu().detach().numpy().copy()

            mask = output_np.squeeze()
            mask = np.uint8(mask)

            colored_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
            for i0 in range(len(classes)):
                colored_mask[mask == i0] = colormap[i0]

            # 使用PIL的Image.fromarray()方法将NumPy数组转换为PIL图像
            if colour_i != " ":
                image_out = Image.fromarray(colored_mask)
            else:
                image_out = Image.fromarray(mask)
            #
            # 将NumPy数组转换为PIL图像
            image_out = np.array(image_out)
            # 使用掩码来确定是使用按位或还是按位与
            update_mask = assigned_mask[y_start:y_end, x_start:x_end]
            reconstructed_image[y_start:y_end, x_start:x_end][update_mask] = np.bitwise_and(
                reconstructed_image[y_start:y_end, x_start:x_end][update_mask], image_out[update_mask]
            )
            reconstructed_image[y_start:y_end, x_start:x_end][~update_mask] = np.bitwise_or(
                reconstructed_image[y_start:y_end, x_start:x_end][~update_mask], image_out[~update_mask]
            )

            # 更新assigned_mask
            assigned_mask[y_start:y_end, x_start:x_end] = True

            num = num + 1

            print(f'finish {num}')
            print(f'finish {num / number:.3f}')

    # 将NumPy数组转换为PIL图像
    image = Image.fromarray(reconstructed_image)

    # 保存图像到文件，例如保存为'output.png'
    path = 'static/image/result/classification_result.png'
    image.save(path)
    remove_black = remove_the_blackborder(path)
    cv2.imwrite(path, remove_black)
    return path


# '''E:\arcgis_objects\冰川\tntw_sj0.tif'''
now0 = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))

