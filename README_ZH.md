# 维基百科翻译工具包 (Wikipedia Translation Toolkit)

<p align="center">
  <a href="README.md">বাংলা</a> | <a href="README_EN.md">English</a> | <b>中文</b>
</p>

这是一个针对维基百科开发的高性能自动化 Python 翻译与音译框架，专用于将**中文、日文、俄文、德文及英文**的维基百科条目、信息框（Infobox）、维基表格（Wikitable）及结构化列表精准翻译为标准孟加拉语（Standard Bengali），并严格执行**孟加拉语维基百科的13条强制性编辑规范**。

---

## 📑 目录
- [主要特性](#-主要特性)
- [语言翻译模块](#-语言翻译模块)
- [通用组件与架构](#-通用组件与架构)
- [内容翻译（CX）后处理器与网页仪表盘](#-内容翻译cx后处理器与网页仪表盘)
- [孟加拉语维基百科13条强制性规范](#-孟加拉语维基百科13条强制性规范)
- [安装与环境配置](#-安装与环境配置)
- [使用说明与快速上手](#-使用说明与快速上手)
  - [1. 命令行界面 (CLI)](#1-命令行界面-cli)
  - [2. Python 代码接口 (API)](#2-python-代码接口-api)
  - [3. 启动网页仪表盘](#3-启动网页仪表盘)
  - [4. 全系统功能演示](#4-全系统功能演示)
- [测试与规范验证](#-测试与规范验证)
- [项目目录结构](#-项目目录结构)
- [开源许可证](#-开源许可证)

---

## ✨ 主要特性

- **多语种专业音译与翻译引擎：** 针对汉语（汉字/拼音）、日语（平文式/训令式罗马字、假名）、俄语（西里尔字母音标）、德语（德语音系转换规范）以及英语设有独立的处理模块。
- **100% 遵循孟加拉语维基百科编辑规范：** 自动实施所有13项官方强制规则（如100%全孟加拉数字 `০-৯`、词首禁止出现'ৎ'、预组装变音字母 `য়, ড়, ঢ়`、面积单位强制转换为 `বর্গকিমি`、清除英语维护模板等）。
- **维基表格自动平衡与防错机制：** 解析 MediaWiki 表格标记，当单元格缺失时自动补全 `&nbsp;`，防止渲染表格右侧出现空白或错位。
- **本地可视化管理仪表盘：** 内置轻量级 Web 服务器与暗色调仪表盘界面（`http://127.0.0.1:8765/dashboard`），支持草稿实时后处理与一键规范验证。
- **高测试覆盖率：** 配备 54 项自动化单元测试，确保各语言模块、表格转换器与后处理流程 100% 稳定运行。

---

## 🌐 语言翻译模块

| 源语言 | 对应目录 | 核心功能与实现 |
|---|---|---|
| **中文 → 孟加拉语** | [`চীনা-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/চীনা-বাংলা%20অনুবাদ/) | • 拼音音节映射表与汉字到孟加拉语音译引擎 (`transliteration.py`)<br>• 中国行政区划代码、省市县地名词典 (`links_dictionary.py`)<br>• 行政区划表格与全页面翻译器 (`table_translator.py`, `translate_page.py`) |
| **日文 → 孟加拉语** | [`জাপানি-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/জাপানি-বাংলা%20অনুবাদ/) | • 平文式（Hepburn）与训令式罗马字转写引擎 (`japanese_transliteration.py`)<br>• 天皇、幕府将军及日本首相传记的三层标准格式与生卒年解析 (`prime_minister_notes.py`)<br>• 日文维基表格与日期转换 (`table_translator.py`, `number_converter.py`) |
| **俄文 → 孟加拉语** | [`রুশ-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/রুশ-বাংলা%20অনুবাদ/) | • 西里尔字母到标准孟加拉语音素的精准音译引擎 (`cyrillic_transliteration.py`)<br>• 俄罗斯全境85个联邦主体与行政区划词典 (`federal_subjects.py`)<br>• 俄罗斯区级行政表格与页面转换器 (`table_translator.py`, `translate_page.py`) |
| **德文 → 孟加拉语** | [`জার্মান-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/জার্মান-বাংলা%20অনুবাদ/) | • 德语音系规则（如首字母 $Z \to S$, Zimmermann $\to$ সিমারমান）<br>• 双语电影条目标题格式化：`''[[链接\|孟加拉语译名]]'' (''外文原名'')`<br>• 电影节奖项、类型、导演及演职人员映射 (`film_title_translator.py`) |
| **英文 → 孟加拉语** | [`ইংরেজি-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/ইংরেজি-বাংলা%20অনুবাদ/) | • 全维基文本章节标题、段落及信息框转换 (`translate_page.py`)<br>• 电影年表、传记及文学作品表格处理器 (`table_translator.py`)<br>• 序数词（1st $\to$ ১ম, 2nd $\to$ ২য়）与大数（million/billion）转换器 (`number_converter.py`) |

---

## 🛠️ 通用组件与架构

- [`common/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/common/):
  - `bengali_utils.py`: 核心数字转换（`0-9` $\to$ `০-৯`）、变音符规范化、统治年份（`r. [年份]` $\to$ `শাসনকাল: [বছর]`）、单位上标规范化（`km²` $\to$ `বর্গকিমি`）以及维护模板清除。
- [`cx_postprocess/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/cx_postprocess/):
  - `pipeline.py`: 针对维基媒体内容翻译（Content Translation, CX）输出的自动化后处理引擎。
  - `server.py`: 本地 HTTP Web 服务器，提供 REST API 支撑。
  - `draft_manager.py`: 本地翻译草稿的版本控制与状态管理。
  - `dashboard.html`: 响应式可视化前端界面。
- [`scripts/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/scripts/):
  - `fix_nukta.py`: 修复不规范的组合字符为预组合 Unicode 单字。
  - `check_digits.py`: 全文及表格扫描，定位残留的 ASCII 数字。
  - `sort_bengali.py`: 按孟加拉语标准字母排序（`অ-হ`）对列表重排。
  - `verify_table.py`: 检验表格行列结构与单元格对齐。
  - `stats.py`: 统计翻译进度与词数指标。
- [`wikitext_templates/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/wikitext_templates/):
  - 孟加拉语维基百科标准信息框（如 `তথ্যছক ব্যক্তি`, `তথ্যছক বসতি`, `তথ্যছক চলচ্চিত্র`）及常用模板。
- [`archive/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/archive/):
  - 已归档的历史翻译项目数据与临时脚本（蒙古区县、利比亚、坦桑尼亚等）。

---

## 🖥️ 内容翻译（CX）后处理器与网页仪表盘

工具包自带独立的本地图形化管理控制台。

```bash
# 启动仪表盘服务：
python cx_postprocess/server.py
```
在浏览器中访问：**`http://127.0.0.1:8765/dashboard`**

### 仪表盘核心功能：
1. **即时后处理：** 直接粘贴维基百科 CX 工具导出的初稿，一键应用全部13条规范。
2. **信息框与表格修复：** 修复破损的标记语言，自动清理多余的英文模板。
3. **本地草稿箱：** 本地保存、恢复及归档各类语言翻译任务。
4. **规范合规审查：** 实时检测任何违反孟加拉语维基百科准则的地方并标红警示。

---

## 📜 孟加拉语维基百科13条强制性规范

本工具箱在所有转换流程中坚决执行以下13条编辑规则：

1. **禁用 `{{Short description}}`：** 孟加拉语维基百科说明由 Wikidata 自动加载，条目中严禁保留该模板。
2. **100% 孟加拉数字：** 所有可见的年份、日期、页码、统计数字一律转为孟加拉数字（`০-৯`）。
3. **按孟加拉语字母表排序：** 人物及条目列表必须严格按孟加拉文字母顺序（`অ-হ`）排序，严禁使用英文字母 A-Z 顺序。
4. **词首严禁使用 'ৎ'：** 孟加拉语词首不得使用“ৎ”（如 `tsunami` $\to$ `সুনামি`，`Zimmermann` $\to$ `সিমারমান`）；词中或词尾允许使用“ৎস”。
5. **在位年代 'r.' 翻译：** 如君王在位时间 `r. 1200` 必须转换为 `শাসনকাল: ১২০০`。
6. **保持表格列数平衡：** 数据行单元格数必须与表头严格对齐，空单元格统一填充 `&nbsp;`。
7. **国家元首与政府首脑三层展示规范：** (1) 孟加拉文名称与内链，(2) 原文文字（汉字/西里尔文等），(3) 附带生卒年的拉丁转写。
8. **Defaultsort 与分类本地化：** 必须使用 `{{DEFAULTSORT:孟加拉文名称}}`，且所有分类均为孟加拉语。
9. **电影年表表头与人名音译：** 表头统一为 `! শিরোনাম !! পরিচালক !! অভিনয়ে !! ধরন !! মন্তব্য`，演职人员姓名100%音译为孟加拉语。
10. **双语电影标题规范：** 格式为 `''[[链接|孟加拉语译名]]'' (''原语片名'')`。
11. **使用预组合 Unicode 字符：** 必须使用预组合字形 `য়` (U+09DF), `ড়` (U+09DC), `ঢ়` (U+09DD)，严禁使用基字加附标的分解形式。
12. **禁止面积单位上标：** 严禁使用 `km²` 或 `কিমি²`，必须转换为 `বর্গকিমি` 或 `কিমি<sup>২</sup>`。
13. **清除英语维护与方言模板：** 彻底移除 `{{Use British English}}`, `{{Use dmy dates}}` 等无效英文模板。

---

## 📦 安装与环境配置

### 1. 克隆代码仓库
```bash
git clone https://github.com/example/wikipedia-translation-toolkit.git
cd "উইকিপিডিয়া অনুবাদ"
```

### 2. 安装依赖包
```bash
pip install -r requirements.txt
```

---

## ⚡ 使用说明与快速上手

### 1. 命令行界面 (CLI)

```bash
# 查看系统状态及支持的语种模块：
python cli.py info

# 翻译一篇完整的英文维基百科条目：
python cli.py english -i input_article.txt -o translated_article.txt

# 仅翻译德文维基表格：
python cli.py german -i film_table.txt -o bn_table.txt --table-only

# 验证已有译文是否完全符合13项规范：
python cli.py english -i translated_draft.txt --check-rules
```

### 2. Python 代码接口 (API)

```python
from wikipedia_translation_toolkit import WikipediaTranslator

translator = WikipediaTranslator()

# 翻译任意支持语种的维基文本
wikitext = """
{{Short description|American actress}}
{{Use British English}}
== Early life ==
She was born in 1995 and lived in an area of 500 km².
"""

translated = translator.translate_text(wikitext, source_lang="english")
print(translated)

# 校验是否符合孟加拉语维基百科规范
report = translator.validate_rules(translated)
if report["valid"]:
    print("✅ 全部规范验证通过！")
else:
    print("未合规项:", report["issues"])
```

### 3. 全系统综合演示
运行包含全部 7 个子系统的交互演示：
```bash
python examples/demo.py
```

---

## 🧪 测试与规范验证

运行完整的自动化测试套件（共54项测试）：
```bash
python run_all_tests.py
# 或直接调用 pytest：
pytest tests/ -v
```

清理缓存与临时构建文件：
```bash
python clean.py
```

---

## 📂 项目目录结构

```text
উইকিপিডিয়া অনুবাদ/
├── common/                         # 核心孟加拉语工具与规范化函数
├── cx_postprocess/                 # CX后处理引擎与本地Web仪表盘
├── scripts/                        # 变音符修复、数字验证与排序脚本
├── wikitext_templates/             # 维基百科标准信息框与表格模板
├── examples/                       # 调用示例与 demo.py 演示脚本
├── docs/                           # 架构设计与技术文档
├── tests/                          # 54项自动化单元测试集合
├── archive/                        # 历史翻译任务归档与原始数据
├── চীনা-বাংলা অনুবাদ/             # 中文-孟加拉语翻译引擎
├── জাপানি-বাংলা অনুবাদ/           # 日文-孟加拉语翻译引擎
├── রুশ-বাংলা অনুবাদ/               # 俄文-孟加拉语翻译引擎
├── জার্মান-বাংলা অনুবাদ/            # 德文-孟加拉语翻译引擎
├── ইংরেজি-বাংলা অনুবাদ/            # 英文-孟加拉语翻译引擎
├── wikipedia_translation_toolkit.py # 统一的顶级 Python 调用库
├── cli.py                          # 命令行交互工具
├── clean.py                        # 缓存清理脚本
├── run_all_tests.py                # 测试执行入口
├── README.md                       # 主说明文档 (孟加拉语)
├── README_EN.md                    # 英文说明文档
└── README_ZH.md                    # 中文说明文档
```

---

## 📄 开源许可证
本项目采用 [MIT 许可证](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/LICENSE)。
