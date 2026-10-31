<div align="center">

# 🔤 HanTone

**零依赖 · 离线优先的汉字拼音转换引擎**
Zero-dependency, offline-first Mandarin Pinyin conversion engine

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](requirements.txt)
[![Hanzi](https://img.shields.io/badge/汉字-44%2C364-orange.svg)](#)
[![Tests](https://img.shields.io/badge/tests-34%20passed-brightgreen.svg)](#)

**🌐 选择语言 / Choose Language：**

[**简体中文**](#-简体中文) · [**繁體中文**](#-繁體中文) · [**English**](#-english)

</div>

---

<a id="-简体中文"></a>

# 🇨🇳 简体中文

## 🎉 项目介绍

**HanTone** 是一个**零第三方依赖、完全离线**的汉字拼音转换引擎，用纯 Python 标准库实现。

它解决的不是「把汉字查表换成拼音」这种简单问题，而是中文处理中最容易翻车的那件事——**多音字**。

> 大多数拼音工具在单字层面工作，于是「银行」被读成 `yín xíng`、「重庆」被读成 `zhòng qìng`。
> HanTone 在**词组层面**做消歧，因此 `yín háng` 和 `chóng qìng` 才是它的答案。

### 🎯 解决的核心痛点

| 😖 痛点 | ✨ HanTone 的解法 |
| --- | --- |
| 「银行 / 行走」读音不分 | 🎯 **405 条**词组级消歧规则，最长正向匹配 |
| 「重庆 / 重要」地名读错 | 🗺️ 内置地名专用读音（重庆、厦门、六安、丽水……） |
| 姓氏「单 / 仇 / 查」读错 | 👤 `mode='surname'` 姓氏模式，含 59 条复姓规则 |
| Python 中文排序不符合习惯 | 🔤 `sort_key()` 按拼音排序，而非 Unicode 码点 |
| 「一 / 不」的变调不会标 | 🗣️ `sandhi=True` 开启口语变调与三声变调 |
| 需要注音符号教学 | 🎵 内置 `ㄅㄆㄇㄈ` 注音符号（Bopomofo）输出 |
| 离线环境 / 内网无法装包 | 📦 **零依赖**，只用一个 `.py` 包，断网照跑 |

### 💡 自研差异化亮点

- 🧠 **词组优先于单字**：先用最长匹配命中词组规则，未命中才回落单字表。
- 🛡️ **规则保护机制**：词组规则已指定的读音不会被自动轻声/变调改写——所以「快乐」永远是 `kuài lè` 而不是 `kuài le`。
- 📚 **规范优先级合并**：读音来源按《通用规范汉字表》→《现代汉语词典》→《汉语大字典》→ Unicode 主读音 的顺序择优，避免古音污染现代读音。
- 🗜️ **紧凑数据编码**：44,364 字压缩为 500 KB 内嵌数据，惰性解压，启动无负担。

---

## ✨ 核心特性

- 🔤 **44,364 个汉字**、**1,456 个带调音节**、**5,479 个多音字**，覆盖 CJK 基本区与扩展 A/B 区
- 🎯 **405 条词组消歧规则** + **59 条姓氏规则**，最长正向匹配
- 🎨 **六种输出风格**：声调符号 · 数字调 · 无声调 · 声母 · 首字母 · **注音符号**
- 🗣️ **语流音变**：「一」「不」变调、三声变调、轻声、儿化音
- 🔤 **中文排序键**：按拼音排序，`sorted(names, key=hantone.sort_key)`
- 🔗 **URL 别名**：`slug('汉语拼音')` → `han-yu-pin-yin`
- 🔍 **多音字查询**：`heteronym()` 列出全部读音，`explain()` 附带英文释义
- 🖥️ **完整 CLI**：`pinyin / slug / initials / sort / lookup / info` 六个子命令
- 📦 **零第三方依赖**：仅用 `zlib / base64 / argparse / unicodedata`
- 🚫 **离线优先**：无网络请求、无外部数据文件、无遥测
- 🧪 **34 项单元测试**，覆盖数据完整性、消歧、变调、边界与异常

---

## 🚀 快速开始

### 📋 环境要求

- **Python 3.8 或更高版本**（仅标准库，无需任何第三方包）
- 支持 Windows / macOS / Linux
- **无需联网**

### 📥 安装

```bash
# 方式一：从源码安装（推荐）
git clone https://github.com/gitstq/HanTone.git
cd HanTone
make install          # 等价于 pip install -e .

# 方式二：直接用 PyPI 包
pip install hantone

# 方式三：零安装 —— 把 hantone/ 目录拷进你的项目即可
```

### ⚡ 三行上手

```python
import hantone

hantone.convert('中国银行')   # => 'zhōng guó yín háng'
hantone.convert('重庆')       # => 'chóng qìng'
hantone.convert('音乐')       # => 'yīn yuè'
```

### 🖥️ 命令行一步到位

```bash
python -m hantone pinyin 中国银行
# zhōng guó yín háng

python -m hantone pinyin 好好学习 --sandhi
# háo hǎo xué xí

python -m hantone slug 汉语拼音转换引擎
# han-yu-pin-yin-zhuan-huan-yin-qing

python -m hantone sort 张三 李四 王五 赵六
# 李四 / 王五 / 张三 / 赵六

python -m hantone lookup 行
```

---

## 📖 详细使用指南

### 1️⃣ 基础转换 `convert()`

```python
import hantone

hantone.convert('中华人民共和国')
# 'zhōng huá rén mín gòng hé guó'

hantone.convert('你好，世界！')
# 'nǐ hǎo，shì jiè！'          ← 标点两侧自动不加多余空格

hantone.convert('中国 ABC 2026')
# 'zhōng guó ABC 2026'          ← 英文与数字保持原样
```

**参数说明**

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `style` | `'mark'` | 输出风格，见下表 |
| `separator` | `' '` | 分隔符；非空格时对所有片段统一连接 |
| `mode` | `'normal'` | `'surname'` 启用姓氏读音 |
| `sandhi` | `False` | `True` 启用口语变调（默认输出规范本调） |
| `erhua` | `False` | `True` 合并词尾儿化音 |
| `errors` | `'default'` | `'ignore'` 丢弃非汉字；`'keep'` 保留 |

### 2️⃣ 六种输出风格

```python
text = '中华人民共和国'

hantone.convert(text, style='mark')      # 'zhōng huá rén mín gòng hé guó'  声调符号
hantone.convert(text, style='number')    # 'zhong1 hua2 ren2 min2 gong4 he2 guo2'
hantone.convert(text, style='plain')     # 'zhong hua ren min gong he guo'
hantone.convert(text, style='initial')   # 'zh h r m g h g'                 声母
hantone.convert(text, style='first')     # 'z h r m g h g'                  首字母
hantone.convert(text, style='zhuyin')    # 'ㄓㄨㄥ ㄏㄨㄚˊ ㄖㄣˊ ㄇㄧㄣˊ ㄍㄨㄥˋ ㄏㄜˊ ㄍㄨㄛˊ'
```

### 3️⃣ 多音字消歧（核心能力 ✨）

```python
hantone.convert('银行')   # 'yín háng'   ✅ 不是 yín xíng
hantone.convert('行走')   # 'xíng zǒu'
hantone.convert('重庆')   # 'chóng qìng' ✅ 不是 zhòng qìng
hantone.convert('重要')   # 'zhòng yào'
hantone.convert('音乐')   # 'yīn yuè'
hantone.convert('快乐')   # 'kuài lè'    ✅ 轻声规则不会误伤
hantone.convert('厦门')   # 'xià mén'
hantone.convert('六安')   # 'lù ān'
hantone.convert('出差')   # 'chū chāi'
hantone.convert('下载')   # 'xià zài'
```

### 4️⃣ 姓氏模式 👤

```python
hantone.convert('单')                          # 'dān'
hantone.convert('单', mode='surname')         # 'shàn'  ✅
hantone.convert('仇', mode='surname')         # 'qiú'
hantone.convert('查', mode='surname')         # 'zhā'
hantone.convert('曾', mode='surname')         # 'zēng'
hantone.convert('解', mode='surname')         # 'xiè'
hantone.convert('尉迟', mode='surname')       # 'yù chí'  ✅ 复姓
hantone.convert('万俟', mode='surname')       # 'mò qí'
```

### 5️⃣ 语流音变 🗣️

默认输出《汉语拼音方案》**规范本调**；需要口语实际读音时开启 `sandhi=True`。

```python
hantone.convert('你好')                        # 'nǐ hǎo'   规范本调
hantone.convert('你好', sandhi=True)           # 'ní hǎo'   三声变调 ✅

hantone.convert('一个')                        # 'yī gè'
hantone.convert('一个', sandhi=True)           # 'yí gè'    「一」在四声前变二声 ✅
hantone.convert('一天', sandhi=True)           # 'yì tiān'  「一」在一声前变四声 ✅

hantone.convert('不是')                        # 'bù shì'
hantone.convert('不是', sandhi=True)           # 'bú shì'   「不」在四声前变二声 ✅

hantone.convert('妈妈', sandhi=True)           # 'mā ma'    叠词轻声 ✅
```

> ⚠️ **注意**：词组规则中已显式标注的读音不会被变调改写，
> 因此 `hantone.convert('快乐', sandhi=True)` 仍然是 `kuài lè`。

### 6️⃣ 排序、别名与缩写 🔤

```python
# 按拼音排序中文（修正 Unicode 码点排序的不符合直觉）
names = ['张三', '李四', '王五', '赵六']
sorted(names, key=hantone.sort_key)
# ['李四', '王五', '张三', '赵六']

# 生成 URL 友好别名
hantone.slug('汉语拼音转换引擎')              # 'han-yu-pin-yin-zhuan-huan-yin-qing'
hantone.slug('汉语拼音', separator='_')       # 'han_yu_pin_yin'
hantone.slug('汉语拼音', tone=True)           # 'han4-yu3-pin1-yin1'

# 首字母缩写
hantone.initials('中国银行')                  # 'zgyh'
hantone.initials('中国银行', style='initial') # 'zhgyh'  完整声母
```

### 7️⃣ 查询与诊断 🔍

```python
hantone.heteronym('行')       # [['xíng', 'háng', 'héng']]

hantone.explain('中')
# {'char': '中', 'code_point': 'U+4E2D',
#  'pinyin': ['zhōng', 'zhòng'],
#  'zhuyin': ['ㄓㄨㄥ', 'ㄓㄨㄥˋ'],
#  'meaning': 'central; center, middle; in the midst of; hit (target); attain',
#  'heteronym': True}

hantone.hanzi_count()         # 44364
hantone.syllable_count()      # 1456
```

### 8️⃣ 命令行全参数 🖥️

```bash
python -m hantone pinyin  [文本...] [-s STYLE] [-d SEP] [--mode] [--sandhi] [--erhua] [--stdin]
python -m hantone slug     [文本...] [-d SEP] [--tone] [--stdin]
python -m hantone initials [文本...] [--full] [--stdin]
python -m hantone sort     [条目...] [--no-tone] [--stdin]
python -m hantone lookup   汉字 [-s STYLE]
python -m hantone info
```

管道用法：

```bash
echo 重庆银行 | python -m hantone pinyin --stdin
# chóng qìng yín háng

cat names.txt | python -m hantone sort --stdin
```

### 📊 典型使用场景

| 🏷️ 场景 | 💻 用法 |
| --- | --- |
| 博客 URL 生成 | `slug(article.title)` |
| 通讯录按拼音排序 | `sorted(contacts, key=lambda c: sort_key(c.name))` |
| 中文检索索引 | 同时索引原文与 `convert(text, style='plain')` |
| 汉字教学注音 | `convert(text, style='zhuyin')` |
| 数据清洗规范化 | `initials()` 生成缩写列 |
| 离线内网服务 | 直接拷贝 `hantone/` 目录，无需联网装包 |

> 📷 *运行截图与演示动图占位 —— 欢迎社区贡献 PR 补充。*

---

## 💡 设计思路与迭代规划

### 🏗️ 技术架构

```
hantone/
├── __init__.py     公共 API 门面
├── _data.py        压缩内嵌的拼音数据表（自动生成）
├── _table.py       数据加载与查询（惰性解压）
├── style.py        风格渲染（标调规则 / 注音符号）
├── rules.py        消歧规则库（词组 / 姓氏 / 音变）
├── core.py         核心转换引擎（最长匹配 + 音变 + 排版）
├── cli.py          命令行界面
└── __main__.py     python -m hantone
```

### 🧠 关键设计决策

**1. 为什么读音来源要分优先级？**
Unihan 的 `kHanyuPinyin`（《汉语大字典》）收录极全但含大量古音，直接用会让「行」冒出 `hàng`、`xìng` 这类现代罕用读音。HanTone 改用《通用规范汉字表》(2013) 优先，保证输出的是**现代规范普通话**。

**2. 为什么词组规则要被「保护」？**
早期版本让轻声规则作用于所有音节，结果「快乐」变成 `kuài le`、「厦门」变成 `xià men`。修正方案是给规则读音打上锁定标记，自动音变只作用于未锁定的音节。

**3. 为什么变调默认关闭？**
拼音标注的通行做法是标**本调**（「你好」写作 `nǐ hǎo`）。口语变调属于进阶需求，因此做成 `sandhi=True` 可选项。

**4. 为什么坚持零依赖？**
拼音是基础设施级能力。它若引入依赖，会让离线环境、内网部署、嵌入式场景全部失效。数据用 `zlib + base85` 内嵌，是体积与自包含性的最佳平衡。

### 🛣️ 后续迭代规划

- [ ] 🌏 扩展词组规则至 1000+ 条，并开放用户自定义词典加载
- [ ] 🈶 支持粤语（Jyutping）读音扩展
- [ ] 🔊 增加韵母押韵检测，服务诗词创作场景
- [ ] ⚡ 引入读音缓存，进一步降低重复调用开销
- [ ] 🧩 提供 JavaScript / WebAssembly 移植版本
- [ ] 📝 补充声调连读（如「不」在重叠词中读轻声）规则

### 🙋 社区贡献方向

最欢迎的三类 PR：

1. **🗺️ 地名与专有名词读音**（最容易发现错误的地方）
2. **📖 词组规则扩充**（附词典依据更佳）
3. **🌐 文档翻译与母语润色**

---

## 📦 打包与部署指南

本项目属于**工具库 / 命令行工具**类型，无需上传 Release 二进制包，按以下方式集成即可。

### 🔧 本地开发

```bash
git clone https://github.com/gitstq/HanTone.git
cd HanTone
make test           # 运行 34 项单元测试
make demo           # 功能演示
```

### 📦 构建分发包

```bash
# Unix / macOS / WSL
./build.sh build

# Windows
build.bat build

# 或使用标准工具链
python -m build
```

产物位于 `dist/`：`hantone-1.0.0.tar.gz` 与 `hantone-1.0.0-py3-none-any.whl`。

### 🚀 部署方式

| 🎯 方式 | 📝 命令 | ✅ 适用 |
| --- | --- | --- |
| PyPI 安装 | `pip install hantone` | 常规项目 |
| Wheel 离线安装 | `pip install hantone-1.0.0-py3-none-any.whl` | 内网环境 |
| 源码内嵌 | 拷贝 `hantone/` 目录到项目 | 零依赖打包 / 嵌入式 |
| 容器镜像 | `COPY hantone/ /app/hantone/` | Docker 部署 |

### 🔄 重新生成数据表

```bash
curl -O https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
unzip Unihan.zip
python tools/build_data.py Unihan_Readings.txt hantone/_data.py
```

### ⚙️ 兼容环境

- ✅ Python 3.8 / 3.9 / 3.10 / 3.11 / 3.12
- ✅ Windows 10+、macOS 10.15+、Linux（含 ARM）
- ✅ CPython 与 PyPy
- ✅ 完全离线运行，无任何网络请求

### ❗ 注意事项

- 📦 `_data.py` 约 500 KB，属生成产物但**必须随包分发**，请勿从仓库移除。
- 🧠 数据表首次访问时惰性解压，之后常驻内存（约 40 MB）。
- ⚠️ 生僻字的读音来自《汉语大字典》，可能包含现代罕用读音。
- 🗺️ 若发现地名读音错误，欢迎提交 Issue 并附词典依据。

---

## 🤝 贡献指南

- 📋 提交信息请遵循 **Angular 规范**：`feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`
- 🧪 新增功能请配套单元测试，并保证 `make test` 全绿
- 🚫 **硬性要求**：不得引入任何第三方运行时依赖
- 📖 详细规范见 [CONTRIBUTING.md](CONTRIBUTING.md)

提交 Issue 时请附：HanTone 版本、Python 版本、可复现的最小输入与期望/实际输出。

---

## 📄 开源协议说明

本项目采用 **MIT 开源协议**，详见 [LICENSE](LICENSE)。

- ✅ 允许商用、修改、分发、私有使用
- ✅ 无需署名（但欢迎Star ⭐）
- ❌ 不承担任何担保责任

**数据说明**：内置汉字读音表由本项目依据 Unicode 官方 Unihan 数据库（`Unihan_Readings.txt`，Unicode License）经归一化与规范优先级合并后重新编码生成，属事实性语言数据。

---

<a id="-繁體中文"></a>

# 🇹🇼 繁體中文

## 🎉 專案介紹

**HanTone** 是一套**零第三方依賴、完全離線**的漢字拼音轉換引擎，以純 Python 標準函式庫實作。

它要解決的並不是「把漢字查表換成拼音」這種簡單問題，而是中文處理裡最容易出錯的那一件事——**多音字**。

> 多數拼音工具只在單字層面運作，於是「銀行」被讀成 `yín xíng`、「重慶」被讀成 `zhòng qìng`。
> HanTone 在**詞組層面**進行消歧，因此 `yín háng` 與 `chóng qìng` 才是它的答案。

### 🎯 解決的核心痛點

| 😖 痛點 | ✨ HanTone 的解法 |
| --- | --- |
| 「銀行 / 行走」讀音不分 | 🎯 **405 條**詞組級消歧規則，最長正向匹配 |
| 「重慶 / 重要」地名讀錯 | 🗺️ 內建地名專用讀音（重慶、廈門、六安、麗水……） |
| 姓氏「單 / 仇 / 查」讀錯 | 👤 `mode='surname'` 姓氏模式，含 59 條複姓規則 |
| Python 中文排序不符合習慣 | 🔤 `sort_key()` 依拼音排序，而非 Unicode 碼位 |
| 「一 / 不」的變調不會標 | 🗣️ `sandhi=True` 開啟口語變調與三聲變調 |
| 需要注音符號教學 | 🎵 內建 `ㄅㄆㄇㄈ` 注音符號（Bopomofo）輸出 |
| 離線環境 / 內網無法裝套件 | 📦 **零依賴**，只用一個 `.py` 套件，斷網照跑 |

### 💡 自研差異化亮點

- 🧠 **詞組優先於單字**：先以最長匹配命中詞組規則，未命中才回落單字表。
- 🛡️ **規則保護機制**：詞組規則已指定的讀音不會被自動輕聲／變調改寫——所以「快樂」永遠是 `kuài lè` 而不是 `kuài le`。
- 📚 **規範優先順序合併**：讀音來源依《通用規範漢字表》→《現代漢語詞典》→《漢語大字典》→ Unicode 主讀音 的順序擇優，避免古音污染現代讀音。
- 🗜️ **緊湊資料編碼**：44,364 字壓縮為 500 KB 內嵌資料，惰性解壓，啟動無負擔。

---

## ✨ 核心特性

- 🔤 **44,364 個漢字**、**1,456 個帶調音節**、**5,479 個多音字**，涵蓋 CJK 基本區與擴充 A/B 區
- 🎯 **405 條詞組消歧規則** + **59 條姓氏規則**，最長正向匹配
- 🎨 **六種輸出風格**：聲調符號 · 數字調 · 無聲調 · 聲母 · 首字母 · **注音符號**
- 🗣️ **語流音變**：「一」「不」變調、三聲變調、輕聲、兒化音
- 🔤 **中文排序鍵**：依拼音排序，`sorted(names, key=hantone.sort_key)`
- 🔗 **URL 別名**：`slug('漢語拼音')` → `han-yu-pin-yin`
- 🔍 **多音字查詢**：`heteronym()` 列出全部讀音，`explain()` 附帶英文釋義
- 🖥️ **完整 CLI**：`pinyin / slug / initials / sort / lookup / info` 六個子命令
- 📦 **零第三方依賴**：僅用 `zlib / base64 / argparse / unicodedata`
- 🚫 **離線優先**：無網路請求、無外部資料檔、無遙測
- 🧪 **34 項單元測試**，涵蓋資料完整性、消歧、變調、邊界與例外

---

## 🚀 快速開始

### 📋 環境需求

- **Python 3.8 或更高版本**（僅標準函式庫，無需任何第三方套件）
- 支援 Windows / macOS / Linux
- **無需連網**

### 📥 安裝

```bash
# 方式一：從原始碼安裝（推薦）
git clone https://github.com/gitstq/HanTone.git
cd HanTone
make install          # 等同於 pip install -e .

# 方式二：直接用 PyPI 套件
pip install hantone

# 方式三：零安裝 —— 把 hantone/ 目錄複製進你的專案即可
```

### ⚡ 三行上手

```python
import hantone

hantone.convert('中国银行')   # => 'zhōng guó yín háng'
hantone.convert('重庆')       # => 'chóng qìng'
hantone.convert('音乐')       # => 'yīn yuè'
```

### 🖥️ 命令列一步到位

```bash
python -m hantone pinyin 中国银行
# zhōng guó yín háng

python -m hantone pinyin 好好学习 --sandhi
# háo hǎo xué xí

python -m hantone slug 汉语拼音转换引擎
# han-yu-pin-yin-zhuan-huan-yin-qing

python -m hantone sort 张三 李四 王五 赵六
# 李四 / 王五 / 张三 / 赵六

python -m hantone lookup 行
```

---

## 📖 詳細使用指南

### 1️⃣ 基礎轉換 `convert()`

```python
import hantone

hantone.convert('中华人民共和国')
# 'zhōng huá rén mín gòng hé guó'

hantone.convert('你好，世界！')
# 'nǐ hǎo，shì jiè！'          ← 標點兩側自動不加多餘空格

hantone.convert('中国 ABC 2026')
# 'zhōng guó ABC 2026'          ← 英文與數字保持原樣
```

**參數說明**

| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `style` | `'mark'` | 輸出風格，見下表 |
| `separator` | `' '` | 分隔符號；非空格時對所有片段統一連接 |
| `mode` | `'normal'` | `'surname'` 啟用姓氏讀音 |
| `sandhi` | `False` | `True` 啟用口語變調（預設輸出規範本調） |
| `erhua` | `False` | `True` 合併詞尾兒化音 |
| `errors` | `'default'` | `'ignore'` 丟棄非漢字；`'keep'` 保留 |

### 2️⃣ 六種輸出風格

```python
text = '中华人民共和国'

hantone.convert(text, style='mark')      # 'zhōng huá rén mín gòng hé guó'  聲調符號
hantone.convert(text, style='number')    # 'zhong1 hua2 ren2 min2 gong4 he2 guo2'
hantone.convert(text, style='plain')     # 'zhong hua ren min gong he guo'
hantone.convert(text, style='initial')   # 'zh h r m g h g'                 聲母
hantone.convert(text, style='first')     # 'z h r m g h g'                  首字母
hantone.convert(text, style='zhuyin')    # 'ㄓㄨㄥ ㄏㄨㄚˊ ㄖㄣˊ ㄇㄧㄣˊ ㄍㄨㄥˋ ㄏㄜˊ ㄍㄨㄛˊ'
```

### 3️⃣ 多音字消歧（核心能力 ✨）

```python
hantone.convert('银行')   # 'yín háng'   ✅ 不是 yín xíng
hantone.convert('行走')   # 'xíng zǒu'
hantone.convert('重庆')   # 'chóng qìng' ✅ 不是 zhòng qìng
hantone.convert('重要')   # 'zhòng yào'
hantone.convert('音乐')   # 'yīn yuè'
hantone.convert('快乐')   # 'kuài lè'    ✅ 輕聲規則不會誤傷
hantone.convert('厦门')   # 'xià mén'
hantone.convert('六安')   # 'lù ān'
hantone.convert('出差')   # 'chū chāi'
hantone.convert('下载')   # 'xià zài'
```

### 4️⃣ 姓氏模式 👤

```python
hantone.convert('单')                          # 'dān'
hantone.convert('单', mode='surname')         # 'shàn'  ✅
hantone.convert('仇', mode='surname')         # 'qiú'
hantone.convert('查', mode='surname')         # 'zhā'
hantone.convert('曾', mode='surname')         # 'zēng'
hantone.convert('解', mode='surname')         # 'xiè'
hantone.convert('尉迟', mode='surname')       # 'yù chí'  ✅ 複姓
hantone.convert('万俟', mode='surname')       # 'mò qí'
```

### 5️⃣ 語流音變 🗣️

預設輸出《漢語拼音方案》**規範本調**；需要口語實際讀音時開啟 `sandhi=True`。

```python
hantone.convert('你好')                        # 'nǐ hǎo'   規範本調
hantone.convert('你好', sandhi=True)           # 'ní hǎo'   三聲變調 ✅

hantone.convert('一个')                        # 'yī gè'
hantone.convert('一个', sandhi=True)           # 'yí gè'    「一」在四聲前變二聲 ✅
hantone.convert('一天', sandhi=True)           # 'yì tiān'  「一」在一聲前變四聲 ✅

hantone.convert('不是')                        # 'bù shì'
hantone.convert('不是', sandhi=True)           # 'bú shì'   「不」在四聲前變二聲 ✅

hantone.convert('妈妈', sandhi=True)           # 'mā ma'    疊詞輕聲 ✅
```

> ⚠️ **注意**：詞組規則中已明確標註的讀音不會被變調改寫，
> 因此 `hantone.convert('快乐', sandhi=True)` 仍然是 `kuài lè`。

### 6️⃣ 排序、別名與縮寫 🔤

```python
# 依拼音排序中文（修正 Unicode 碼位排序的不直覺）
names = ['张三', '李四', '王五', '赵六']
sorted(names, key=hantone.sort_key)
# ['李四', '王五', '张三', '赵六']

# 產生 URL 友善別名
hantone.slug('汉语拼音转换引擎')              # 'han-yu-pin-yin-zhuan-huan-yin-qing'
hantone.slug('汉语拼音', separator='_')       # 'han_yu_pin_yin'
hantone.slug('汉语拼音', tone=True)           # 'han4-yu3-pin1-yin1'

# 首字母縮寫
hantone.initials('中国银行')                  # 'zgyh'
hantone.initials('中国银行', style='initial') # 'zhgyh'  完整聲母
```

### 7️⃣ 查詢與診斷 🔍

```python
hantone.heteronym('行')       # [['xíng', 'háng', 'héng']]

hantone.explain('中')
# {'char': '中', 'code_point': 'U+4E2D',
#  'pinyin': ['zhōng', 'zhòng'],
#  'zhuyin': ['ㄓㄨㄥ', 'ㄓㄨㄥˋ'],
#  'meaning': 'central; center, middle; in the midst of; hit (target); attain',
#  'heteronym': True}

hantone.hanzi_count()         # 44364
hantone.syllable_count()      # 1456
```

### 8️⃣ 命令列全參數 🖥️

```bash
python -m hantone pinyin  [文本...] [-s STYLE] [-d SEP] [--mode] [--sandhi] [--erhua] [--stdin]
python -m hantone slug     [文本...] [-d SEP] [--tone] [--stdin]
python -m hantone initials [文本...] [--full] [--stdin]
python -m hantone sort     [条目...] [--no-tone] [--stdin]
python -m hantone lookup   漢字 [-s STYLE]
python -m hantone info
```

管線用法：

```bash
echo 重庆银行 | python -m hantone pinyin --stdin
# chóng qìng yín háng

cat names.txt | python -m hantone sort --stdin
```

### 📊 典型使用場景

| 🏷️ 場景 | 💻 用法 |
| --- | --- |
| 部落格 URL 產生 | `slug(article.title)` |
| 通訊錄依拼音排序 | `sorted(contacts, key=lambda c: sort_key(c.name))` |
| 中文檢索索引 | 同時索引原文與 `convert(text, style='plain')` |
| 漢字教學注音 | `convert(text, style='zhuyin')` |
| 資料清理正規化 | `initials()` 產生縮寫欄位 |
| 離線內網服務 | 直接複製 `hantone/` 目錄，無需連網裝套件 |

> 📷 *執行截圖與示範動畫預留位置 —— 歡迎社群貢獻 PR 補充。*

---

## 💡 設計思路與迭代規劃

### 🏗️ 技術架構

```
hantone/
├── __init__.py     公共 API 門面
├── _data.py        壓縮內嵌的拼音資料表（自動產生）
├── _table.py       資料載入與查詢（惰性解壓）
├── style.py        風格渲染（標調規則 / 注音符號）
├── rules.py        消歧規則庫（詞組 / 姓氏 / 音變）
├── core.py         核心轉換引擎（最長匹配 + 音變 + 排版）
├── cli.py          命令列介面
└── __main__.py     python -m hantone
```

### 🧠 關鍵設計決策

**1. 為什麼讀音來源要分優先順序？**
Unihan 的 `kHanyuPinyin`（《漢語大字典》）收錄極全但含大量古音，直接用會讓「行」冒出 `hàng`、`xìng` 這類現代罕用讀音。HanTone 改以《通用規範漢字表》(2013) 優先，保證輸出的是**現代規範普通話**。

**2. 為什麼詞組規則要被「保護」？**
早期版本讓輕聲規則作用於所有音節，結果「快樂」變成 `kuài le`、「廈門」變成 `xià men`。修正方案是給規則讀音加上鎖定標記，自動音變只作用於未鎖定的音節。

**3. 為什麼變調預設關閉？**
拼音標註的通行做法是標**本調**（「你好」寫作 `nǐ hǎo`）。口語變調屬進階需求，因此做成 `sandhi=True` 選項。

**4. 為什麼堅持零依賴？**
拼音是基礎設施級能力。它若引入依賴，會讓離線環境、內網部署、嵌入式場景全部失效。資料用 `zlib + base85` 內嵌，是體積與自包含性的最佳平衡。

### 🛣️ 後續迭代規劃

- [ ] 🌏 擴充詞組規則至 1000+ 條，並開放使用者自訂詞典載入
- [ ] 🈶 支援粵語（Jyutping）讀音擴充
- [ ] 🔊 增加韻母押韻偵測，服務詩詞創作場景
- [ ] ⚡ 引入讀音快取，進一步降低重複呼叫開銷
- [ ] 🧩 提供 JavaScript / WebAssembly 移植版本
- [ ] 📝 補充聲調連讀（如「不」在重疊詞中讀輕聲）規則

### 🙋 社群貢獻方向

最受歡迎的三類 PR：

1. **🗺️ 地名與專有名詞讀音**（最容易發現錯誤的地方）
2. **📖 詞組規則擴充**（附詞典依據更佳）
3. **🌐 文件翻譯與母語潤飾**

---

## 📦 打包與部署指南

本專案屬於**工具庫 / 命令列工具**類型，無需上傳 Release 二進位檔，依下列方式整合即可。

### 🔧 本地開發

```bash
git clone https://github.com/gitstq/HanTone.git
cd HanTone
make test           # 執行 34 項單元測試
make demo           # 功能示範
```

### 📦 建置發行套件

```bash
# Unix / macOS / WSL
./build.sh build

# Windows
build.bat build

# 或使用標準工具鏈
python -m build
```

產物位於 `dist/`：`hantone-1.0.0.tar.gz` 與 `hantone-1.0.0-py3-none-any.whl`。

### 🚀 部署方式

| 🎯 方式 | 📝 命令 | ✅ 適用 |
| --- | --- | --- |
| PyPI 安裝 | `pip install hantone` | 常規專案 |
| Wheel 離線安裝 | `pip install hantone-1.0.0-py3-none-any.whl` | 內網環境 |
| 原始碼內嵌 | 複製 `hantone/` 目錄到專案 | 零依賴打包 / 嵌入式 |
| 容器映像 | `COPY hantone/ /app/hantone/` | Docker 部署 |

### 🔄 重新產生資料表

```bash
curl -O https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
unzip Unihan.zip
python tools/build_data.py Unihan_Readings.txt hantone/_data.py
```

### ⚙️ 相容環境

- ✅ Python 3.8 / 3.9 / 3.10 / 3.11 / 3.12
- ✅ Windows 10+、macOS 10.15+、Linux（含 ARM）
- ✅ CPython 與 PyPy
- ✅ 完全離線執行，無任何網路請求

### ❗ 注意事項

- 📦 `_data.py` 約 500 KB，屬產生結果但**必須隨套件散布**，請勿從儲存庫移除。
- 🧠 資料表首次存取時惰性解壓，之後常駐記憶體（約 40 MB）。
- ⚠️ 生僻字的讀音來自《漢語大字典》，可能包含現代罕用讀音。
- 🗺️ 若發現地名讀音錯誤，歡迎提交 Issue 並附詞典依據。

---

## 🤝 貢獻指南

- 📋 提交資訊請遵循 **Angular 規範**：`feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`
- 🧪 新增功能請配套單元測試，並保證 `make test` 全數通過
- 🚫 **硬性要求**：不得引入任何第三方執行時依賴
- 📖 詳細規範見 [CONTRIBUTING.md](CONTRIBUTING.md)

提交 Issue 時請附：HanTone 版本、Python 版本、可重現的最小輸入與期望/實際輸出。

---

## 📄 開源協議說明

本專案採用 **MIT 開源協議**，詳見 [LICENSE](LICENSE)。

- ✅ 允許商用、修改、散布、私有使用
- ✅ 無需署名（但歡迎 Star ⭐）
- ❌ 不承擔任何擔保責任

**資料說明**：內建漢字讀音表由本專案依據 Unicode 官方 Unihan 資料庫（`Unihan_Readings.txt`，Unicode License）經正規化與規範優先順序合併後重新編碼產生，屬事實性語言資料。

---

<a id="-english"></a>

# 🇺🇸 English

## 🎉 Introduction

**HanTone** is a **zero-dependency, fully offline** Mandarin Pinyin conversion engine written against nothing but the Python standard library.

It is not trying to solve the easy problem of "look a character up in a table". It is aimed squarely at the thing that actually breaks Chinese text processing — **heteronyms**, characters with more than one reading.

> Most Pinyin tools operate at the single-character level, which is why 银行 comes out as `yín xíng` instead of `yín háng`, and 重庆 as `zhòng qìng` instead of `chóng qìng`.
> HanTone disambiguates at the **phrase** level, so `yín háng` and `chóng qìng` are what you get.

### 🎯 Pain points it removes

| 😖 Problem | ✨ How HanTone fixes it |
| --- | --- |
| 银行 / 行走 sound identical | 🎯 **405** phrase-level disambiguation rules, longest-match-first |
| Place names misread (重庆 / 重要) | 🗺️ Dedicated toponym readings: 重庆, 厦门, 六安, 丽水 … |
| Surnames misread (单 / 仇 / 查) | 👤 `mode='surname'` with 59 rules including compound surnames |
| Python sorts Chinese unintuitively | 🔤 `sort_key()` sorts by Pinyin, not by Unicode code point |
| No tone sandhi for 一 and 不 | 🗣️ `sandhi=True` enables spoken-form tone sandhi |
| Need Bopomofo for teaching | 🎵 Built-in `ㄅㄆㄇㄈ` Zhuyin output |
| Air-gapped / no-pip environments | 📦 **Zero dependencies**, one `.py` package, works offline |

### 💡 What makes this implementation different

- 🧠 **Phrase before character**: longest-match phrase rules win; the character table is only a fallback.
- 🛡️ **Protected rule readings**: readings pinned by a phrase rule are never rewritten by automatic sandhi — so 快乐 stays `kuài lè`, never `kuài le`.
- 📚 **Authority-ordered sources**: readings are merged in the order *General Standard Chinese Characters (2013)* → *Modern Chinese Dictionary* → *Hanyu Da Zidian* → Unicode default, keeping archaic readings out of modern output.
- 🗜️ **Compact encoding**: 44,364 characters compress into a 500 KB embedded blob, decompressed lazily on first use.

---

## ✨ Features

- 🔤 **44,364 hanzi**, **1,456 toned syllables**, **5,479 heteronyms**, covering CJK base and Extension A/B blocks
- 🎯 **405 phrase rules** + **59 surname rules**, longest-match-first
- 🎨 **Six output styles**: tone marks · tone numbers · untoned · initial · first letter · **Zhuyin**
- 🗣️ **Tone sandhi**: 一 / 不 sandhi, third-tone sandhi, neutral tone, erhua
- 🔤 **Chinese sort key**: `sorted(names, key=hantone.sort_key)`
- 🔗 **URL slugs**: `slug('汉语拼音')` → `han-yu-pin-yin`
- 🔍 **Heteronym lookup**: `heteronym()` lists every reading, `explain()` adds English glosses
- 🖥️ **Full CLI**: `pinyin / slug / initials / sort / lookup / info`
- 📦 **Zero third-party dependencies** — only `zlib / base64 / argparse / unicodedata`
- 🚫 **Offline-first**: no network calls, no external data files, no telemetry
- 🧪 **34 unit tests** covering data integrity, disambiguation, sandhi, edges and errors

---

## 🚀 Quick start

### 📋 Requirements

- **Python 3.8 or newer** (standard library only — nothing to install)
- Windows / macOS / Linux
- **No network access required**

### 📥 Installation

```bash
# Option 1: from source (recommended)
git clone https://github.com/gitstq/HanTone.git
cd HanTone
make install          # equivalent to: pip install -e .

# Option 2: from PyPI
pip install hantone

# Option 3: no install at all — just drop the hantone/ folder into your project
```

### ⚡ In three lines

```python
import hantone

hantone.convert('中国银行')   # => 'zhōng guó yín háng'
hantone.convert('重庆')       # => 'chóng qìng'
hantone.convert('音乐')       # => 'yīn yuè'
```

### 🖥️ CLI in one step

```bash
python -m hantone pinyin 中国银行
# zhōng guó yín háng

python -m hantone pinyin 好好学习 --sandhi
# háo hǎo xué xí

python -m hantone slug 汉语拼音转换引擎
# han-yu-pin-yin-zhuan-huan-yin-qing

python -m hantone sort 张三 李四 王五 赵六
# 李四 / 王五 / 张三 / 赵六

python -m hantone lookup 行
```

---

## 📖 Usage guide

### 1️⃣ Basic conversion `convert()`

```python
import hantone

hantone.convert('中华人民共和国')
# 'zhōng huá rén mín gòng hé guó'

hantone.convert('你好，世界！')
# 'nǐ hǎo，shì jiè！'          <- no stray spaces around punctuation

hantone.convert('中国 ABC 2026')
# 'zhōng guó ABC 2026'          <- Latin text and digits pass through
```

**Parameters**

| Parameter | Default | Meaning |
| --- | --- | --- |
| `style` | `'mark'` | Output style (see below) |
| `separator` | `' '` | Join separator; non-space values join every token uniformly |
| `mode` | `'normal'` | `'surname'` enables surname readings |
| `sandhi` | `False` | `True` applies spoken tone sandhi (default is citation tone) |
| `erhua` | `False` | `True` merges trailing 儿 into the previous syllable |
| `errors` | `'default'` | `'ignore'` drops non-hanzi; `'keep'` preserves them |

### 2️⃣ Six output styles

```python
text = '中华人民共和国'

hantone.convert(text, style='mark')      # 'zhōng huá rén mín gòng hé guó'  tone marks
hantone.convert(text, style='number')    # 'zhong1 hua2 ren2 min2 gong4 he2 guo2'
hantone.convert(text, style='plain')     # 'zhong hua ren min gong he guo'
hantone.convert(text, style='initial')   # 'zh h r m g h g'                 initials
hantone.convert(text, style='first')     # 'z h r m g h g'                  first letters
hantone.convert(text, style='zhuyin')    # 'ㄓㄨㄥ ㄏㄨㄚˊ ㄖㄣˊ ㄇㄧㄣˊ ㄍㄨㄥˋ ㄏㄜˊ ㄍㄨㄛˊ'
```

### 3️⃣ Heteronym disambiguation (the core feature ✨)

```python
hantone.convert('银行')   # 'yín háng'   ✅ not yín xíng
hantone.convert('行走')   # 'xíng zǒu'
hantone.convert('重庆')   # 'chóng qìng' ✅ not zhòng qìng
hantone.convert('重要')   # 'zhòng yào'
hantone.convert('音乐')   # 'yīn yuè'
hantone.convert('快乐')   # 'kuài lè'    ✅ neutral-tone rules don't corrupt it
hantone.convert('厦门')   # 'xià mén'
hantone.convert('六安')   # 'lù ān'
hantone.convert('出差')   # 'chū chāi'
hantone.convert('下载')   # 'xià zài'
```

### 4️⃣ Surname mode 👤

```python
hantone.convert('单')                          # 'dān'
hantone.convert('单', mode='surname')         # 'shàn'  ✅
hantone.convert('仇', mode='surname')         # 'qiú'
hantone.convert('查', mode='surname')         # 'zhā'
hantone.convert('曾', mode='surname')         # 'zēng'
hantone.convert('解', mode='surname')         # 'xiè'
hantone.convert('尉迟', mode='surname')       # 'yù chí'  ✅ compound surname
hantone.convert('万俟', mode='surname')       # 'mò qí'
```

### 5️⃣ Tone sandhi 🗣️

By default HanTone emits **citation tones** as prescribed by the *Hanyu Pinyin Fang'an*. Pass `sandhi=True` for the way people actually say it.

```python
hantone.convert('你好')                        # 'nǐ hǎo'   citation tone
hantone.convert('你好', sandhi=True)           # 'ní hǎo'   third-tone sandhi ✅

hantone.convert('一个')                        # 'yī gè'
hantone.convert('一个', sandhi=True)           # 'yí gè'    一 → 2nd before a 4th ✅
hantone.convert('一天', sandhi=True)           # 'yì tiān'  一 → 4th before a 1st ✅

hantone.convert('不是')                        # 'bù shì'
hantone.convert('不是', sandhi=True)           # 'bú shì'   不 → 2nd before a 4th ✅

hantone.convert('妈妈', sandhi=True)           # 'mā ma'    reduplication neutral tone ✅
```

> ⚠️ **Note:** readings explicitly pinned by a phrase rule are never rewritten by sandhi,
> so `hantone.convert('快乐', sandhi=True)` still returns `kuài lè`.

### 6️⃣ Sorting, slugs and acronyms 🔤

```python
# Sort Chinese by Pinyin instead of by Unicode code point
names = ['张三', '李四', '王五', '赵六']
sorted(names, key=hantone.sort_key)
# ['李四', '王五', '张三', '赵六']

# URL-friendly slugs
hantone.slug('汉语拼音转换引擎')              # 'han-yu-pin-yin-zhuan-huan-yin-qing'
hantone.slug('汉语拼音', separator='_')       # 'han_yu_pin_yin'
hantone.slug('汉语拼音', tone=True)           # 'han4-yu3-pin1-yin1'

# Acronyms
hantone.initials('中国银行')                  # 'zgyh'
hantone.initials('中国银行', style='initial') # 'zhgyh'  full initials
```

### 7️⃣ Lookup and diagnostics 🔍

```python
hantone.heteronym('行')       # [['xíng', 'háng', 'héng']]

hantone.explain('中')
# {'char': '中', 'code_point': 'U+4E2D',
#  'pinyin': ['zhōng', 'zhòng'],
#  'zhuyin': ['ㄓㄨㄥ', 'ㄓㄨㄥˋ'],
#  'meaning': 'central; center, middle; in the midst of; hit (target); attain',
#  'heteronym': True}

hantone.hanzi_count()         # 44364
hantone.syllable_count()      # 1456
```

### 8️⃣ Complete CLI 🖥️

```bash
python -m hantone pinyin  [text...] [-s STYLE] [-d SEP] [--mode] [--sandhi] [--erhua] [--stdin]
python -m hantone slug     [text...] [-d SEP] [--tone] [--stdin]
python -m hantone initials [text...] [--full] [--stdin]
python -m hantone sort     [items...] [--no-tone] [--stdin]
python -m hantone lookup   CHAR [-s STYLE]
python -m hantone info
```

Piping:

```bash
echo 重庆银行 | python -m hantone pinyin --stdin
# chóng qìng yín háng

cat names.txt | python -m hantone sort --stdin
```

### 📊 Typical use cases

| 🏷️ Scenario | 💻 Usage |
| --- | --- |
| Blog post slugs | `slug(article.title)` |
| Sorting a contact list | `sorted(contacts, key=lambda c: sort_key(c.name))` |
| Chinese search indexing | Index both the original text and `convert(text, style='plain')` |
| Teaching materials | `convert(text, style='zhuyin')` |
| Data normalisation | `initials()` for abbreviation columns |
| Air-gapped services | Copy the `hantone/` folder in — no install, no network |

> 📷 *Screenshots and demo GIF placeholders — community PRs welcome.*

---

## 💡 Design notes and roadmap

### 🏗️ Architecture

```
hantone/
├── __init__.py     public API surface
├── _data.py        compressed embedded Pinyin table (generated)
├── _table.py       data loading and lookup (lazy decompression)
├── style.py        style rendering (tone placement / Zhuyin)
├── rules.py        disambiguation rules (phrases / surnames / sandhi)
├── core.py         conversion engine (longest match + sandhi + layout)
├── cli.py          command-line interface
└── __main__.py     python -m hantone
```

### 🧠 Key design decisions

**1. Why are reading sources ranked?**
Unihan's `kHanyuPinyin` (*Hanyu Da Zidian*) is exhaustive but full of archaic readings; using it directly makes 行 sprout `hàng` and `xìng`. HanTone prefers the *General Standard Chinese Characters* (2013) so the output is **modern standard Mandarin**.

**2. Why are phrase rules "protected"?**
An early version applied neutral-tone rules to every syllable, turning 快乐 into `kuài le` and 厦门 into `xià men`. The fix marks rule-specified readings as locked, so automatic sandhi only touches unlocked syllables.

**3. Why is sandhi off by default?**
Pinyin annotation conventionally uses the **citation tone** (你好 is written `nǐ hǎo`). Spoken sandhi is an advanced need, so it is opt-in via `sandhi=True`.

**4. Why insist on zero dependencies?**
Pinyin is infrastructure. If it pulls in dependencies, offline, air-gapped and embedded scenarios all break. `zlib + base85` embedded data is the best balance of size and self-containment.

### 🛣️ Roadmap

- [ ] 🌏 Grow phrase rules past 1,000 and allow loading user dictionaries
- [ ] 🈶 Optional Cantonese (Jyutping) readings
- [ ] 🔊 Rhyme detection for poetry-writing use cases
- [ ] ⚡ Reading cache to cut repeated-lookup overhead
- [ ] 🧩 JavaScript / WebAssembly port
- [ ] 📝 More connected-speech rules (e.g. 不 as neutral in reduplicated verbs)

### 🙋 Where contributions help most

1. **🗺️ Toponym and proper-noun readings** — the most common source of errors
2. **📖 More phrase rules** — citing a dictionary is a plus
3. **🌐 Documentation translation and native-level polish**

---

## 📦 Packaging and deployment

HanTone is a **library / CLI tool**, so no Release binaries are published — integrate it as follows.

### 🔧 Local development

```bash
git clone https://github.com/gitstq/HanTone.git
cd HanTone
make test           # run 34 unit tests
make demo           # feature demo
```

### 📦 Building distributions

```bash
# Unix / macOS / WSL
./build.sh build

# Windows
build.bat build

# or the standard toolchain
python -m build
```

Artifacts land in `dist/`: `hantone-1.0.0.tar.gz` and `hantone-1.0.0-py3-none-any.whl`.

### 🚀 Deployment options

| 🎯 Method | 📝 Command | ✅ Best for |
| --- | --- | --- |
| PyPI | `pip install hantone` | regular projects |
| Offline wheel | `pip install hantone-1.0.0-py3-none-any.whl` | air-gapped networks |
| Vendor the source | copy `hantone/` into your project | dependency-free packaging / embedded |
| Container image | `COPY hantone/ /app/hantone/` | Docker deployments |

### 🔄 Regenerating the data table

```bash
curl -O https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
unzip Unihan.zip
python tools/build_data.py Unihan_Readings.txt hantone/_data.py
```

### ⚙️ Compatibility

- ✅ Python 3.8 / 3.9 / 3.10 / 3.11 / 3.12
- ✅ Windows 10+, macOS 10.15+, Linux (including ARM)
- ✅ CPython and PyPy
- ✅ Fully offline — zero network requests

### ❗ Caveats

- 📦 `_data.py` is roughly 500 KB. It is generated, but it **must ship with the package** — do not remove it.
- 🧠 The table is decompressed lazily on first access and then stays resident (~40 MB).
- ⚠️ Readings for rare characters come from *Hanyu Da Zidian* and may include archaic pronunciations.
- 🗺️ If you spot a wrong place-name reading, please open an issue with a dictionary citation.

---

## 🤝 Contributing

- 📋 Follow the **Angular commit convention**: `feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`
- 🧪 Add unit tests for new features and keep `make test` green
- 🚫 **Hard rule:** no third-party runtime dependencies
- 📖 See [CONTRIBUTING.md](CONTRIBUTING.md) for details

When opening an issue, please include: HanTone version, Python version, and a minimal reproducible input with expected vs. actual output.

---

## 📄 License

Released under the **MIT License** — see [LICENSE](LICENSE).

- ✅ Commercial use, modification, distribution and private use allowed
- ✅ No attribution required (a ⭐ is always welcome though)
- ❌ Provided without warranty of any kind

**Data notice:** the bundled readings were produced by this project from the Unicode Unihan Database (`Unihan_Readings.txt`, Unicode License) through normalisation and authority-ordered merging. They are factual linguistic data.

---

<div align="center">

**HanTone** · 零依赖 · 离线优先 · Zero-dependency & offline-first

如果这个项目帮到了你，欢迎点个 ⭐ Star！
If this project helped you, a ⭐ would be much appreciated!

</div>
