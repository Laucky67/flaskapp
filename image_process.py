import cv2
from flask import Flask, request, send_file, jsonify
from PIL import Image
from io import BytesIO
import numpy as np
from osgeo import gdal
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from scipy import ndimage as ndi
import re
from os.path import dirname, abspath, join
from matplotlib import pyplot as plt
from dem_tools import dem_analysis


# 用于改名
def match_image(path):
    print(path)
    match = re.search(r'result/(.*?).tif', path)
    # 如果匹配成功，提取文件名
    if match:
        file_name = match.group(1)
        print(file_name)  # 输出: file_process
        return file_name
    else:
        print("No match found")
        return EOFError


# 归一化函数，传入数组，返回归一化后的数组【0,255】
def normalize(arr):
    # 计算数组的最小值和最大值
    min_val = np.min(arr)
    print(min_val)
    max_val = np.max(arr)
    print(max_val)
    # 归一化数组到 [0, 255] 范围
    normalized_arr = (arr - min_val) / (max_val - min_val) * 255
    print(normalized_arr)
    # 确保结果为整数类型
    normalized_arr = normalized_arr.astype(np.uint8)
    return normalized_arr


# 图像加载函数，传入file，返回图像url和图像地理位置
def image_load(file):
    temp_file_path = "image/" + secure_filename(file.filename)
    print(temp_file_path)
    # 切割文件名称
    filename_list = temp_file_path.split('.')
    filename = filename_list[0]
    # 保存文件
    file.save(temp_file_path)
    # 使用gdal读取TIFF文件
    dataset = gdal.Open(temp_file_path)
    # 获取地理变换参数
    geotransform = dataset.GetGeoTransform()
    # 读取TIFF文件的宽度和高度
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    # 计算左上角和右下角的地理坐标
    xmin = geotransform[0]
    ymax = geotransform[3]
    xmax = xmin + width * geotransform[1]
    ymin = ymax + height * geotransform[5]
    location_data = [xmin, ymin, xmax, ymax]
    print(location_data)

    if dataset is None:
        return '无法打开文件', 400
    # 转换为numpy数组
    band = dataset.GetRasterBand(1)
    arr = band.ReadAsArray()
    # temp_array = band.ReadAsArray()
    # 归一化
    # arr = normalize(temp_array)
    print(arr)
    # 转换为图像
    img = Image.fromarray(arr).convert('RGB')
    img_io = BytesIO()
    img_io.seek(0)
    # 返回图像数据
    print(img)
    print(img_io)
    print("success!")
    # 保存图像到服务器
    img.save("static/" + filename + ".png")
    # 返回图像URL
    img_url = request.host_url + "static/" + filename + ".png"
    dataset = None  # 释放数据集
    # 返回url和地理位置信息
    return img_url, location_data


# 加载rgb
def image_load_RGB(file):
    temp_file_path = "static/image/" + secure_filename(file.filename)
    print(temp_file_path)
    # 切割文件名称
    filename_list = temp_file_path.split('.')
    filename = filename_list[0]
    # 保存文件
    file.save(temp_file_path)
    # 返回图像URL
    img_url = request.host_url + filename + ".png"
    print("img_url:", img_url)
    # 返回url和地理位置信息
    return img_url


def import_model(name, model_path):
    pass


# 图像格式转换
def tif_to_png(file_path):
    # TIFF文件路径
    tif_file = file_path
    path_list = file_path.split('.')[0]
    # PNG文件路径
    png_file = path_list + ".png"

    # 使用GDAL打开TIFF文件
    dataset = gdal.Open(tif_file)
    # 如果打开失败，打印错误信息并退出
    if not dataset:
        print('无法打开文件:', tif_file)
        exit(1)
    # 转换为numpy数组
    band = dataset.GetRasterBand(1)
    arr = band.ReadAsArray()
    # 转换为图像
    img = Image.fromarray(arr).convert('RGB')
    img_io = BytesIO()
    img_io.seek(0)
    # 返回图像数据
    print("success!")
    # 保存图像到服务器
    print(png_file)
    img.save(png_file)
    del dataset
    print('TIFF文件已成功转换为PNG文件:', png_file)
    return png_file


# 计算坡度、坡向和曲率
def calculate_sac(dem, geotransform, id):
    method = int(id) - 6
    # 转换DEM数据为浮点数
    dem[dem == -32768] = 0
    dem = dem.astype(np.float32)
    # 计算x和y方向上的梯度
    dx = np.gradient(dem, geotransform[1])
    dy = np.gradient(dem, geotransform[5])
    # 计算坡度（度）
    # 首先计算dx和dy的平方和
    squared_dx = dx[0] ** 2 + dx[1] ** 2
    squared_dy = dy[0] ** 2 + dy[1] ** 2
    # 然后计算平方和的平方根
    slope = np.degrees(np.arctan(np.sqrt(squared_dx + squared_dy)))
    # 计算坡向（度）
    aspect = np.degrees(np.arctan2(dx, dy))
    # 计算曲率
    dxx = np.gradient(dx, geotransform[1])
    dyy = np.gradient(dy, geotransform[5])
    curvature = dxx + dyy
    result_list = [
        slope,
        curvature,
        aspect
    ]
    print("地理参数计算成功！")
    return result_list[method]


# 进行图像预处理计算函数
def image_cal(image, parmater, method, temp_image, result_image):
    dataset = image
    band = image.GetRasterBand(1)
    img = band.ReadAsArray()
    # 获取DEM的地理变换参数
    geotransform = dataset.GetGeoTransform()
    method = int(method)
    parmater = int(parmater)
    if method == 0:
        # 高通滤波
        high_pass = ndi.gaussian_filter(img, sigma=parmater)  # 先用高斯模糊
        high_pass = img - high_pass  # 然后用原始图像减去模糊后的图像
        print("高通滤波成功")
        return high_pass
    elif method == 1:
        # 低通
        low_pass = ndi.gaussian_filter(img, sigma=parmater)
        print("低通滤波成功")
        return low_pass
    elif method == 2:
        # 中值滤波
        median_filter = ndi.median_filter(img, size=parmater)
        print("中值滤波成功")
        return median_filter
    elif method == 3:
        # 线性拉伸
        min_val = np.min(img)
        max_val = np.max(img)
        linear_stretch = (img - min_val) / (max_val - min_val) * 255
        print("线性拉伸成功")
        return linear_stretch
    elif method == 4:
        # 对数变换
        log_transformed = parmater * np.log(img + 1)
        print("对数变换成功")
        return log_transformed
    elif method == 5:
        # 幂律变换
        power_transformed = np.power(img, parmater)
        print("幂律变换成功")
        return power_transformed
    elif method == 6:
        # 坡度
        slope = calculate_sac(img, geotransform, method)
        print("计算坡度成功")
        return slope
    elif method == 7:
        curvature = calculate_sac(img, geotransform, method)
        print("计算曲率成功")
        return curvature
    elif method == 8:
        aspect = calculate_sac(img, geotransform, method)
        print("计算坡向成功")
        return aspect
    elif method == 9:
        dem_analysis.fill_sinks(temp_image, result_image)
        dataset = gdal.Open(result_image)
        imageBand = dataset.GetRasterBand(1)
        fill = imageBand.ReadAsArray()
        return fill
    elif method == 9:
        dem_analysis.calculate_flow_direction(temp_image, result_image)
        dataset = gdal.Open(result_image)
        imageBand = dataset.GetRasterBand(1)
        flow = imageBand.ReadAsArray()
        return flow



def white_box(method, inputpath, output_path):
    if method == 9:
        dem_analysis.fill_sinks(inputpath, output_path)
    elif method == 10:
        dem_analysis.calculate_flow_direction(inputpath, output_path)


# 执行图像预处理的函数
def process(methodList, parameters, image_url):
    print("开始图像预处理")
    print(image_url)
    print(methodList)
    # 字典用于对于方法与代号
    code_dict = {"高通滤波": 0, "低通滤波": 1, "中值滤波": 2, "线性拉伸": 3, "对数变换": 4, "幂律变换": 5, "坡度": 6,
                 "曲率": 7, "坡向": 8, "计算坡度": 6, "计算曲率": 7, "计算坡向": 8, "填洼": 9, "计算填洼": 9,
                 "计算流向": 10, "流向": 10}
    # 生成保存图像的路径
    # 使用正则表达式匹配文件名
    match = re.search(r'/static/image/(.*?).tif', image_url)
    # 如果匹配成功，提取文件名
    if match:
        file_name = match.group(1)
        print(file_name)  # 输出: file_process
    else:
        print("No match found")
        return EOFError

    temp_img = "image/" + file_name + ".tif"
    result_path = "static/image/result/" + file_name + "_PreResult.tif"
    print("result_path", result_path)

    # 读取TIFF图像
    print("temp_path", temp_img)
    dataset = gdal.Open(temp_img)
    print(dataset)
    band = dataset.GetRasterBand(1)
    img = band.ReadAsArray()
    print(img)

    # 判断是否有数据
    if img is None:
        return -1

    print("read preProcess image success")
    length = len(methodList)
    # 迭代处理图像
    for i in range(length):
        method_type = methodList[i].strip('\'')
        method_type = method_type.strip(' ')
        method = code_dict[method_type]
        parameter = parameters[i]
        print(method, parameter)
        img = image_cal(dataset, parameter, method, temp_img, result_path)
    print("process preProcess image success!")
    # 保存滤波后的图像
    driver = gdal.GetDriverByName('GTiff')
    img_ds = driver.CreateCopy(result_path, dataset)
    img_ds.GetRasterBand(1).WriteArray(img)
    del img_ds
    print(result_path)
    png_file = tif_to_png(result_path)
    # 返回地址
    return request.host_url + png_file


def tif_to_png_(tif_path, output_name):
    try:
        print("tifPath:", tif_path)
        # 打开tif图像
        dataset = gdal.Open(tif_path)
        if dataset is None:
            raise Exception("无法打开tif文件")

        # 获取tif图像的驱动和数据
        driver = gdal.GetDriverByName('PNG')
        file_name = match_image(tif_path)
        print("filename:", file_name)
        out_path = "static/image/" + file_name + ".png"
        # out_path = join(dirname(abspath(tif_path)), output_name + '.png')

        # 创建输出图像
        out_dataset = driver.CreateCopy(out_path, dataset, strict=0)
        if out_dataset is None:
            raise Exception("无法创建png文件")

        # 关闭数据集
        out_dataset = None
        dataset = None

        return out_path

    except Exception as e:
        print("发生错误：", e)
        return None


# 用于统计像素情况
def sum_rgb(class_list, rgb_list, path):
    colormap = np.array(rgb_list)
    image = Image.open(path)
    image_data = np.array(image)
    print(image_data)
    classNum = len(class_list)
    # 初始化计数器
    class_counts = {class_name: 0 for class_name in class_list}
    # 遍历图像数据，统计每个类的数量
    for row in image_data:
        for pixel in row:
            # 查找匹配的颜色
            matched_class = np.where((colormap == pixel).all(axis=1))
            if len(matched_class[0]) > 0:
                class_index = matched_class[0][0]
                class_name = class_list[class_index]
                class_counts[class_name] += 1
    return class_counts


# pixel1 是 地形识别结果，Pixel2是土地利用分类结果,返回叠置分析结果
# 示例数据：pixel1 = [0,0,0] pixel2 = [100,100,100]
def judge(pixel1, pixel2):
    # 将输入的像素值转换为NumPy数组
    pixel1 = np.array(pixel1, dtype=np.uint8)
    pixel2 = np.array(pixel2, dtype=np.uint8)

    # 冰川谷地 或森林 不适合开发
    if (pixel1 == [255, 255, 255]).all() or (pixel2 == [34, 139, 34]).all():
        return [0, 0, 255]
    # 水体，进行或运算
    elif (pixel1 == [192, 64, 128]).all() or (pixel1 == [0, 0, 255]).all():
        return [192, 64, 128]
    # 建筑物，道路已经被开发利用
    elif (pixel2 == [180, 30, 30]).all() or (pixel2 == [100, 100, 100]).all():
        return [180, 30, 30]
    # 未知
    elif (pixel2 == [0, 0, 0]).all() and (pixel1 == [0, 0, 0]).all():
        return [0, 0, 0]
    # 可以利用土地 包括 贫瘠地区，农田
    elif (pixel2 == [220, 220, 220]).all() or (pixel2 == [255, 215, 0]).all():
        return [220, 220, 220]
    # 其他
    else:
        return [255, 192, 203]


def overlay_analysis(image_url1, image_url2):
    image1 = cv2.imread(image_url1)
    image2 = cv2.imread(image_url2)
    # 将image1和image转换为np数组
    image1 = np.array(image1)
    image2 = np.array(image2)
    print("image1:", image1)
    print("image2:", image2)
    # 对数组进行叠置分析
    x, y, z = image1.shape
    # 创建一个与image1相同大小的数组
    result = np.zeros((x, y, 3), dtype=np.uint8)
    for i in range(x):
        for j in range(y):
            pixel = judge(image1[i, j], image2[i, j])
            result[i, j] = pixel
    # 将结果保存为图像
    result_url = "static/image/result/result_overlay.png"
    # 使用matplotlib显示图像
    plt.figure()
    # 添加颜色条（可选）
    plt.imshow(result)
    plt.show()
    cv2.imwrite(result_url, result)

    return result_url
