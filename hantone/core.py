# -*- coding: utf-8 -*-
"""HanTone 核心转换引擎。

处理流程
--------
1. 逐字扫描文本，按「最长词组优先」匹配 :data:`rules.PHRASE_RULES`；
2. 命中词组则直接采用规则读音并整体跳过，未命中再查单字表；
3. 按需要叠加姓氏读音、儿化、轻声与变调规则；
4. 交由 :mod:`hantone.style` 渲染为最终字符串。

该设计使多音字消歧发生在「词组」层面而非「单字」层面，
例如「银行」不会被误读为 ``yín xíng``。
"""

from __future__ import annotations

import unicodedata
from typing import List, Optional, Sequence, Set, Tuple, Union

from . import rules
from ._table import Syllable, definitions, lookup
from .style import STYLES, render, render_many

# 输出时对未收录字符的处理策略
ERROR_DEFAULT = 'default'   # 保留原字符
ERROR_IGNORE = 'ignore'     # 丢弃
ERROR_KEEP = 'keep'         # 保留原字符（同 default，语义更明确）

_ERROR_MODES = (ERROR_DEFAULT, ERROR_IGNORE, ERROR_KEEP)


def _is_hanzi(char: str) -> bool:
    """判断是否为 CJK 统一汉字（含扩展区）。"""
    code = ord(char)
    return (0x3400 <= code <= 0x4DBF      # 扩展 A
            or 0x4E00 <= code <= 0x9FFF   # 基本区
            or 0xF900 <= code <= 0xFAFF   # 兼容表意文字
            or 0x20000 <= code <= 0x2A6DF  # 扩展 B
            or 0x2A700 <= code <= 0x2EBEF) # 扩展 C~F


def annotate(text: str,
             mode: str = 'normal',
             sandhi: bool = False,
             erhua: bool = False) -> List[Tuple[str, Optional[Syllable]]]:
    """把文本标注为 ``(字符, 音节)`` 序列，非汉字音节为 ``None``。

    :param mode: ``normal`` 常规；``surname`` 视为姓名（首字用姓氏读音）
    :param sandhi: 是否应用「一/不」变调与三声变调。默认 ``False``，
        即输出《汉语拼音方案》规范本调；置为 ``True`` 得到口语实际读音。
    :param erhua: 是否把词尾「儿」并入前一音节（如 ``huar1``）
    """
    # 三元组：(字符, 音节, 是否被词组/姓氏规则锁定)
    entries: List[Tuple[str, Optional[Syllable], bool]] = []
    length = len(text)
    i = 0
    while i < length:
        char = text[i]

        # 姓氏模式：仅在开头匹配姓氏规则
        if mode == 'surname' and i == 0:
            hit = _match_surname(text, i)
            if hit:
                phrase, readings = hit
                for ch, syl in zip(phrase, readings):
                    entries.append((ch, syl, True))
                i += len(phrase)
                continue

        # 词组规则：最长优先匹配
        hit = _match_phrase(text, i)
        if hit:
            phrase, readings = hit
            for ch, syl in zip(phrase, readings):
                entries.append((ch, syl, True))
            i += len(phrase)
            continue

        if not _is_hanzi(char):
            entries.append((char, None, False))
            i += 1
            continue

        readings = lookup(char)
        entries.append((char, readings[0] if readings else None, False))
        i += 1

    # 收集有读音的音节，并记录来自规则的下标（不应被自动音变改写）
    sylls: List[Syllable] = []
    protected: Set[int] = set()
    for _ch, syl, locked in entries:
        if syl is not None:
            if locked:
                protected.add(len(sylls))
            sylls.append(syl)

    if erhua:
        sylls = _apply_erhua(list(zip([c for c, _, _ in entries], sylls)))
        protected = {p for p in protected if p < len(sylls)}
    if sandhi:
        sylls = rules.apply_neutral(sylls, protected)
        sylls = rules.apply_tone_sandhi(sylls, protected)

    # 把音变后的读音写回标注序列
    merged: List[Tuple[str, Optional[Syllable]]] = []
    idx = 0
    for ch, syl, _locked in entries:
        if syl is None:
            merged.append((ch, None))
        else:
            merged.append((ch, sylls[idx]))
            idx += 1
    return merged


def _match_phrase(text: str, start: int):
    """从 ``start`` 开始做最大正向匹配，返回 ``(词组, 读音元组)`` 或 ``None``。"""
    upper = min(rules.MAX_PHRASE_LEN, len(text) - start)
    for size in range(upper, 1, -1):
        phrase = text[start:start + size]
        readings = rules.PHRASE_RULES.get(phrase)
        if readings:
            return phrase, readings
    return None


def _match_surname(text: str, start: int):
    """匹配姓氏（优先匹配复姓）。"""
    for size in (2, 1):
        if start + size > len(text):
            continue
        name = text[start:start + size]
        readings = rules.SURNAME_RULES.get(name)
        if readings:
            return name, readings
    return None


def _apply_erhua(annotated: Sequence[Tuple[str, Optional[Syllable]]]) -> List[Syllable]:
    """儿化音处理：词尾「儿」并入前一音节，生成 ``huar1`` 这类形式。"""
    sylls = [syl for _ch, syl in annotated if syl is not None]
    if len(sylls) < 2:
        return sylls
    last_char, last_syl = annotated[-1]
    if last_char == '儿' and last_syl is not None:
        # 去掉末尾音节，把 r 附到前一个音节上
        tail = sylls.pop()
        if sylls:
            base, tone = sylls[-1]
            sylls[-1] = (base + 'r', tone if tone != 5 else tail[1])
    return sylls


def lazy_pinyin(text: str,
                style: str = 'mark',
                mode: str = 'normal',
                sandhi: bool = False,
                erhua: bool = False,
                errors: str = ERROR_DEFAULT) -> List[str]:
    """返回每个汉字对应的拼音列表（忽略非汉字）。

    >>> lazy_pinyin('中国银行')
    ['zhōng', 'guó', 'yín', 'háng']
    """
    if style not in STYLES:
        raise ValueError(f'未知 style: {style!r}，可选: {STYLES}')
    if errors not in _ERROR_MODES:
        raise ValueError(f'未知 errors: {errors!r}，可选: {_ERROR_MODES}')
    out: List[str] = []
    pending: List[str] = []       # 连续的非汉字片段，合并后整体输出
    for char, syl in annotate(text, mode=mode, sandhi=sandhi, erhua=erhua):
        if syl is None:
            if errors != ERROR_IGNORE:
                pending.append(char)
            continue
        if pending:
            out.append(''.join(pending))
            pending.clear()
        out.append(render(syl, style))
    if pending:
        out.append(''.join(pending))
    return out


def convert(text: str,
            style: str = 'mark',
            separator: str = ' ',
            mode: str = 'normal',
            sandhi: bool = False,
            erhua: bool = False,
            errors: str = ERROR_DEFAULT) -> str:
    """把整段文本转换为拼音字符串，保留标点与非汉字内容。

    默认排版会合并连续的英文/数字片段，并在标点两侧省略多余空格；
    显式传入 ``separator`` 时则对所有片段统一使用该分隔符连接。

    >>> convert('你好，世界！')
    'nǐ hǎo，shì jiè！'
    """
    if style not in STYLES:
        raise ValueError(f'未知 style: {style!r}，可选: {STYLES}')
    if errors not in _ERROR_MODES:
        raise ValueError(f'未知 errors: {errors!r}，可选: {_ERROR_MODES}')

    # 构建片段序列：汉字转为拼音，连续非汉字合并为原文片段
    tokens: List[Tuple[str, bool]] = []     # (内容, 是否为拼音)
    pending: List[str] = []
    for char, syl in annotate(text, mode=mode, sandhi=sandhi, erhua=erhua):
        if syl is None:
            if errors != ERROR_IGNORE:
                pending.append(char)
            continue
        if pending:
            tokens.append((''.join(pending), False))
            pending.clear()
        tokens.append((render(syl, style), True))
    if pending:
        tokens.append((''.join(pending), False))

    if separator != ' ':
        return separator.join(content for content, _ in tokens)
    return _layout(tokens)


def _is_punctuation(char: str) -> bool:
    """判断是否为标点或空白（用于决定是否需要空格分隔）。"""
    return bool(char) and (unicodedata.category(char)[0] in ('P', 'Z')
                           or char.isspace())


def _layout(tokens: Sequence[Tuple[str, bool]]) -> str:
    """按阅读习惯排版：拼音之间加空格，标点两侧不加空格。"""
    if not tokens:
        return ''
    buf: List[str] = [tokens[0][0]]
    for (prev_text, _), (cur_text, _cur_is) in zip(tokens, tokens[1:]):
        need_space = True
        if prev_text and _is_punctuation(prev_text[-1]):
            need_space = False
        elif cur_text and _is_punctuation(cur_text[0]):
            need_space = False
        if need_space:
            buf.append(' ')
        buf.append(cur_text)
    return ''.join(buf)


def slug(text: str, separator: str = '-', tone: bool = False) -> str:
    """生成 URL 友好的拼音别名，常用于文章标题转路径。

    >>> slug('汉语拼音转换引擎')
    'han-yu-pin-yin-zhuan-huan-yin-qing'
    """
    style = 'number' if tone else 'plain'
    parts = [p for p in lazy_pinyin(text, style=style, errors=ERROR_IGNORE)
             if p.strip()]
    return separator.join(parts)


def initials(text: str, style: str = 'first') -> str:
    """提取首字母缩写（默认取拼音首字母，``style='initial'`` 取完整声母）。"""
    if style not in ('first', 'initial'):
        raise ValueError("style 只能是 'first' 或 'initial'")
    return ''.join(lazy_pinyin(text, style=style, errors=ERROR_IGNORE))


def sort_key(text: str, tone: bool = True) -> Tuple:
    """生成中文排序键，可直接用于 ``sorted(key=...)``。

    默认按「拼音字母 + 声调」排序，解决 Python 默认的
    Unicode 码点排序不符合汉语习惯的问题。

    >>> names = ['张三', '李四', '王五']
    >>> sorted(names, key=sort_key)
    ['李四', '王五', '张三']
    """
    style = 'number' if tone else 'plain'
    key: List[str] = []
    for char, syl in annotate(text, sandhi=False):
        key.append(char if syl is None else render(syl, style))
    return tuple(key)


def heteronym(text: str, style: str = 'mark') -> List[List[str]]:
    """返回每个汉字的全部读音（多音字查询），非汉字返回空列表。"""
    out: List[List[str]] = []
    for char in text:
        if not _is_hanzi(char):
            out.append([])
            continue
        readings = lookup(char)
        if not readings:
            out.append([])
        else:
            out.append([render(syl, style) for syl in readings])
    return out


def explain(char: str) -> Optional[dict]:
    """查询单个汉字的读音与英文释义，未收录返回 ``None``。"""
    if len(char) != 1:
        raise ValueError('explain 只接受单个字符')
    readings = lookup(char)
    if not readings:
        return None
    meaning = definitions().get(ord(char))
    return {
        'char': char,
        'code_point': f'U+{ord(char):04X}',
        'pinyin': [render(s, 'mark') for s in readings],
        'pinyin_number': [render(s, 'number') for s in readings],
        'zhuyin': [render(s, 'zhuyin') for s in readings],
        'meaning': meaning,
        'heteronym': len(readings) > 1,
    }
