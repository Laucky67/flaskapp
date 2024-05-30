import cv2
import matplotlib.pyplot as plt

# 图像路径
image_path = 'D:\\project\\html\\mapbox\\flaskProject\\static\\image\\result\\multimoding_result.png'

# 读取图像
image = cv2.imread(image_path)

# 检查图像是否成功加载
if image is None:
    print("Could not open or find the image")
else:
    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用高斯模糊
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 使用简单阈值方法
    _, bin_img = cv2.threshold(blurred, 0, 1, cv2.THRESH_BINARY)

    # 搜索图像中的连通区域
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(bin_img, connectivity=4)

    # 定义一个面积阈值，小于这个阈值的区域将被过滤掉
    area_threshold = 500  # 例如，设置面积为100像素的小区域将被去除

    # 复制原图像以绘制结果
    original_img_cbk = image.copy()

    idx = 1
    for stat in stats[1:]:  # 跳过背景标签
        area = stat[4]  # 区域面积
        if area < area_threshold:
            continue  # 如果区域面积小于阈值，则跳过
        if (stat[2] - stat[0]) > bin_img.shape[0] / 2:
            continue
        cv2.rectangle(original_img_cbk, (stat[0], stat[1]), (stat[0] + stat[2], stat[1] + stat[3]), (0, 0, 255), 2)
        cv2.putText(original_img_cbk, str(idx), (stat[0], stat[1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 25, 25), 2)
        idx += 1

    # 使用matplotlib显示图像
    plt.imshow(cv2.cvtColor(original_img_cbk, cv2.COLOR_BGR2RGB))
    plt.show()

    # 保存图像
    output_path = 'D:\\project\\html\\mapbox\\flaskProject\\static\\image\\result\\output_image.png'
    cv2.imwrite(output_path, original_img_cbk)
