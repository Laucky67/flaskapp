from flask import Flask, request, send_file, jsonify
import flask
from flask_bootstrap import Bootstrap5
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from image_process import image_load
from image_process import process
from http import HTTPStatus
import dashscope
from dashscope.api_entities.dashscope_response import Role
from dashscope import Generation
from wsgiref.simple_server import make_server


# sk-ac7bd32e53284528855a5f03347a4e7c

def call_with_prompt(messages):
    result = ""
    dashscope.api_key = 'sk-ac7bd32e53284528855a5f03347a4e7c'  # 将 API-KEY
    # 调用dashscope库中的Generation.call方法，使用qwen_turbo模型处理消息列表，并设置结果格式为'message'
    response = Generation.call(
        Generation.Models.qwen_turbo,
        messages=messages,
        result_format='message'
    )
    # 检查请求是否成功（HTTP状态码为200）
    print("response:", response)
    if response.status_code == HTTPStatus.OK:
        # 打印响应内容
        result = response.output.choices[0]['message']['content']  # get the result
        # 将AI回复添加到消息列表中
        messages.append({
            'role': response.output.choices[0]['message']['role'],
            'content': response.output.choices[0]['message']['content']
        })
        return result, messages
    else:
        # 请求失败时打印错误信息
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
        result = ('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
        return result, messages

def simple_multimodal_conversation_call():
    """Simple single round multimodal conversation call.
    """
    dashscope.api_key = 'sk-ac7bd32e53284528855a5f03347a4e7c'  # 将 API-KEY
    messages = [
        {
            "role": "user",
            "content": [
                {"image": "file://static/新西兰库克山.jpg"},
                {"text": "这是什么?"}
            ]
        }
    ]
    response = dashscope.MultiModalConversation.call(model='qwen-vl-max',
                                                     messages=messages)
    # The response status_code is HTTPStatus.OK indicate success,
    # otherwise indicate request is failed, you can get error code
    # and message from code and message.
    if response.status_code == HTTPStatus.OK:
        print(response)
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.

simple_multimodal_conversation_call()