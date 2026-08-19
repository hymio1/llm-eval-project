import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 读取环境变量
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


def chat_completion(prompt: str, temperature: float = 0.1) -> str:
    """
    OpenAI统一调用接口
    :param prompt: 用户输入prompt
    :param temperature: 温度，评测场景建议0.1
    :return: 返回模型文本输出
    """
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return resp.choices[0].message.content.strip()


if __name__ == "__main__":
    # 简单自测
    print(chat_completion("hello, say one word"))
