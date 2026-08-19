import json
import re
import csv
from openai import OpenAI

# ===================== 配置，改成你自己的API =====================
API_KEY = "sk-pchgrY87VS5FsnFAivGSaRu5TT0rMMaElBfkSASj40M1HarE"
BASE_URL = "https://apihub.agnes-ai.com/v1"  # 换成你的接口地址
MODEL_NAME = "agnes-2.0-flash"
# =================================================================

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def call_llm(prompt: str) -> str:
    """统一调用大模型，返回文本字符串"""
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return resp.choices[0].message.content.strip()


def judge_response(query, model_answer, expected_answer):
    prompt = f"""
你是评测专家，请严格输出JSON，不要输出任何多余文字、注释。
字段：score(0‑10整数), is_hallucination(bool), comment(简短中文)
query：{query}
模型回答：{model_answer}
参考答案：{expected_answer}
"""
    raw = call_llm(prompt).strip()
    # 清洗 markdown ```json 代码块标记
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"⚠️ judge解析失败，原始返回：{raw}")
        return {
            "score": 0,
            "is_hallucination": True,
            "comment": "大模型返回格式非法，解析JSON失败"
        }


def main():
    with open("test_cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    total = len(cases)
    result_rows = []

    for idx, case in enumerate(cases):
        category = case.get("category", "未分类")
        q = case["query"]
        expect = case["expected"]
        print(f"\n[{idx+1}/{total}] query: {q}")

        # 调用被测模型获取回答
        model_out = call_llm(q)
        print(f"模型回答: {model_out}")

        judge_res = judge_response(q, model_out, expect)

        score = judge_res.get("score", 0)
        is_hallu = judge_res.get("is_hallucination", False)
        comment = judge_res.get("comment", "")

        print(f"score:{score}, is_hallucination:{is_hallu}, comment:{comment}")

        result_rows.append({
            "category": category,
            "query": q,
            "expected": expect,
            "model_answer": model_out,
            "score": score,
            "is_hallucination": is_hallu,
            "comment": comment
        })

    # 写入csv，Excel可以直接打开
    csv_filename = "eval_result.csv"
    headers = ["category", "query", "expected", "model_answer", "score", "is_hallucination", "comment"]
    with open(csv_filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(result_rows)

    # 简单统计
    all_score = [r["score"] for r in result_rows]
    avg_score = sum(all_score)/len(all_score) if all_score else 0
    hallu_count = sum(1 for r in result_rows if r["is_hallucination"])
    print("\n====评测汇总====")
    print(f"总用例：{len(result_rows)}")
    print(f"平均分：{avg_score:.2f}")
    print(f"幻觉数量：{hallu_count}")
    print(f"结果已输出到 {csv_filename}")


if __name__ == "__main__":
    main()
