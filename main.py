from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)


def convert_format(openai_format):
    openai_format = json.loads(openai_format)
    phind_format = {
        'user_input': openai_format['messages'][-1]['content'],
        'message_history': openai_format['messages'],
        'requested_model': 'Phind Model',
        'challenge': openai_format['temperature']
    }
    return phind_format


@app.route('/v1/chat/completions', methods=['POST'])
def proxy():
    # 获取请求内容
    incoming_data = request.get_data(as_text=True)

    # 转换请求格式
    converted_data = convert_format(incoming_data)
    data = json.dumps(converted_data, ensure_ascii=False)

    # 设定目标API的URL和头部信息
    url = "https://https.api.phind.com/agent/"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
    }

    # 向目标API发送请求并获取响应
    response = requests.post(url, headers=headers,
                             data=data.encode('utf-8'), stream=True)

    # 将响应内容转换为生成器，以便可以流式传输
    def generate():
        for line in response.iter_lines():
            if line:
                yield line.decode('utf-8') + '\n'
        yield "data: [DONE]\n\n"

    # 创建流式响应
    return Response(generate(), content_type='text/event-stream')


@app.route('/')
def home():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=False, port=8080)
