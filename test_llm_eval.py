import time
import json
import re
import csv
import os
from openai import OpenAI

# ===================== 配置，改成你自己的API =====================
API_KEY = "sk-pchgrY87VS5FsnFAivGSaRu5TT0rMMaElBfkSASj40M1HarE"
BASE_URL = "https://apihub.agnes-ai.com/v1"  # 换成你的接口地址
MODEL_NAME = "agnes-2.0-flash"
# =================================================================

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


# def call_llm(prompt: str) -> str:
#     """统一调用大模型，返回文本字符串"""
#     resp = client.chat.completions.create(
#         model=MODEL_NAME,
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.1
#     )
#     return resp.choices[0].message.content.strip()


# def judge_response(query, model_answer, expected_answer):
#     prompt = f"""
# 你是评测专家，请严格输出JSON，不要输出任何多余文字、注释。
# 字段：score(0‑10整数), is_hallucination(bool), comment(简短中文)
# query：{query}
# 模型回答：{model_answer}
# 参考答案：{expected_answer}
# """
#     time.sleep(1)
#     raw = call_llm(prompt).strip()
#     # 清洗 markdown ```json 代码块标记
#     raw = re.sub(r"^```json\s*", "", raw)
#     raw = re.sub(r"\s*```$", "", raw)
#     raw = raw.strip()
#     try:
#         return json.loads(raw)
#     except json.JSONDecodeError as e:
#         print(f"⚠️ judge解析失败，原始返回：{raw}")
#         return {
#             "score": 0,
#             "is_hallucination": True,
#             "comment": "大模型返回格式非法，解析JSON失败"
#         }


# def main():
#     with open("test_cases.json", "r", encoding="utf-8") as f:
#         cases = json.load(f)

#     total = len(cases)
#     result_rows = []

#     for idx, case in enumerate(cases):
#         category = case.get("category", "未分类")
#         q = case["query"]
#         expect = case["expected"]
#         print(f"\n[{idx+1}/{total}] query: {q}")

#         # 调用被测模型获取回答
#         model_out = call_llm(q)
#         print(f"模型回答: {model_out}")

#         judge_res = judge_response(q, model_out, expect)

#         score = judge_res.get("score", 0)
#         is_hallu = judge_res.get("is_hallucination", False)
#         comment = judge_res.get("comment", "")

#         print(f"score:{score}, is_hallucination:{is_hallu}, comment:{comment}")

#         result_rows.append({
#             "category": category,
#             "query": q,
#             "expected": expect,
#             "model_answer": model_out,
#             "score": score,
#             "is_hallucination": is_hallu,
#             "comment": comment
#         })

#     # 写入csv，Excel可以直接打开
#     csv_filename = "eval_result_2.csv"
#     headers = ["category", "query", "expected", "model_answer", "score", "is_hallucination", "comment"]
#     with open(csv_filename, "w", encoding="utf-8-sig", newline="") as f:
#         writer = csv.DictWriter(f, fieldnames=headers)
#         writer.writeheader()
#         writer.writerows(result_rows)

#     # 简单统计
#     all_score = [r["score"] for r in result_rows]
#     avg_score = sum(all_score)/len(all_score) if all_score else 0
#     hallu_count = sum(1 for r in result_rows if r["is_hallucination"])
#     print("\n====评测汇总====")
#     print(f"总用例：{len(result_rows)}")
#     print(f"平均分：{avg_score:.2f}")
#     print(f"幻觉数量：{hallu_count}")
#     print(f"结果已输出到 {csv_filename}")


# if __name__ == "__main__":
#     main()


def call_llm(prompt):
    max_retry = 5
    delay = 10  # 免费层速率限制窗口较长，初始等待10秒
    for i in range(max_retry):
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return resp.choices[0].message.content
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "rate limit" in err_msg.lower():
                print(f"[API限流] 等待{delay}s后重试，剩余重试次数：{max_retry - i -1}")
                time.sleep(delay)
                delay += 5
            else:
                raise
    raise Exception("达到最大重试次数，调用LLM失败")


def judge_response(query, model_answer, expected_answer):
    prompt = f"""
你是评测专家，请严格输出JSON，不要输出任何多余文字、注释。
字段：score(0‑10整数), is_hallucination(bool), comment(简短中文)
query：{query}
模型回答：{model_answer}
参考答案：{expected_answer}
"""
    time.sleep(1)
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
        query = case["query"]    
        ref = case["ref_answer"]    
        print(f"\n[{idx+1}/{len(cases)}] query: {query}")     

        # ===== 获取模型回答（保留原有被测模型逻辑） =====
        try:        
            time.sleep(2)  # 请求前先等2s        
            model_out = call_llm(query)        
            # 清洗markdown符号        
            model_out = re.sub(r"\*\*", "", model_out)        
            model_out = re.sub(r"\*", "", model_out)        
            model_out = re.sub(r"#+\s*", "", model_out)        
            model_out = re.sub(r"\n+", " ", model_out).strip()        
            print(f"模型回答: {model_out}")    
        except Exception as e:        
            model_out = ""        
            print(f"当前用例【被测模型】调用失败：达到最大重试次数，调用LLM失败")     

        # ===== Judge打分【注释掉LLM调用，不发第二个API请求】 =====
        # try:
        #     time.sleep(2) # judge请求前等待2s
        #     judge_prompt = f"参考答案：{ref}\n模型回答：{model_out}\n请输出：分数(0-10),是否幻觉(True/False),简短评语"
        #     judge_res = call_llm(judge_prompt)
        #     score, is_hallu, comment = parse_judge(judge_res)
        # except Exception as e:
        #     score = 0
        #     is_hallu = True
        #     comment = "Judge模型调用超时/限流，评测失败"
        
        # ===== Judge打分：调用LLM对模型回答进行评测 =====
        try:
            time.sleep(2)
            judge_prompt = f"""
你是评测专家，请严格输出JSON，不要输出任何多余文字、注释。
字段：score(0-10整数), is_hallucination(bool), comment(简短中文)
query：{query}
模型回答：{model_out}
参考答案：{ref}
"""
            judge_res = call_llm(judge_prompt)
            # 清洗 markdown ```json 代码块标记，提取 JSON 内容
            judge_res = re.sub(r"^```json\s*", "", judge_res, flags=re.DOTALL)
            judge_res = re.sub(r"\s*```$", "", judge_res, flags=re.DOTALL)
            judge_res = judge_res.strip()
            # 找不到 JSON 时尝试用正则提取第一个 {...}
            if not judge_res.startswith("{"):
                m = re.search(r"\{.*\}", judge_res, re.DOTALL)
                if m:
                    judge_res = m.group(0)
            # 尝试标准解析，失败则把单引号替换为双引号
            try:
                judge_dict = json.loads(judge_res)
            except json.JSONDecodeError:
                judge_dict = json.loads(judge_res.replace("'", '"'))
            score = judge_dict.get("score", 0)
            is_hallu = judge_dict.get("is_hallucination", False)
            comment = judge_dict.get("comment", "")
        except json.JSONDecodeError:
            # LLM可能返回单引号JSON，尝试替换后再解析
            try:
                judge_dict = json.loads(judge_res.replace("'", '"'))
                score = judge_dict.get("score", 0)
                is_hallu = judge_dict.get("is_hallucination", False)
                comment = judge_dict.get("comment", "")
            except Exception:
                print(f"[Judge] 解析失败，原始返回：{judge_res if 'judge_res' in dir() else ''}")
                score = 0
                is_hallu = True
                comment = "Judge解析JSON失败"
        except Exception as e:
            print(f"[Judge] 调用失败：{e}")
            score = 0
            is_hallu = True
            comment = "Judge调用失败"

        if model_out.strip() == "":
            score = 0
            is_hallu = True
            comment = "被测模型调用失败"

        print(f"Judge Result: score={score}, is_hallucination={is_hallu}, comment:{comment}")

        result_rows.append({
            "category": case.get("category", "未分类"),
            "query": query,
            "expected": ref,
            "model_answer": model_out,
            "score": score,
            "is_hallucination": is_hallu,
            "comment": comment
        })

        # 每条用例跑完，强制等待8秒冷却！！
        time.sleep(8)




    # 写入csv，Excel/WPS可以直接打开
    csv_filename = "eval_result_2.csv"
    headers = ["category", "query", "expected", "model_answer", "score", "is_hallucination", "comment"]
    with open(csv_filename, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(result_rows)
    # 简单统计
    all_score = [r["score"] for r in result_rows]
    avg_score = sum(all_score)/len(all_score) if all_score else 0
    hallu_count = sum(1 for r in result_rows if r["is_hallucination"])
    print("\n==================== 评测汇总 ====================")
    print(f"总用例：{len(result_rows)}")
    print(f"平均分：{avg_score:.2f}")
    print(f"幻觉数量：{hallu_count}")
    print(f"结果已输出到 {csv_filename}")

if __name__ == "__main__":
    main()