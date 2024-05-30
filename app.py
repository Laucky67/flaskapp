from flask import Flask, request, send_file, jsonify
import flask
import base64
from flask_bootstrap import Bootstrap5
from flask_cors import CORS, cross_origin
from image_process import *
from dashscope.api_entities.dashscope_response import Role
from wsgiref.simple_server import make_server
from chat import call_with_prompt
import json
from chatglm import chatGLM
from image_merge import align_images
from osgeo import gdal
from X import predict, see_RGB
import re
from mobile_sam import *
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from chatglm import *
location = []
point_x = []
point_y = []
labels = []
po_ne = [1]

# sk-ac7bd32e53284528855a5f03347a4e7c

app = Flask(__name__)
app.secret_key = '3.1415926535897932'
bootstrap = Bootstrap5(app)


'''
# 添加拓展
%load_ext sql
# 数据库连接初始化
%sql postgresql://postgres:123456@127.0.0.1/gisc
# conn=psycopg2.connect(dbname=gisc,user=gisc,password=ZCH20021104,host = "192.168.171.128",port=5432)
'''

# 路由
# 数据库管理
# 配置数据库 URI
# 格式通常是：postgresql://username:password@host:port/database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@127.0.0.1/gisc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化 SQLAlchemy
db = SQLAlchemy(app)

# 定义模型，指定表和模式
class Login(db.Model):
    __tablename__ = 'login'
    __table_args__ = {'schema': 'users'}
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(120), nullable=False)
# 创建数据库和表（如果尚不存在）
@app.before_request
def create_tables():
    db.create_all()

# 获取所有登录信息
@app.route('/logins', methods=['GET'])
def get_logins():
    logins = Login.query.all()
    return jsonify([{'username': l.username, 'password': l.password} for l in logins])

# 更新登录信息
@app.route('/logins/<string:username>', methods=['PUT'])
def update_login(username):
    login = Login.query.get_or_404(username)
    data = request.get_json()
    login.password = data['password']
    db.session.commit()
    return jsonify({'message': 'Login updated', 'login': {'username': login.username, 'password': login.password}})

# 用户注册路由
@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # 检查用户名是否已存在
    if Login.query.get(username):
        return jsonify({'message': 'User already exists'}), 400

    # 创建新用户
    hashed_password = generate_password_hash(password)
    new_user = Login(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered', 'user': {'username': username}}), 201


''' 页面管理 '''


# 登录
@app.route('/', methods=['GET', 'POST'])
def login():  # put application's code here
    return flask.render_template('login.html')
# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    return flask.render_template('register.html')
# 首页
@app.route('/index', methods=['GET', 'POST'])
def index():
    return flask.render_template('index.html')

# 地图页面
@app.route("/map")
@cross_origin("*")  # 允许跨域请求
def map():
    return flask.render_template("map.html", imageUrl=request.host_url + "/static/喜马拉雅山.jpg",
                                 location=[11324268.960713115, 3438648.608765711, 11371312.459048243,
                                           3488080.7755635544])


@app.route("/map2")
@cross_origin("*")
def map2():
    if flask.session.get("image_url"):
        print("image_url:", flask.session.get("image_url"))
        imageUrl = flask.session.get("image_url")
        location = flask.session.get("location")
        print("get the image:", imageUrl, location)
        for key in list(flask.session.keys()):
            del flask.session[key]
        return flask.render_template("map.html", imageUrl=imageUrl, location=location, bool="a")
    else:
        imageUrl = request.host_url + "/" + "static/雪山天空.jpg"
        if flask.session.get("location") != []:
            location = flask.session.get("location")
        else:
            location = [0, 0, 0, 0]
        print("no image:", imageUrl, location)
        for key in list(flask.session.keys()):
            del flask.session[key]
        # return flask.render_template("map.html", imageUrl=imageUrl, location=location)
        return flask.render_template("map.html", imageUrl=imageUrl, location=location, bool="b")


# 智能问答界面
# 存储对话历史的列表
@app.route("/chat", methods=['GET', 'POST'])
@cross_origin("*")
def chat():
    return flask.render_template("chat.html")


# 地貌识别页面
@app.route("/recognition", methods=['GET', 'POST'])
@cross_origin("*")
def recognition():
    return flask.render_template("multimoding.html")


# 多模态识别页面
@app.route("/multimoding_page", methods=['GET', 'POST'])
@cross_origin("*")
def multimoding_page():
    return flask.render_template("multimoding.html")


# 土地利用分类页面
@app.route("/land_classification", methods=['GET', 'POST'])
@cross_origin("*")
def land_classification():
    return flask.render_template("land_classification.html")


@app.route('/analysis', methods=['GET', 'POST'])
@cross_origin("*")
def analysis():
    return flask.render_template("analysis.html")


# sam标注界面
@app.route("/label", methods=['GET', 'POST'])
@cross_origin("*")
def label():
    return flask.render_template("label.html")


# 顶部导航栏
@app.route("/header")
def header():
    return flask.render_template("header.html")


''' 请求处理 '''


# 处理图像上传请求
@app.route("/upload", methods=['POST'])
@cross_origin("*")  # 允许跨域请求
def upload():
    try:
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if file:
            # 读取tif文件
            file = request.files['file']
            # 调用图像处理函数处理,获取图像的url和图像的坐标数据
            img_url, location_data = image_load(file)
            global location
            location = location_data
            return jsonify({'url': img_url, 'location': location_data})

    except Exception as e:
        print(e)
        return 'Internal server error', 500


@app.route("/upload_RGB", methods=['POST'])
@cross_origin("*")
def upload_RGB():
    try:
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if file:
            # 读取tif文件
            file = request.files['file']
            # 调用图像处理函数处理,获取图像的url和图像的坐标数据
            img_url = image_load_RGB(file)
            return jsonify({'url': img_url})

    except Exception as e:
        print(e)
        return 'Internal server error', 500


# 地图显示
@app.route("/map_show", methods=['GET', 'POST'])
@cross_origin("*")
def map_show():
    image_url = request.json.get('url')
    # 将图像 URL 存储在会话中
    flask.session['image_url'] = image_url
    if 'location' in request.json:
        flask.session['location'] = request.json.get('location')
    else:
        # 假设 location 是一个全局变量或已经定义的会话变量
        flask.session['location'] = location
    # 重定向到新的网页，并传递图像 URL
    print(flask.session['image_url'])
    print(flask.session['location'])
    return jsonify({'status': 'success'})


# 处理图像预处理请求
@app.route("/preprocessing", methods=['GET', 'POST'])
@cross_origin("*")  # 允许跨域请求
def preprocessing():
    try:
        if request.json is None:
            return 'No data part', 400
        elif request.json:
            data = request.json
            print(data)
            result = process(data['processList'], data['paramenters'], data['rawUrl'])
            print(result)
            return jsonify({'resultUrl': result})
    except Exception as e:
        print(e)
        return 'Internal server error', 500


# 处理大模型对话请求
conversation_history = [{'role': Role.SYSTEM,
                         'content': 'If any questions are asked about identity, remember who you are: you are a big model of artificial intelligence focused on solving problems in the geographic sciences. '
                                    'You will answer questions about geography objectively and scientifically.'}]


# 下载图像请求
@app.route("/download_image/<string:imageName>", methods=['GET', 'POST'])
@cross_origin("*")
def download_image(imageName):
    # 指定要下载的图像文件的路径
    image_path = request.host_url + "static/images/" + imageName
    # 使用send_file函数来发送文件
    return send_file(image_path, as_attachment=True)


# 语义解析
@app.route("/semantic_analysis", methods=['POST'])
def semantic_analysis():
    # 导入预设参数
    # 分解用户输入
    user_input = request.json
    print(user_input)
    # 错误处理
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    url = user_input["url"]
    text = user_input["string"]

    # 合成用户的输入信息
    user_message = {'role': 'user', 'content': text}
    # 调用大模型进行对话
    result = chatGLM(user_message)
    print(result)
    # 解析大模型的回答
    parts = None
    result = result[1:-1]  # 去除外围大括号
    if "], [" in result:
        parts = result.split("], [")
    elif "],[" in result:
        parts = result.split("],[")
    print("parts:", parts)
    list1_str = parts[0][1:]  # 去除开始的括号
    list2_str = parts[1][:-1]  # 去除尾部的 bracket
    list1 = list1_str.split(",")
    list2 = [int(item) for item in list2_str.split(",")]
    print("list1:", list1, "\n list2:", list2)
    # 处理图像
    result_url = process(list1, list2, url)
    return jsonify({'resultUrl': result_url, "process": list1, "parameters": list2})


@app.route("/chatbot", methods=['POST'])
@cross_origin("*")
def chatbot():
    user_input = request.json.get('input')
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    # 合成用户的输入信息
    user_message = {'role': Role.USER, 'content': user_input}
    print("user input:   ", user_message)
    # 将用户输入添加到对话历史
    global conversation_history
    conversation_history.append(user_message)
    print("history before:  ", conversation_history)

    output_message, conversation_history = call_with_prompt(conversation_history)
    # 将API回复添加到对话历史
    print("history after:  ", conversation_history)
    # 返回API回复
    return jsonify({'response': output_message})


# 获取客户端的ip地址
@app.route("/get_ip", methods=['GET'])
@cross_origin("*")
def get_ip():
    ip = request.host_url
    print("ip:", ip)
    return jsonify({'ip': ip})


@app.route("/multimoding", methods=['GET', "POST"])
@cross_origin("*")
def multimoding():
    image_url1 = request.json.get('near-infrared')
    image_url2 = request.json.get("DEMImage")
    image_url3 = request.json.get("slopeImage")
    # 合成影像
    m_image_name = align_images(image_url1, image_url2, image_url3)
    print("merge_image:", m_image_name)
    # 对图像进行识别
    # 获取识别图像
    temp_url = predict.split_and_reconstruct(m_image_name, (512, 512), 512, 'attention_unet')
    #temp_url = "static/image/result/multimoding_result.png"
    predict_image = request.host_url + temp_url
    classes = ["背景", "水体", "冰川谷"]
    colormap = [[0, 0, 0], [192, 64, 128], [255, 255, 255]]
    predict_dict = sum_rgb(classes, colormap, temp_url)

    # 合成用户的输入信息
    user_message = {'role': 'user', 'content': str(predict_dict)}
    # 调用大模型进行对话
    result = analysisChat(user_message)
    # print("resultText:", result)
    print("resultText:__________________________",str(result))
    return jsonify({'resultUrl': predict_image, "sum_dict": predict_dict,"chatResult":str(result)})


@app.route("/classify", methods=['GET', "POST"])
@cross_origin("*")
def classify():
    image_url = request.json.get("imageUrl")
    print("imageUrl:", image_url)
    base_url = re.sub(r'http://127.0.0.1:8000/', '', image_url)
    print("loacal:", base_url)
    classes = ["未知", "背景值", "建设用地", "道路", "水体", "高原荒漠", "森林", "农业"]
    colormap = [[0, 0, 0], [255, 255, 255], [180, 30, 30], [100, 100, 100], [0, 0, 255], [220, 220, 220],
                [34, 139, 34], [255, 215, 0]]

    temp_url = see_RGB.split_and_reconstruct_rgb(base_url, (512, 512), 128, 'unet_x')
    # temp_url = 'static/image/result/classification_result.png'
    predict_image = request.host_url + temp_url
    result_dict = sum_rgb(classes, colormap, temp_url)  # 统计预测结果图像的数据分布方法
    # 合成用户的输入信息
    user_message = {'role': 'user', 'content': str(result_dict)}
    # 调用大模型进行对话
    result = analysisChat(user_message)
    print("resultText:", result)
    return jsonify({'resultUrl': predict_image, "sum_dict": result_dict,"chatResult":result})

@app.route("/overlayAnalysis", methods=['GET', "POST"])
@cross_origin("*")
def overlayAnalysis():
    multimoding_url = request.json.get("multimodingUrl")
    classify_url = request.json.get("classifyUrl")
    multimoding_url = re.sub(r'http://127.0.0.1:8000/', '', multimoding_url)
    classify_url = re.sub(r'http://127.0.0.1:8000/', '', classify_url)
    print("multimoding_url:", multimoding_url, "classify_url:", classify_url)
    return_url = overlay_analysis(multimoding_url, classify_url)
    # return_url = "static/image/result/classification_result.png"
    result_path = request.host_url + return_url
    # result_path = "http://127.0.0.1:8000/static/image/result/classification_result.png"
    classes = ["不适宜开发", "水体", "已经建设利用土地", "未知", "高原荒漠", "其他"]
    colormap = [[255, 0, 0], [128, 64, 192], [255,215,0], [0, 0, 0], [220, 220, 220], [203, 192, 255]]
    class_count = sum_rgb(classes, colormap, return_url)
    # 合成用户的输入信息
    user_message = {'role': 'user', 'content': str(class_count)}
    # 调用大模型进行对话
    result = analysisChat(user_message)
    print("resultText:", result)
    return jsonify({'resultUrl': result_path, "class_count": class_count,"chatResult":result})


# 绘图窗口请求
@app.route("/showImage", methods=['GET', "POST"])
@cross_origin("*")
def show_image():
    # 这里假设你的图片位于static/images/myimage.jpg
    global location
    location = request.json.get("location")
    url = request.json.get("url")

    return flask.render_template('index.html', imageUrl=url, location=location)


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
    data = request.get_json()  # 获取JSON数据
    image_url = data['image_url']  # 获取图像URL
    print(point_x)  # 在此处执行你想停止操作的函数或打印语句
    tmp = list(zip(point_x, point_y))
    label = [1] * len(tmp)
    print(tmp)
    print(labels)
    path = sam_predict(image_url, tmp, label, "D:/project/html/mapbox/flaskProject/static/image/result/sam")
    # path = sam_atuo_split(image_url)
    point_x.clear()
    point_y.clear()
    po_ne.clear()
    po_ne.append(1)
    print("label Finish!____________________ ")
    path = request.host_url + path
    print(path)
    # return '', 204  # 返回HTTP状态码204表示成功处理请求但没有内容返回
    return jsonify({'path': path})


@app.route('/auto_signal', methods=['POST'])
def auto_sam():
    print("Auto Sam Start")  # 在此处执行你想停止操作的函数或打印语句
    data = request.get_json()  # 获取JSON数据
    image_url = data['image_url']  # 获取图像URL
    print(image_url)
    path = sam_auto_pr(image_path=image_url, save_path="D:/project/html/mapbox/flaskProject/static/image/result/sam")
    print(path)
    point_x.clear()
    point_y.clear()
    po_ne.clear()
    po_ne.append(1)
    print("Auto Finish!____________________________ ")
    path_result = request.host_url + path
    print(path_result)
    # return '', 204  # 返回HTTP状态码204表示成功处理请求但没有内容返回
    return jsonify({'path': path_result})


# 启动Flask应用程序
CORS(app)
app.config['DEBUG'] = True

if __name__ == '__main__':
    server = make_server('0.0.0.0', 5000, app)
    server.serve_forever()
    app.run()
