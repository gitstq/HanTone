# -*- coding: utf-8 -*-
"""HanTone —— 零依赖 · 离线优先的汉字拼音转换引擎。

核心能力
--------
* **多音字词组级消歧**：在词组层面决定读音，「银行」不会读成 yín xíng。
* **六种输出风格**：声调符号、数字调、无声调、声母、首字母、注音符号。
* **语流音变**：「一」「不」变调、三声变调、轻声、儿化。
* **中文排序键**：按拼音而非 Unicode 码点排序中文。
* **姓氏模式**：单(shàn)、仇(qiú)、查(zhā) 等姓氏专用读音。

快速上手
--------
>>> import hantone
>>> hantone.convert('中国银行')
'zhōng guó yín háng'
>>> hantone.convert('好好学习，天天向上')
'hǎo hǎo xué xí ， tiān tiān xiàng shàng'
>>> hantone.slug('汉语拼音转换引擎')
'han-yu-pin-yin-zhuan-huan-yin-qing'
>>> sorted(['张三', '李四', '王五'], key=hantone.sort_key)
['李四', '王五', '张三']
"""

from __future__ import annotations

from ._table import hanzi_count, syllable_count
from .core import (
    ERROR_DEFAULT,
    ERROR_IGNORE,
    ERROR_KEEP,
    annotate,
    convert,
    explain,
    heteronym,
    initials,
    lazy_pinyin,
    slug,
    sort_key,
)
from .style import STYLES, render, render_many, to_zhuyin

__version__ = '1.0.0'
__license__ = 'MIT'
__all__ = [
    'convert', 'lazy_pinyin', 'slug', 'initials', 'sort_key',
    'heteronym', 'explain', 'annotate',
    'render', 'render_many', 'to_zhuyin', 'STYLES',
    'hanzi_count', 'syllable_count',
    'ERROR_DEFAULT', 'ERROR_IGNORE', 'ERROR_KEEP',
    '__version__',
]
