from ultralytics.models.sam import Predictor as SAMPredictor
from pathlib import Path


def sam_predict(image_path, points, labels, save_path):
    print("start mobile sam")
    print(points)
    print(labels)
    name = image_path.split("/")[-1]
    # Create SAMPredictor
    overrides = dict(conf=0.25, task='segment', mode='predict', imgsz=1024, model="mobile_sam.pt")
    predictor = SAMPredictor(overrides=overrides)

    # Set image
    predictor.set_image("static/雪山天空.jpg")  # set with image file
    # 假设 predictor 是一个 BasePredictor 实例
    predictor.save_dir = Path("D:/project/html/mapbox/flaskProject/static/image/result/sam")
    # # Define multiple points and labels
    # points = [[439, 437], [900, 370]]  # Each point is a list of [x, y] coordinates
    # labels = [1, 1]  # Each label corresponds to a point
    # Run prediction with multiple points and specify the save directory
    results = predictor(points=points, labels=labels, line_width=1, show_labels=True)
    # Reset image
    predictor.reset_image()
    original_string = "/static/image/result/sam/" + name
    # 提取子字符串
    # 假设你想要从最后一个 '/' 之后开始提取
    return original_string


def sam_auto_pr(image_path, save_path):
    print("start auto mobile sam")
    name = image_path.split("/")[-1]

    # Create SAMPredictor
    overrides = dict(conf=0.25, task='segment', mode='predict', imgsz=1024, model="mobile_sam.pt",line_width=1, show_labels=True)
    predictor = SAMPredictor(overrides=overrides)
    # Set image
    predictor.set_image(image_path)  # set with image file
    # 假设 predictor 是一个 BasePredictor 实例
    predictor.save_dir = Path("D:/project/html/mapbox/flaskProject/static/image/result/sam")
    # # Define multiple points and labels
    # points = [[439, 437], [900, 370]]  # Each point is a list of [x, y] coordinates
    # labels = [1, 1]  # Each label corresponds to a point
    # Run prediction with multiple points and specify the save directory
    results = predictor()
    # Reset image
    predictor.reset_image()
    original_string = "/static/image/result/sam/" + name
    # 提取子字符串
    # 假设你想要从最后一个 '/' 之后开始提取
    print(original_string)
    return original_string

