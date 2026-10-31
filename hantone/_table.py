# -*- coding: utf-8 -*-
"""HanTone 内置数据表加载层。

设计要点
--------
* 拼音数据以 ``zlib + base85`` 压缩后内嵌在 :mod:`hantone._data` 中，
  首次访问时才解压，避免 ``import hantone`` 产生不必要的启动开销。
* 解压结果缓存为模块级字典，汉字查询是 O(1) 的哈希查找。
* 英文释义体积较大且使用频率低，单独惰性加载，不影响主流程。

数据版权
--------
读音来源为 Unicode 官方 Unihan 数据库（Unicode License），属事实性语言数据，
经 ``tools/build_data.py`` 归一化、按规范优先级合并后重新编码存储。
"""

from __future__ import annotations

import base64
import zlib
from typing import Dict, List, Optional, Tuple

from . import _data

# 音节内部表示：(基础字母串, 声调编号 1-5)，例如 ('zhong', 1)
Syllable = Tuple[str, int]

_SYLLABLES: Optional[List[Syllable]] = None
_PINYIN_MAP: Optional[Dict[int, List[Syllable]]] = None
_DEFINITIONS: Optional[Dict[int, str]] = None


def _b85_decompress(blob: str) -> str:
    """把 base85 编码的 zlib 数据还原为文本。"""
    return zlib.decompress(base64.b85decode(blob)).decode('utf-8')


def syllables() -> List[Syllable]:
    """返回音节表，索引即音节 ID。"""
    global _SYLLABLES
    if _SYLLABLES is None:
        raw = _b85_decompress(_data._SYLLABLES_BLOB)
        # 形如 "zhong1,yi2,..."，末位数字为声调
        _SYLLABLES = [(item[:-1], int(item[-1])) for item in raw.split(',')]
    return _SYLLABLES


def pinyin_map() -> Dict[int, List[Syllable]]:
    """返回「汉字码点 -> 读音列表」映射，读音已按常用度排序。"""
    global _PINYIN_MAP
    if _PINYIN_MAP is None:
        syll = syllables()
        raw = _b85_decompress(_data._MAPPING_BLOB)
        table: Dict[int, List[Syllable]] = {}
        prev = 0
        for item in raw.split(';'):
            delta_hex, id_list = item.split(':')
            code_point = prev + int(delta_hex, 16)
            prev = code_point
            table[code_point] = [syll[int(i)] for i in id_list.split(',')]
        _PINYIN_MAP = table
    return _PINYIN_MAP


def definitions() -> Dict[int, str]:
    """返回「汉字码点 -> 英文释义」映射（惰性加载）。"""
    global _DEFINITIONS
    if _DEFINITIONS is None:
        raw = _data._DEFINITION_BLOB
        table: Dict[int, str] = {}
        if raw:
            text = _b85_decompress(raw)
            prev = 0
            for item in text.split('\n'):
                if ':' not in item:
                    continue
                delta_hex, meaning = item.split(':', 1)
                code_point = prev + int(delta_hex, 16)
                prev = code_point
                table[code_point] = meaning
        _DEFINITIONS = table
    return _DEFINITIONS


def lookup(char: str) -> Optional[List[Syllable]]:
    """查询单个汉字的全部读音，未收录返回 ``None``。"""
    if len(char) != 1:
        return None
    return pinyin_map().get(ord(char))


def hanzi_count() -> int:
    """收录的汉字总数。"""
    return len(pinyin_map())


def syllable_count() -> int:
    """收录的不同带调音节总数。"""
    return len(syllables())
