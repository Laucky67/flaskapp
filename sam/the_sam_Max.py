# 导入必要的库函数
import io
import os
import matplotlib.colors as mcolors
import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
from sam.mobileSam import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
from PIL import Image, ImageDraw
from json import *
from flask import Flask, request, send_file, jsonify

plt.ioff()  # 禁用interactive mode


# 定义可视化函数
def show_mask(img_array, mask, random_color=False):
    # 定义掩膜颜色
    if random_color:
        color = np.random.randint(0, 256, 3)
    else:
        color = (255, 255, 255)  # 红色

    # 将掩膜应用到图像上
    masked_img = img_array.copy()
    masked_img[mask == 1] = color

    # Overlay mask on image
    overlaid_img = cv2.addWeighted(img_array.astype(np.uint8), 1, masked_img.astype(np.uint8), 1, 0)

    return overlaid_img


def show_points(image, coords, labels):
    for i, element in enumerate(coords):
        IN = labels[i]
        # 定义标记点的颜色和半径
        color = (0, 255, 0)  # 绿色
        radius = 5  # 半径大小
        # 绘制标记点
        cv2.circle(image, element, radius, color, -1)  # 最后一个参数-1表示填充圆圈


def save_mask_overlay(image_pth, point_list, label_list, output_dir="static/image/result/"):
    """
    适用于取点分割
    """
    # 显示一个机场的影像
    # image = cv2.imread('./test/test.jpg')
    image0 = cv2.imread(image_pth)
    image = cv2.cvtColor(image0, cv2.COLOR_BGR2RGB)

    # input_point = [[161.68633534, 72.98191204], [877.04076261, 201.13987133]]
    input_point = point_list
    input_point = np.array(input_point)
    '''例如[[161.68633534,72.98191204],[877.04076261,201.13987133]]'''
    # input_label = [1, 1]
    input_label = label_list
    input_label = np.array(input_label)
    '''例如[0,1]，0为负类，1为正类'''
    # load模型文件，定义预测模型为Sampredictor即交互式预测
    sam_checkpoint = "./SegmentAnything/weights/mobile_sam.pt"
    model_type = "vit_h"  # sam

    """
    sam_checkpoint = "./weights/mobile_sam.pt"
    model_type = "vit_t" # mobile_sam
    """

    device = "cuda" if torch.cuda.is_available() else "cpu"
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)
    predictor = SamPredictor(sam)
    predictor.set_image(image)  # embedding操作
    # 预测效率较高v100显卡大概3s完成预测
    masks, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True, )

    # plt.figure(figsize=(20, 15))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, (mask, score) in enumerate(zip(masks, scores)):
        # plt.figure(figsize=(10, 10))  # 调整figure大小以适应子图
        '''plt.subplot(1, 3, i + 1)
        plt.imshow(image)'''
        pic = show_mask(image0, mask)
        # show_points(input_point, input_label, plt.gca())
        # plt.title(f"Mask {i + 1}, Score: {score:.3f}", fontsize=18)
        '''plt.axis('off')

        # 将matplotlib Figure转换为RGB格式的numpy数组
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
        buffer.seek(0)
        pil_image = Image.open(buffer)'''
        # OpenCV中的颜色顺序是BGR(A)，所以我们需要先将其转换为BGRA
        # bgra_matrix = pic[..., [2, 1, 0, 3]]  # 交换R和B通道的位置
        # 将PIL Image保存为PNG文件
        output_file_path = os.path.join(output_dir, f"mask_{i + 1}.png")
        cv2.imwrite(output_file_path, pic)
        return output_file_path
        # pic.save(output_file_path)


# 实例分割的掩膜是由多个多边形组成的，可以通过下面的函数将掩膜显示在图片上
def show_anns(image, masks):
    if len(masks) == 0:
        return image

    sorted_masks = sorted(masks, key=lambda x: np.sum(x['segmentation']), reverse=True)
    overlay = image.copy()

    for mask_dict in sorted_masks:
        mask = mask_dict['segmentation']
        color_mask = np.random.randint(0, 256, 3)  # 随机生成颜色
        color_mask = color_mask.astype(np.uint8)
        overlay[mask == 1] = color_mask

    # Overlay mask on image
    overlaid_img = cv2.addWeighted(image.astype(np.uint8), 1, overlay.astype(np.uint8), 0.6, 0)
    return overlaid_img


# atuo_split函数用于对图像进行自动分割
def sam_atuo_split(image_pth, output_dir="static/image/result/"):
    """
    适用于自主分割
    """
    # 使用split()方法分割URL
    print(image_pth)
    parts = image_pth.split('/')
    path = '/'.join(parts[-2:])

    print(path)

    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sam_checkpoint ="sam/SegmentAnything/weights/mobile_sam.pt"
    # model_type = "vit_h"  # sam
    model_type = "vit_b"
    # sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)
    mask_generator = SamAutomaticMaskGenerator(sam)
    masks = mask_generator.generate(image)

    # 此时masks包含多种信息，segmentation', 'area', 'bbox', 'predicted_iou', 'point_coords', 'stability_score',
    # 'crop_box'分别代表掩膜文件、多边形、坐标框、iou、采样点、得分、裁剪框
    print(len(masks))  # 多边形个数，数值越大，分割粒度越小
    print(masks[0].keys())

    pic = show_anns(image, masks)
    output_file_path = os.path.join(output_dir, f"mask_.png")
    print("outputFilePath:", output_file_path)
    cv2.imwrite(output_file_path, pic)
    return output_file_path
    '''plt.figure(figsize=(10, 10))
    plt.imshow(image)
    show_anns(masks)  # 显示过程较慢
    plt.show()'''


'''tmp = [[161.68633534, 72.98191204], [877.04076261, 201.13987133]]
label = [1, 1]
save_mask_overlay(r'./SegmentAnything/images/picture1.jpg', tmp, label, output_dir=r'./output')'''
