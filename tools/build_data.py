# -*- coding: utf-8 -*-
"""
HanTone 数据构建脚本（开发期使用，不参与运行时）
数据源：Unicode 官方 Unihan_Readings.txt（Unicode License，事实性读音数据）
输出：hantone/_data.py —— zlib+base85 压缩内嵌的码点->拼音映射表
"""
import re, unicodedata, zlib, base64, collections, os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/Unihan_Readings.txt'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'hantone/_data.py'

# 组合声调标记 -> 声调编号
TONE_MARK = {'\u0304': 1, '\u0301': 2, '\u030c': 3, '\u0300': 4}
VOWELS = set('aeiouv')
# 允许作为鼻音单独成音节的情形（呣、嗯、哼等）
NASAL_ONLY = frozenset(('ng', 'm', 'n', 'hm', 'hng', 'ngm'))


def norm_syllable(raw):
    """把带声调符号的音节标准化为 (字母串, 声调1-5)。无法解析返回 None。

    Unihan 使用 IPA 式带调字母（如 zhōng / ǚ / ê̄ / ḿ），这里统一做
    Unicode NFD 分解后剥离声调标记，得到「基础字母 + 声调编号」。
    """
    s = raw.strip().lower()
    if not s:
        return None
    tone = 0
    letters = []
    for ch in unicodedata.normalize('NFD', s):
        if ch in TONE_MARK:
            tone = max(tone, TONE_MARK[ch])
        elif ch == '\u0308':
            # 分音符：u + ¨ => ü，在本项目中统一记作 v
            if letters and letters[-1] == 'u':
                letters[-1] = 'v'
        elif unicodedata.combining(ch):
            # 其余组合记号（抑扬符、短音符等）不影响拉丁转写，忽略
            continue
        elif 'a' <= ch <= 'z':
            letters.append(ch)
        else:
            return None
    base = ''.join(letters)
    if not base or not re.fullmatch(r'[a-z]+', base):
        return None
    if tone == 0:
        tone = 5  # 无调号视为轻声
    # 校验：合法音节应含元音，或属于少数鼻音音节
    if not (set(base) & VOWELS) and base not in NASAL_ONLY:
        return None
    return base, tone


# ---------- 解析 Unihan ----------
# 多音字来源按「现代汉语规范权威性」分级，优先级从高到低：
#   1. kTGHZ2013  《通用规范汉字表》(2013) —— 最新国家标准读音
#   2. kXHC1983   《现代汉语词典》
#   3. kHanyuPinyin 《汉语大字典》—— 收录最全，但含大量古音/罕用音
#   4. kSMSZD2003Readings —— 需剥离粤语注音后缀
#   5. kMandarin  Unicode 主读音（单音兜底）
TIER_FIELDS = ['kTGHZ2013', 'kXHC1983', 'kHanyuPinyin', 'kSMSZD2003Readings']

tiers = {f: {} for f in TIER_FIELDS}
mandarin = {}      # cp -> 默认读音（字母,调）
freq = {}          # cp -> {音节: 频次}
defs = {}          # cp -> 英文释义（仅保留短释义）

FIELD_RE = re.compile(r'^U\+([0-9A-Fa-f]+)\t(k\w+)\t(.*)$')
PINYIN_RE = re.compile(r'^([^\(]+)\((\d+)\)$')


def parse_loc_val(val, strip_yue=False):
    """解析 '480.020:zhōng 481.040:zhòng' 这类「位置:读音,读音」格式。"""
    seen = []
    for grp in val.split():
        body = grp
        if strip_yue and '\u7ca4' in body:      # 剥离「粵...」粤语注音
            body = body.split('\u7ca4', 1)[0]
        if ':' in body:
            body = body.split(':', 1)[1]
        for tok in body.split(','):
            r = norm_syllable(tok)
            if r and r not in seen:
                seen.append(r)
    return seen


with open(SRC, encoding='utf-8') as f:
    for line in f:
        m = FIELD_RE.match(line)
        if not m:
            continue
        cp, field, val = int(m.group(1), 16), m.group(2), m.group(3).strip()
        if field == 'kMandarin':
            for tok in val.split():
                r = norm_syllable(tok)
                if r:
                    mandarin.setdefault(cp, r)
                    break
        elif field in tiers:
            got = parse_loc_val(val, strip_yue=(field == 'kSMSZD2003Readings'))
            if got:
                tiers[field][cp] = got
        elif field == 'kHanyuPinlu':
            d = {}
            for tok in val.split():
                mm = PINYIN_RE.match(tok)
                if mm:
                    r = norm_syllable(mm.group(1))
                    if r:
                        d[r] = int(mm.group(2))
            if d:
                freq[cp] = d
        elif field == 'kDefinition':
            if len(val) <= 100 and cp not in defs:
                defs[cp] = val

for f_ in TIER_FIELDS:
    print(f'{f_:20}: {len(tiers[f_])}')
print(f'{"kMandarin":20}: {len(mandarin)}')
print(f'{"kHanyuPinlu":20}: {len(freq)}')
print(f'{"kDefinition":20}: {len(defs)}')

# ---------- 合并：按优先级为每个码点确定读音列表 ----------
allcp = set(mandarin)
for f_ in TIER_FIELDS:
    allcp |= set(tiers[f_])

table = {}
tier_hits = {f_: 0 for f_ in TIER_FIELDS}
tier_hits['kMandarin'] = 0
for cp in sorted(allcp):
    cands = []
    for f_ in TIER_FIELDS:
        if cp in tiers[f_]:
            cands = list(tiers[f_][cp])
            tier_hits[f_] += 1
            break
    if not cands:
        if cp in mandarin:
            cands = [mandarin[cp]]
            tier_hits['kMandarin'] += 1
        else:
            continue
    # 用 kHanyuPinlu 语料频次排序（常用读音在前）；同频次时 kMandarin 主读音优先
    fr = freq.get(cp, {})
    default_py = mandarin.get(cp)

    def key(py):
        return (-fr.get(py, 0), 0 if py == default_py else 1)

    cands.sort(key=key)
    out = []
    for c in cands:
        if c not in out:
            out.append(c)
    table[cp] = out

print('读音来源命中：', tier_hits)
print('合并后汉字数:', len(table))

# ---------- 序列化 ----------
# 音节表：去重后按索引引用，显著压缩体积
syll_index = {}
syll_list = []
for cp, pys in table.items():
    for base, tone in pys:
        k = (base, tone)
        if k not in syll_index:
            syll_index[k] = len(syll_list)
            syll_list.append(k)

parts = []
prev = 0
for cp in sorted(table):
    delta = cp - prev
    prev = cp
    idxs = ','.join(str(syll_index[p]) for p in table[cp])
    parts.append(f'{delta:x}:{idxs}')
payload = ';'.join(parts).encode('ascii')
syllpayload = ','.join(f'{b}{t}' for b, t in syll_list).encode('ascii')

comp_map = zlib.compress(payload, 9)
comp_syll = zlib.compress(syllpayload, 9)
b85_map = base64.b85encode(comp_map).decode('ascii')
b85_syll = base64.b85encode(comp_syll).decode('ascii')
print('音节数:', len(syll_list), '原始:', len(payload), '压缩:', len(comp_map))
print('音节表原始:', len(syllpayload), '压缩:', len(comp_syll))

# 释义（仅保留常用区，控制体积）
comp_defs = b''
b85_defs = ''
if defs:
    dparts = []
    prev = 0
    for cp in sorted(defs):
        dparts.append(f'{cp - prev:x}:{defs[cp]}')
        prev = cp
    dp = '\n'.join(dparts).encode('utf-8')
    comp_defs = zlib.compress(dp, 9)
    b85_defs = base64.b85encode(comp_defs).decode('ascii')
    print('释义原始:', len(dp), '压缩:', len(comp_defs))


def wrap(name, s):
    n = 96
    return '\n'.join('    "' + s[i:i + n] + '"' for i in range(0, len(s), n))


with open(OUT, 'w', encoding='utf-8') as f:
    f.write('# -*- coding: utf-8 -*-\n')
    f.write('"""\nHanTone 内置拼音数据表（自动生成，请勿手工编辑）\n\n')
    f.write('数据来源：Unicode 官方 Unihan 数据库（Unihan_Readings.txt, Unicode License）。\n')
    f.write('构建脚本：tools/build_data.py\n')
    f.write(f'收录汉字：{len(table)} 个，音节：{len(syll_list)} 个\n')
    f.write('存储格式：zlib(level 9) + base85 编码，运行时按需解压，无第三方依赖。\n"""\n\n')
    f.write('# 音节表：逗号分隔的 "<字母串><声调>" 序列，索引即音节 ID\n')
    f.write('_SYLLABLES_BLOB = (\n' + wrap('s', b85_syll) + '\n)\n\n')
    f.write('# 码点映射：分号分隔的 "<码点增量16进制>:<音节ID列表>" 序列\n')
    f.write('_MAPPING_BLOB = (\n' + wrap('m', b85_map) + '\n)\n\n')
    if b85_defs:
        f.write('# 英文释义：换行分隔的 "<码点增量16进制>:<释义>" 序列\n')
        f.write('_DEFINITION_BLOB = (\n' + wrap('d', b85_defs) + '\n)\n\n')
    else:
        f.write('_DEFINITION_BLOB = ""\n\n')
    f.write(f'HANZI_COUNT = {len(table)}\n')
    f.write(f'SYLLABLE_COUNT = {len(syll_list)}\n')

print('已写入', OUT, os.path.getsize(OUT), '字节')
