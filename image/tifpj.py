from osgeo import gdal

# 读取三张灰度图像
raster1 = gdal.Open(r"E:\arcgis_objects\冰川\dcband6.tif")
raster2 = gdal.Open(r"E:\arcgis_objects\冰川\dcdem.tif")
raster3 = gdal.Open(r"E:\arcgis_objects\冰川\dcslope.tif")

# 检查所有图像的地理坐标系和分辨率是否一致
if raster1.GetGeoTransform() == raster2.GetGeoTransform() and raster1.GetGeoTransform() == raster3.GetGeoTransform():
    print("Geotransform is the same for all rasters.")
else:
    print("Geotransforms are not the same, cannot align and mosaic.")

# 获取第一张图像的信息用于创建新的RGB图像
driver = raster1.GetDriver()
x_size = raster1.RasterXSize
y_size = raster1.RasterYSize
geotransform = raster1.GetGeoTransform()
projection = raster1.GetProjection()

# 创建一个新的RGB图像，每个通道都用32位无符号整型
out_raster = driver.Create('output.tif', x_size, y_size, 3, gdal.GDT_UInt32)
out_raster.SetGeoTransform(geotransform)
out_raster.SetProjection(projection)

# 将灰度图像的数据复制到RGB图像的不同波段
red_band = out_raster.GetRasterBand(1)
red_band.WriteArray(raster1.GetRasterBand(1).ReadAsArray())

green_band = out_raster.GetRasterBand(2)
green_band.WriteArray(raster2.GetRasterBand(1).ReadAsArray())

blue_band = out_raster.GetRasterBand(3)
blue_band.WriteArray(raster3.GetRasterBand(1).ReadAsArray())

# 关闭所有文件
raster1 = None
raster2 = None
raster3 = None
out_raster = None
