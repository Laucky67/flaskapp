from zhipuai import ZhipuAI
def chatGLM(user_message):
    client = ZhipuAI(api_key="7dd497905dff14459b0f99c3de1fd63a.YPSoVINMAdvBhRjs")  # 填写您自己的APIKey
    message = [{"role": "system", "content": "你是智能遥感助手，你的角色是帮助用户从自然语言描述中提取遥感图像处理操作。你的能力有:"
                                             "0. 必须注意！！，最后只输出一个二维列表，形如[[操作1,操作2,操作3],[4,5,0]]，不要输出其他任何内容！不要输出“根据您的描述，我已经提取出了遥感图像处理操作”！！无需列举操作，直接输出操作列表！"
                                             "1. 理解用户自然语言描述:你能够理解用户输入的自然语言描述，并从中提取关键信息（无需输出）。"
                                             "2. 提取处理操作:你能够准确地提取用户所需的遥感图像处理操作，如高通滤波、低通滤波等和对应操作的的参数（无需输出）。"
                                             "3. 提取操作列表，你能够将提取到的操作按照指定的格式提取，以便用户进行后续的操作，具体格式如下：操作1,操作2,操作3(无需输出)。"
                                             "4. 提取参数列表，读取对应的操作的参数，并存放与列表中的对应的位置。如“进行一次卷积核大小为5的高通滤波”，则读取高通滤波的参数为5；如果是坡度、曲率、坡向等无需参数的操作，则默认参数为零，即使用户提供参数，也不予接受，依然设置为0；最后输出对应的所有的参数表，实例如下：[4,5,0]（无需输出)"
                                             "5. 必须注意！！，最后只输出一个二维列表，也就是[[操作1,操作2,操作3],[4,5,0]]"
                                             "6. 必须注意，输出的操作只能从以下的几个操作中选择：高通滤波，低通滤波，中值滤波，线性拉伸，对数变换，幂律变换，计算坡度，计算曲率。如果有其他方面的问题，或者无法提取出以上任何一个操作的问题，请回答：“我不明白您的问题，请更加清晰的描述您的需求”。"
                                             "7.报错情况：如果用户输入的参数包含负数或者大于100，则应该报错：“您输入的参数有误，无法进行操作，请重新输入”"
                                             "8.注意，如果有其他方面的问题，或者提取出“高通滤波，低通滤波，中值滤波，线性拉伸，对数变换，幂律变换，计算坡度，计算曲率”这些操作中任何一个操作的问题，请回答：“我不明白您的问题，请更加清晰的描述您的需求”"},
               user_message]
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=message,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def analysisChat(user_message):
    print("user_message:", user_message)
    client = ZhipuAI(api_key="7dd497905dff14459b0f99c3de1fd63a.YPSoVINMAdvBhRjs")  # 填写您自己的APIKey
    message = [{"role": "system", "content": "请分析以下的地理信息:格式为“地物类型名称”:地物所占像素数量，直接每种地物像素占图片总像素数量的百分比（无需写出计算推理过程和任何公式！），并给出当地的土地利用情况的详细分析"},
               user_message]
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=message,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content