#!/user/bin/env python3
# -*- coding: utf-8 -*-
import os

from osgeo import gdal, gdalnumeric
import numpy as np
from scipy.signal import convolve2d
import whitebox
from whitebox.whitebox_tools import WhiteboxTools

here_direction = "/static/image/"
# 初始化WhiteboxTools
wbt = WhiteboxTools()
wbt.verbose = True  # 控制是否显示详细运行信息
wbt.work_dir = here_direction  # 设置工作目录
"""
                这里一定一定要注意！！！
                我为whitebox设置的工作目录是软件包本身，工作目录在哪里，文件就会保存到哪里！！！
"""


def write_geotiff(output_file, data_array, source_ds, data_type):
    """
    将数组写入到带有源DEM地理信息的GeoTIFF文件中
    """
    driver = gdal.GetDriverByName('GTiff')
    dest_ds = driver.Create(output_file, source_ds.RasterXSize, source_ds.RasterYSize, 1, data_type)
    dest_ds.SetProjection(source_ds.GetProjection())
    dest_ds.SetGeoTransform(source_ds.GetGeoTransform())
    dest_ds.GetRasterBand(1).WriteArray(data_array)
    dest_ds.FlushCache()  # 提交更改
    dest_ds = None  # 关闭dataset释放资源


def calculate_slope_dem(dem_file, out_slope_file):
    """
    计算并输出坡度和方位角栅格文件
    """
    # 打开DEM数据
    dem_ds = gdal.Open(dem_file, gdal.GA_ReadOnly)
    elev_array = gdalnumeric.LoadFile(dem_file)

    # 获取分辨率和地理变换参数
    geotransform = dem_ds.GetGeoTransform()
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]

    # 计算梯度
    dx, dy = np.gradient(elev_array, pixel_width, pixel_height)

    # 计算坡度和方位角
    slope_rad = np.arctan(np.sqrt(dx ** 2 + dy ** 2))
    slope_degrees = np.rad2deg(slope_rad)

    # 写入坡度和方位角栅格文件
    write_geotiff(out_slope_file, slope_degrees, dem_ds, gdal.GDT_Float32)


def calculate_ruggedness_dem(dem_file, out_ruggedness_file):
    """
    计算并输出地形起伏度栅格文件
    """
    dem_ds = gdal.Open(dem_file, gdal.GA_ReadOnly)
    elev_array = gdalnumeric.LoadFile(dem_file)

    # 计算地形起伏度
    dx, dy = np.gradient(elev_array)
    ruggedness = np.abs(dx) + np.abs(dy)

    # 写入起伏度栅格文件
    write_geotiff(out_ruggedness_file, ruggedness, dem_ds, gdal.GDT_Float32)


def calculate_tpi_dem(dem_file, out_tpi_file, kernel_size=3):
    """
    计算并输出地形一致性指数（TPI）栅格文件
    """
    dem_ds = gdal.Open(dem_file, gdal.GA_ReadOnly)
    elev_array = gdalnumeric.LoadFile(dem_file)
    nodata = dem_ds.GetRasterBand(1).GetNoDataValue()

    # 创建一个均匀权重的卷积核
    neighborhood = np.ones((kernel_size, kernel_size))
    neighborhood /= neighborhood.sum()

    # 计算局部平均高程
    local_elev_avg = convolve2d(elev_array, neighborhood, mode='same', boundary='wrap')

    # 计算TPI
    tpi = elev_array - local_elev_avg

    # 处理边界
    border = kernel_size // 2
    tpi[:border, :] = nodata
    tpi[-border:, :] = nodata
    tpi[:, :border] = nodata
    tpi[:, -border:] = nodata

    # 写入TPI栅格文件，这里假设nodata值已在内部处理
    write_geotiff(out_tpi_file, tpi, dem_ds, gdal.GDT_Float32)


def calculate_curvatures(dem_file, out_profile_curvature_file, out_plan_curvature_file):
    """
    计算并输出地形总曲率、剖面曲率和水平曲率栅格文件
    """
    # 打开DEM数据
    dem_ds = gdal.Open(dem_file, gdal.GA_ReadOnly)
    elev_array = gdalnumeric.LoadFile(dem_file)
    rows, cols = elev_array.shape

    # 获取分辨率和地理变换参数
    geotransform = dem_ds.GetGeoTransform()
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]

    # 计算一阶导数（梯度）
    dx, dy = np.gradient(elev_array, pixel_width, pixel_height)

    # 计算二阶导数（曲率）
    dxx, dyy = np.gradient(dx, pixel_width, pixel_height)
    dxy = np.gradient(dy, pixel_width, pixel_height)[1]

    # 计算总曲率、剖面曲率和水平曲率
    profile_curvature = (dxx * dy ** 2 - 2 * dx * dy * dxy + dyy * dx ** 2) / ((dx ** 2 + dy ** 2) ** 1.5)
    plan_curvature = (dxx * dy ** 2 - 2 * dx * dy * dxy + dyy * dx ** 2) / (
            (dx ** 2 + dy ** 2) ** 1.5 - (dx * dxy + dy * dyy) ** 2)

    # 写入曲率栅格文件
    write_geotiff(out_profile_curvature_file, profile_curvature, dem_ds, gdal.GDT_Float32)
    write_geotiff(out_plan_curvature_file, plan_curvature, dem_ds, gdal.GDT_Float32)


def calculate_aspect(dem_file, out_aspect_file):
    """
    计算并输出地形坡向栅格文件
    """
    # 打开DEM数据
    dem_ds = gdal.Open(dem_file, gdal.GA_ReadOnly)
    elev_array = gdalnumeric.LoadFile(dem_file)
    rows, cols = elev_array.shape

    # 获取分辨率和地理变换参数
    geotransform = dem_ds.GetGeoTransform()
    pixel_width = abs(geotransform[1])
    pixel_height = abs(geotransform[5])

    # 计算一阶导数（梯度）
    dx, dy = np.gradient(elev_array, pixel_width, pixel_height)

    # 计算坡向
    # 注意，这里使用atan2函数计算方位角，返回值范围是-pi到pi
    # 转换为0-360度，以正北为0度，逆时针方向增加
    aspect = np.degrees(np.arctan2(dx, -dy)) % 360

    # 将负值转换为正值（因为arctan2返回的结果在东西方向可能出现负值）
    aspect[aspect < 0] += 360

    # 写入坡向栅格文件
    write_geotiff(out_aspect_file, aspect, dem_ds, gdal.GDT_Float32)


def fill_sinks(input_dem, output_filled_dem):
    """
    使用WhiteboxTools填洼算法
    """
    wbt.fill_depressions(input_dem, output_filled_dem)


def calculate_flow_direction(input_dem, output_flow_dir):
    """
    使用WhiteboxTools计算水流方向
    """
    wbt.d8_pointer(input_dem, output_flow_dir)


def apply_operation_on_rasters(operation, *raster_files, scalar=None, output_file=None):
    """
    栅格计算器
    """
    # 获取第一个栅格数据集的信息作为基准
    base_raster_file = raster_files[0]
    base_raster_ds = gdal.Open(base_raster_file, gdal.GA_ReadOnly)
    base_array = gdalnumeric.LoadFile(base_raster_file)
    rows, cols = base_array.shape
    band = base_raster_ds.GetRasterBand(1)
    data_type = band.DataType
    nodata_value = band.GetNoDataValue()

    # 加载所有栅格数据集
    arrays = [gdalnumeric.LoadFile(raster_file) for raster_file in raster_files]

    # 如果有标量值参与运算，则将其转化为与栅格同形状的数组
    if scalar is not None:
        scalar_array = np.full((rows, cols), scalar,
                               dtype=np.float32 if data_type in [gdal.GDT_Float32, gdal.GDT_Float64] else np.int32)
        arrays.append(scalar_array)

    # 执行运算
    result_array = arrays[0]
    for array in arrays[1:]:
        if operation == '+':
            result_array += array
        elif operation == '-':
            result_array -= array
        elif operation == '*':
            result_array *= array
        elif operation == '/':
            # 防止除以零
            divisor_zeros = (array == 0)
            result_array = np.divide(result_array, array, out=np.zeros_like(result_array), where=~divisor_zeros)
        elif operation == 'and':
            result_array &= array
        elif operation == 'or':
            result_array |= array
        elif operation == 'not':  # NOT运算仅针对单个栅格
            if len(arrays) != 2:
                raise ValueError("The NOT operation requires exactly one raster input.")
            result_array = ~array
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    # 创建输出文件
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_file, base_raster_ds.RasterXSize, base_raster_ds.RasterYSize, 1, data_type)
    out_ds.SetGeoTransform(base_raster_ds.GetGeoTransform())
    out_ds.SetProjection(base_raster_ds.GetProjection())

    # 写入结果数据
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(result_array)
    if nodata_value is not None:
        out_band.SetNoDataValue(nodata_value)

    # 清理资源
    out_band = None
    out_ds = None
    base_raster_ds = None
