import numpy as np
from tifffile import imread, imwrite
from osgeo import gdal
import re


def match_image(path):
    print(path)
    match = re.search(r'/static/image/(.*?).tif', path)
    # 如果匹配成功，提取文件名
    if match:
        file_name = match.group(1)
        print(file_name)  # 输出: file_process
        return file_name
    else:
        print("No match found")
        return EOFError


def align_images(image1, image2, image3):
    file_name = match_image(image1)
    print(file_name)
    # 获取图像的名称
    image1 = "image/" + match_image(image1) + ".tif"
    image2 = "image/" + match_image(image2) + ".tif"
    image3 = "image/" + match_image(image3) + ".tif"

    # 读取图像
    print(image1, image2, image3)
    img1 = imread(image1)
    img2 = imread(image2)
    img3 = imread(image3)

    # 获取图像的地理坐标信息
    dataset1 = gdal.Open(image1)
    geotransform1 = dataset1.GetGeoTransform()
    dataset2 = gdal.Open(image2)
    geotransform2 = dataset2.GetGeoTransform()
    dataset3 = gdal.Open(image3)
    geotransform3 = dataset3.GetGeoTransform()

    # 获取图像的地理坐标信息
    projection1 = dataset1.GetProjection()

    # 计算平移量
    dx2 = int((geotransform1[0] - geotransform2[0]) / geotransform2[1])
    dy2 = int((geotransform1[3] - geotransform2[3]) / geotransform2[5])

    dx3 = int((geotransform1[0] - geotransform3[0]) / geotransform3[1])
    dy3 = int((geotransform1[3] - geotransform3[3]) / geotransform3[5])

    # 对齐图像
    aligned_img2 = np.roll(img2, shift=(dy2, dx2), axis=(0, 1))
    aligned_img3 = np.roll(img3, shift=(dy3, dx3), axis=(0, 1))

    # 拼接图像
    result = np.dstack((img1, aligned_img2, aligned_img3))

    # 组合新名称
    output_filename = "static/image/result/" + file_name + "_mergeResult.tif"

    # 创建并写入新的GeoTIFF文件
    driver = gdal.GetDriverByName('GTiff')
    out_dataset = driver.Create(output_filename, result.shape[1], result.shape[0], result.shape[2],
                                gdal.GDT_Float32)  # 假设数据类型为Float32

    # 设置地理参考信息和地理坐标变换参数
    out_dataset.SetProjection(projection1)
    out_dataset.SetGeoTransform(geotransform1)

    # 写入数据
    for band_index in range(result.shape[2]):
        out_band = out_dataset.GetRasterBand(band_index + 1)
        out_band.WriteArray(result[:, :, band_index])

    # 确保所有更改已保存
    out_dataset.FlushCache()

    # 释放内存
    dataset2 = None
    dataset3 = None
    dataset1 = None

    # 返回保存后的图像文件路径
    return output_filename


# 使用示例
image1 = 'path/to/image1.tif'
image2 = 'path/to/image2.tif'
image3 = 'path/to/image3.tif'
# result0 = align_images(image1, image2, image3)
# imwrite('result.tif', result0)
