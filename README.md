# LLM 自动化评测 Demo
> 轻量级大模型自动化评测工具，可作为Side‑Project写进软件测试 / AI应用简历。
基于LLM‑as‑Judge思想：使用大模型充当裁判，自动完成问答任务打分、幻觉检测，输出CSV评测报告。

## ✨项目特性
- 基于OpenAI兼容API，方便切换各类大模型服务
- LLM‑as‑Judge自动打分，自动识别幻觉样本
- JSON管理测试集，输出结构化CSV评测报告
- 解耦设计：接口层与评测业务分离，便于扩展
- 可对接 GitHub Actions，提交代码自动执行评测CI

## 📁项目目录
```
├── .env                # API密钥配置，禁止提交Git
├── .gitignore
├── llm_api.py          # LLM接口封装模块
├── eval_demo.py        # 主评测脚本
├── test_cases.json     # 测试用例集
└── eval_result.csv     # 运行后自动生成评测报告
```

## 🚀快速运行

### 1.安装依赖
```bash
pip install openai python-dotenv
```

### 2.配置环境变量 `.env`
```env
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

### 3.准备测试用例
编辑`test_cases.json`，格式：
```json
[
  {
    "query":"问题",
    "expected":"参考答案",
    "category":"分类标签"
  }
]
```

### 4.启动评测
```bash
python eval_demo.py
```
运行完成输出`eval_result.csv`，包含每条用例：类别、问题、标准答案、模型输出、分数、幻觉标记、评语。

## 📊输出指标
- 总测试用例数量
- 整体平均分（0‑10）
- 幻觉样本计数、幻觉占比

## 🔧后续拓展方向（简历亮点）
1. 扩充测试集至100+条，覆盖知识、数学、推理、幻觉场景
2. 接入GitHub‑Actions CI，代码提交自动跑评测
3. 增加HTML可视化报告
4. 支持多模型批量对比评测
5. 支持本地大模型（Ollama）接入

## ⚠️安全提醒
- `.env`存放密钥，**严禁上传至GitHub**，已经配置在`.gitignore`
- 中转接口注意base_url必须以`/v1`结尾
- 循环调用添加sleep，避免触发API限流429
