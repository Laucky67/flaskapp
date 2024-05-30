from osgeo import gdal, osr

# 打开包含子数据集的文件
input_raster = r"E:\arcgis_objects\冰川\dc_b6_1_CompositeBands1.tif" # 原始图像
# 输出图像的路径
output_raster = r'E:\chengxu\AI_test\Api\tool\output.tif' # 转为web墨卡托后的带输入图像


def transform_to_web_mercator(input_raster, output_raster):
    # 设置目标投影（Web墨卡托投影）
    target_projection = 'EPSG:3857'
    # 打开输入图像
    dataset = gdal.Open(input_raster)
    # 如果输入图像无法打开，则退出
    if dataset is None:
        print('无法打开输入图像')
        exit(1)
    # 获取输入图像的投影
    source_projection = dataset.GetProjection()
    # 如果输入图像没有投影信息，则退出
    if source_projection is None:
        print('输入图像没有投影信息')
        exit(1)
    # 创建输入图像的SpatialReference对象
    source_sr = osr.SpatialReference()
    source_sr.ImportFromWkt(source_projection)

    # 创建目标投影的SpatialReference对象
    target_sr = osr.SpatialReference()
    target_sr.ImportFromEPSG(int(target_projection.split(':')[-1]))

    # 比较输入图像的投影与目标投影
    if source_sr.IsSame(target_sr):
        print('输入图像已经是Web墨卡托投影，无需重投影')
        exit(1)
    else:
        # 复制输入图像到输出图像，同时进行重投影
        options = gdal.WarpOptions(dstSRS=target_projection, format='GTiff', outputType=gdal.GDT_Float32)
        gdal.Warp(output_raster, dataset, options=options)
    # 清理资源
    dataset = None
    print('图像重投影完成，输出文件：', output_raster)


transform_to_web_mercator(input_raster, output_raster)
