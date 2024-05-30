import tifffile as tifffile
from osgeo import gdal, osr

# 打开包含子数据集的文件
input_raster = r"E:\chengxu\AI_test\Api\tool\output.tif"  # 转为web墨卡托后的带输入图像
# 输出图像的路径
output_raster = r"E:\chengxu\AI_test\reconstructed_image01.tif"  # 预测得到的图像


def ttf(input_raster, output_raster):
    dataset = gdal.Open(input_raster)
    image_matrix = tifffile.imread(output_raster)

    # 检查dataset是否成功打开
    if dataset is None:
        print('无法打开文件')
        exit(1)

    # 获取地理变换参数和投影
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    # 创建一个新的三维数组，形状应该是（波段数，高度，宽度）
    # 假设我们有一个随机的三维数组作为示例
    array_shape = (dataset.RasterYSize, dataset.RasterXSize, 3)  # 3个波段，与原始dataset相同的大小
    random_data = image_matrix

    # 设置输出文件的路径
    output_raster = '预测图的投影图.tif'

    # 创建输出驱动
    driver = gdal.GetDriverByName('GTiff')

    # 创建输出数据集，指定波段数、高度和宽度
    dataset0 = driver.Create(output_raster, dataset.RasterXSize, dataset.RasterYSize, array_shape[-1], gdal.GDT_Float32)

    # 设置地理变换参数和投影
    dataset0.SetGeoTransform(geotransform)
    dataset0.SetProjection(projection)

    # 遍历每个波段，将三维数组的数据按照新维度顺序写入到对应的波段中
    for band_index in range(array_shape[-1]):
        band = dataset0.GetRasterBand(band_index + 1)  # 波段索引依然从1开始
        band.WriteArray(random_data[:, :, band_index])  # 现在按照行、列顺序取波段数据
        band.FlushCache()
        band.ComputeStatistics(True)

    # 清理资源
    band = None
    dataset0 = None
    dataset = None

    print('新的dataset0已创建并写入数据')
