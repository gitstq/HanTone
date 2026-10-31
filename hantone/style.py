# -*- coding: utf-8 -*-
"""拼音风格渲染层：把内部音节 ``(base, tone)`` 渲染成各种书写形式。

支持的风格
----------
===========  ==================  ==================
style        含义                示例（中 -> zhōng）
===========  ==================  ==================
mark         带调符号（默认）    zhōng
number       数字标调            zhong1
plain        无声调              zhong
initial      声母首字母          zh
first        拼音首字母          z
zhuyin       注音符号            ㄓㄨㄥ
unicode      带调 + ü 保留       zhōng
===========  ==================  ==================

标调规则严格遵循《汉语拼音方案》：a 优先，其次 o、e，
i/u 并列时标在后一个，单个元音标在该元音上，轻声不标调。
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from ._table import Syllable

# 元音 -> 五种声调对应的带调字符（索引 0 未使用，便于 tone 直接索引）
_TONE_VOWELS: Dict[str, str] = {
    'a': 'aāáǎà',
    'o': 'oōóǒò',
    'e': 'eēéěè',
    'i': 'iīíǐì',
    'u': 'uūúǔù',
    'v': 'üǖǘǚǜ',
}
_VOWEL_CHARS = 'aoeiv'
_ALL_VOWELS = 'aoeiuv'

# 注音符号：声母
_ZHUYIN_INITIALS: List[Tuple[str, str]] = [
    ('zh', 'ㄓ'), ('ch', 'ㄔ'), ('sh', 'ㄕ'),
    ('b', 'ㄅ'), ('p', 'ㄆ'), ('m', 'ㄇ'), ('f', 'ㄈ'),
    ('d', 'ㄉ'), ('t', 'ㄊ'), ('n', 'ㄋ'), ('l', 'ㄌ'),
    ('g', 'ㄍ'), ('k', 'ㄎ'), ('h', 'ㄏ'),
    ('j', 'ㄐ'), ('q', 'ㄑ'), ('x', 'ㄒ'),
    ('r', 'ㄖ'), ('z', 'ㄗ'), ('c', 'ㄘ'), ('s', 'ㄙ'),
]

# 注音符号：韵母（按长度降序匹配，保证 uang 优先于 u + ang）
_ZHUYIN_FINALS: List[Tuple[str, str]] = [
    ('iong', 'ㄩㄥ'), ('uang', 'ㄨㄤ'), ('ueng', 'ㄨㄥ'),
    ('iang', 'ㄧㄤ'), ('uan', 'ㄨㄢ'), ('van', 'ㄩㄢ'),
    ('iao', 'ㄧㄠ'), ('ing', 'ㄧㄥ'), ('ong', 'ㄨㄥ'),
    ('ang', 'ㄤ'), ('eng', 'ㄥ'), ('er', 'ㄦ'),
    ('ai', 'ㄞ'), ('ei', 'ㄟ'), ('ao', 'ㄠ'), ('ou', 'ㄡ'),
    ('an', 'ㄢ'), ('en', 'ㄣ'), ('in', 'ㄧㄣ'),
    ('un', 'ㄨㄣ'), ('vn', 'ㄩㄣ'), ('iu', 'ㄧㄡ'),
    ('ui', 'ㄨㄟ'), ('ie', 'ㄧㄝ'), ('ve', 'ㄩㄝ'),
    ('ve', 'ㄩㄝ'), ('ia', 'ㄧㄚ'), ('ua', 'ㄨㄚ'),
    ('uo', 'ㄨㄛ'), ('a', 'ㄚ'), ('o', 'ㄛ'), ('e', 'ㄜ'),
    ('i', 'ㄧ'), ('u', 'ㄨ'), ('v', 'ㄩ'),
]

# 整体认读音节：介音 i/u/ü 改写为 y/w 后需还原
_ZHUYIN_SPECIAL: Dict[str, str] = {
    'zhi': 'ㄓ', 'chi': 'ㄔ', 'shi': 'ㄕ', 'ri': 'ㄖ',
    'zi': 'ㄗ', 'ci': 'ㄘ', 'si': 'ㄙ',
    'yi': 'ㄧ', 'wu': 'ㄨ', 'yu': 'ㄩ',
    'ye': 'ㄧㄝ', 'yue': 'ㄩㄝ', 'yuan': 'ㄩㄢ', 'yun': 'ㄩㄣ',
    'yin': 'ㄧㄣ', 'ying': 'ㄧㄥ', 'yang': 'ㄧㄤ', 'yong': 'ㄩㄥ',
    'yan': 'ㄧㄢ', 'yao': 'ㄧㄠ', 'you': 'ㄧㄡ', 'weng': 'ㄨㄥ',
}

_ZHUYIN_TONES = {1: '', 2: 'ˊ', 3: 'ˇ', 4: 'ˋ', 5: '˙'}

# 常见声母集合，用于截取「首字母 / 声母」时判断双字母声母
_MULTI_INITIALS = ('zh', 'ch', 'sh')


def _tone_vowel_position(base: str) -> int:
    """返回需要标注声调的元音下标；没有元音时返回 -1。"""
    for vowel in ('a', 'o', 'e'):
        pos = base.find(vowel)
        if pos >= 0:
            return pos
    # i/u/ü 并列标在后一个：取最靠后的元音
    for pos in range(len(base) - 1, -1, -1):
        if base[pos] in _ALL_VOWELS:
            return pos
    return -1


def apply_tone_mark(base: str, tone: int) -> str:
    """把 ``('zhong', 1)`` 渲染为 ``'zhōng'``。

    ``ü`` 在内部以 ``v`` 存储，输出时还原为 ``ü``。轻声（5）不标调。
    """
    if tone not in (1, 2, 3, 4):
        return base.replace('v', 'ü')
    pos = _tone_vowel_position(base)
    if pos < 0:
        return base.replace('v', 'ü')
    char = base[pos]
    marked = _TONE_VOWELS.get(char, _TONE_VOWELS['a'])[tone]
    return base[:pos] + marked + base[pos + 1:].replace('v', 'ü')


def to_zhuyin(base: str, tone: int) -> str:
    """把音节转换为注音符号（带调号）。

    例：``('zhong', 1)`` -> ``ㄓㄨㄥ``，``('hao', 3)`` -> ``ㄏㄠˇ``。
    """
    body = base.replace('v', 'u')
    if body in _ZHUYIN_SPECIAL:
        marks = _ZHUYIN_SPECIAL[body]
    else:
        initial = ''
        for pinyin_part, mark in _ZHUYIN_INITIALS:
            if body.startswith(pinyin_part):
                initial = mark
                body = body[len(pinyin_part):]
                break
        final = ''
        remaining = body
        while remaining:
            for pinyin_part, mark in _ZHUYIN_FINALS:
                if remaining.startswith(pinyin_part):
                    final += mark
                    remaining = remaining[len(pinyin_part):]
                    break
            else:
                # 无法匹配的残段原样保留，避免出现静默丢字
                final += remaining[0]
                remaining = remaining[1:]
        marks = initial + final
    return marks + _ZHUYIN_TONES.get(tone, '')


def render(syllable: Syllable, style: str = 'mark') -> str:
    """按指定风格渲染单个音节。未知风格回退到 ``mark``。"""
    base, tone = syllable
    if style in ('mark', 'unicode'):
        return apply_tone_mark(base, tone)
    if style == 'number':
        return f'{base.replace("v", "u")}{tone}' if tone != 5 else base.replace('v', 'u')
    if style == 'plain':
        return base.replace('v', 'u')
    if style == 'initial':
        # 声母：zh/ch/sh 视为整体，其余取首字母
        for multi in _MULTI_INITIALS:
            if base.startswith(multi):
                return multi
        return base[0]
    if style == 'first':
        return base[0]
    if style == 'zhuyin':
        return to_zhuyin(base, tone)
    return apply_tone_mark(base, tone)


def render_many(syllables: List[Syllable], style: str = 'mark',
                separator: str = ' ') -> str:
    """渲染音节序列并用分隔符连接。"""
    return separator.join(render(s, style) for s in syllables)


STYLES = ('mark', 'number', 'plain', 'initial', 'first', 'zhuyin')
