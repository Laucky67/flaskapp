import time
import re
import tifffile
import torch
from PIL import Image
from osgeo import gdal
from tifffile import imread
from X.net import Attention_Unet
# from net.attention.Attention_Unet import AttU_Net
from image_process import tif_to_png_
import numpy as np
import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2
from X.net import unet_x


def split_and_reconstruct(image_path, block_size, step_size, modelname):
    # image_path = image_path
    # image_path = "image/dc_b6_1_CompositeBands1.tif"
    print(image_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if modelname == "attention_unet":  # 调用注意力unet
        pth = r"X/pth/model--AttU_Net-best-2024-03-10-11_10_06.pth"
        model = Attention_Unet.AttU_Net(3, 2 + 1).to(device)
        model.load_state_dict(torch.load(pth, map_location=device))
    elif modelname == "unet_x":  # 调用徐unet
        pth = r"X/pth/model--UNet_X-best-2024-03-23-16_37_32.pth"
        # 确保out_channels与预训练模型的输出通道数匹配
        out_channels = 7 # 根据实际情况调整
        model = unet_x.UNet_X(3, out_channels + 1).cuda()
        model.load_state_dict(torch.load(pth))

    # 使用gdal加载文件
    dataset = gdal.Open(image_path)
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    # 读取图像
    image = imread(image_path).astype(np.float32)
    h, w, _ = image.shape
    x_blocks = (w - block_size[0]) // step_size + 1
    y_blocks = (h - block_size[1]) // step_size + 1
    reconstructed_image = np.zeros_like(image).astype(np.uint8)
    assigned_mask = np.zeros_like(reconstructed_image, dtype=bool)

    # 读取图像
    image = imread(image_path).astype(np.float32)
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
            block = image[y_start:y_end, x_start:x_end]
            colour_i = "  "
            classes = ["background", "lake", "vally"]
            colormap = [[0, 0, 0], [192, 64, 128], [255, 255, 255]]

            transform = A.Compose([
                # A.Normalize(),
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

    # 重构后，将图像保存为GeoTIFF
    match = re.search(r'result/(.*?).tif', image_path)
    # 如果匹配成功，提取文件名
    if match:
        file_name = match.group(1)
        print(file_name)  # 输出: file_process
    else:
        print("No match found")
        return EOFError

    output_path = "static/image/result/" + file_name + "_result.tif"
    driver = gdal.GetDriverByName('GTiff')
    out_dataset = driver.Create(output_path, w, h, 3, gdal.GDT_Byte)
    out_dataset.SetGeoTransform(geotransform)
    out_dataset.SetProjection(projection)

    for i in range(3):  # 假设图像有三个通道（RGB）
        out_dataset.GetRasterBand(i + 1).WriteArray(reconstructed_image[:, :, i])

    out_dataset.FlushCache()  # 写入磁盘
    del out_dataset  # 关闭文件
    print(output_path)
    # 转换文件格式
    result_path = tif_to_png_(output_path,'multimoding_result')
    print(result_path)
    return result_path


# '''E:\arcgis_objects\冰川\tntw_sj0.tif'''
now0 = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))

