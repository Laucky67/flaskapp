import base64
from flask import Flask, render_template, request
import numpy as np
import torch
from the_sam_Max import save_mask_overlay, sam_atuo_split
app = Flask(__name__)
point_x = []
point_y = []
labels = []
po_ne = [1]


@app.route('/')
def show_image():
    # 这里假设你的图片位于static/images/myimage.jpg
    with open(
            r'./SegmentAnything/images/picture1.jpg',
            'rb') as img_file:
        img_data = img_file.read()
        encoded_img = base64.b64encode(img_data).decode('utf-8')

    return render_template('index.html', encoded_image=encoded_img)


@app.route('/get_pixel_coordinates', methods=['POST'])
def handle_click_coordinates():
    data = request.get_json()
    point_x0 = data.get('point_x')
    point_y0 = data.get('point_y')

    point_x.append(point_x0)
    point_y.append(point_y0)
    labels.append(po_ne[-1])
    # 在这里你可以处理接收到的坐标，比如存储或进一步处理
    print(f"Received coordinates: ({point_x0}, {point_y0}, {po_ne[-1]})")

    # 示例响应，实际应用中可能需要返回JSON或其他格式的数据
    return '', 204  # 返回HTTP状态码204表示成功处理请求但没有内容返回


@app.route('/send_int_value', methods=['POST'])
def receive_int_value():
    data = request.get_json()
    y_n = data.get('value')
    po_ne.append(y_n)
    print("Received integer value:", y_n)
    # 在这里可以根据接收到的整数值进行相应的处理

    return '', 204


@app.route('/finish_sending_points', methods=['POST'])
def finish_sending_points():
    print(point_x)  # 在此处执行你想停止操作的函数或打印语句
    tmp = list(zip(point_x, point_y))
    label = [1] * len(tmp)
    print(tmp)
    print(labels)
    # save_mask_overlay(r'./SegmentAnything/images/picture1.jpg', tmp, labels)
    sam_atuo_split(r'./SegmentAnything/images/picture1.jpg')
    point_x.clear()
    point_y.clear()
    po_ne.clear()
    po_ne.append(1)
    return '', 204  # 返回HTTP状态码204表示成功处理请求但没有内容返回


@app.route('/auto_signal', methods=['POST'])
def auto_sam():
    print("Auto Sam Start")  # 在此处执行你想停止操作的函数或打印语句
    sam_atuo_split(r'./SegmentAnything/images/picture1.jpg')
    point_x.clear()
    point_y.clear()
    po_ne.clear()
    po_ne.append(1)
    print("Auto Finish! ")
    return '', 204  # 返回HTTP状态码204表示成功处理请求但没有内容返回


if __name__ == '__main__':
    app.run(debug=True)
