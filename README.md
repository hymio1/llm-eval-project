<img width="2212" height="508" alt="image" src="https://github.com/user-attachments/assets/96b445d2-817b-4ce2-965d-ae347a175a90" /># llm‑eval‑project
> 轻量级 LLM‑as‑Judge 大模型自动评测工具，适合大模型效果验证、批量自动化评估。

## 项目简介
本项目实现 **LLM‑as‑Judge** 自动化评测方案，不需要人工逐条看回答打分。
程序批量读取 JSON 格式测试用例，调用被测大模型获取输出；再调用评判模型对回答进行打分（0‑10分）、识别内容幻觉；全部用例跑完后导出 CSV 评测报表，同时控制台输出整体统计指标。
内置 21 条面向软件测试领域的评测样例，可自行扩展替换为别的业务场景。

## 功能特性
- 📑 批量加载 JSON 测试数据集，循环调用被测大模型获取回答
- ⚖️ LLM‑as‑Judge 自动评判：输出分数、是否存在幻觉、简短评语
- 🛡️ 鲁棒容错机制：正则清洗模型返回的 Markdown 代码块；捕获 JSON 解析异常；**单条用例出错不会中断整个批量任务**
- 📊 自动统计总用例数、平均分、幻觉样例数量
- 📁 结果导出 CSV 文件，可用 Excel 打开做后续分析
- 🔌 兼容全部 OpenAI 协议接口：DeepSeek、豆包、通义千问等国内大模型都可以直接接入

## 目录结构
```
llm‑eval‑project/
├── test_llm_eval.py    # 主评测脚本
├── llm_api.py          # 大模型API调用封装
├── test_cases.json     # 测试用例数据集
├── eval_result.csv     # 运行后生成的评测结果（不上传git）
├── .env                # 存放密钥配置（不上传git）
└── .gitignore          # git忽略配置
```

## 环境依赖
Python >=3.8
```bash
pip install openai
```

## 快速开始
1. 修改代码配置，填入你的 `API_KEY`、`BASE_URL`、`MODEL_NAME`；密钥建议放置在 `.env` 文件，不要硬编码提交到代码仓库
2. 修改 `test_cases.json`，可以新增、修改业务测试问题
3. 执行脚本运行批量评测
```bash
python test_llm_eval.py
```
4. 执行结束，项目目录生成 `eval_result.csv`，保存每条用例的问题、标准答案、模型回答、得分、幻觉标记、评判评语。控制台打印汇总统计。

### 运行示例
控制台输出：
<img width="1718" height="784" alt="image" src="https://github.com/user-attachments/assets/31e672bf-b43b-4513-8381-7082cb453adc" />
评测结果CSV报表：
<img width="2212" height="508" alt="image" src="https://github.com/user-attachments/assets/77ab9722-a179-4b1e-bb99-31a9e8c3099d" />

## 项目难点与实现亮点
1. **模型输出不稳定兼容处理**：大模型经常返回 ```json```、多余解释文字，通过正则剥离 markdown 标记，再解析 JSON，提升评判结果解析成功率。
2. **异常降级设计**：捕获网络异常、JSON解析失败，记录异常信息继续执行下一条用例，避免一条失败导致全部评测终止。
3. **可扩展设计**：测试用例和业务解耦，修改json文件即可切换评测场景，不用改动核心代码。
4. **结果可复现**：结构化导出CSV，方便做对比实验，多次运行可以对比模型版本、参数的效果差异。

## 注意事项
- `.env`、`eval_result.csv`、缓存文件已配置在 `.gitignore`，请勿把密钥、本地运行结果提交到公开仓库
- 公开仓库不要直接写 API_KEY，防止密钥泄露产生费用
