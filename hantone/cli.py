# -*- coding: utf-8 -*-
"""HanTone 命令行界面。

零第三方依赖，仅使用标准库 ``argparse``。
提供 ``pinyin / slug / sort / lookup / info`` 五个子命令。
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from ._table import definitions, hanzi_count, syllable_count
from .core import convert, explain, heteronym, initials, slug, sort_key
from .style import STYLES


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='hantone',
        description='HanTone —— 零依赖 · 离线优先的汉字拼音转换引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            '示例:\n'
            '  hantone pinyin 中国银行\n'
            '  hantone pinyin 好好学习 --style number\n'
            '  hantone pinyin 你好 --sandhi\n'
            '  hantone slug 汉语拼音转换引擎\n'
            '  hantone sort 张三 李四 王五\n'
            '  hantone lookup 行\n'
            '  echo 中国银行 | hantone pinyin --stdin\n'
        ),
    )
    parser.add_argument('-V', '--version', action='version',
                        version=f'HanTone {__version__}')
    sub = parser.add_subparsers(dest='command', metavar='<命令>')

    # ---- pinyin ----
    p = sub.add_parser('pinyin', help='把文本转换为拼音')
    p.add_argument('text', nargs='*', help='待转换的文本（省略时配合 --stdin）')
    p.add_argument('-s', '--style', default='mark', choices=STYLES,
                   help='输出风格（默认 mark）')
    p.add_argument('-d', '--separator', default=' ', help='音节分隔符')
    p.add_argument('--mode', default='normal', choices=('normal', 'surname'),
                   help='转换模式（surname 启用姓氏读音）')
    p.add_argument('--sandhi', action='store_true',
                   help='启用口语变调（一/不变调、三声变调、轻声），默认输出规范本调')
    p.add_argument('--erhua', action='store_true', help='启用儿化音合并')
    p.add_argument('--stdin', action='store_true', help='从标准输入读取文本')

    # ---- slug ----
    p = sub.add_parser('slug', help='生成 URL 友好的拼音别名')
    p.add_argument('text', nargs='*')
    p.add_argument('-d', '--separator', default='-', help='连接符（默认 -）')
    p.add_argument('--tone', action='store_true', help='保留声调数字')
    p.add_argument('--stdin', action='store_true', help='从标准输入读取文本')

    # ---- initials ----
    p = sub.add_parser('initials', help='提取拼音首字母缩写')
    p.add_argument('text', nargs='*')
    p.add_argument('--full', action='store_true',
                   help='使用完整声母（zh/ch/sh）而非首字母')
    p.add_argument('--stdin', action='store_true', help='从标准输入读取文本')

    # ---- sort ----
    p = sub.add_parser('sort', help='按拼音对中文排序')
    p.add_argument('items', nargs='*')
    p.add_argument('--no-tone', action='store_true', help='排序时忽略声调')
    p.add_argument('--stdin', action='store_true', help='从标准输入按行读取')

    # ---- lookup ----
    p = sub.add_parser('lookup', help='查询单个汉字的多音字与释义')
    p.add_argument('char', help='单个汉字')
    p.add_argument('-s', '--style', default='mark', choices=STYLES,
                   help='输出风格（默认 mark）')

    # ---- info ----
    sub.add_parser('info', help='显示内置数据统计信息')
    return parser


def _read_text(args) -> str:
    """优先从 stdin 读取，否则拼接命令行参数。"""
    if getattr(args, 'stdin', False):
        return sys.stdin.read().rstrip('\n')
    parts = getattr(args, 'text', None) or []
    return ' '.join(parts)


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == 'pinyin':
        text = _read_text(args)
        if not text:
            parser.error('缺少待转换文本，请提供参数或使用 --stdin')
        print(convert(text, style=args.style, separator=args.separator,
                      mode=args.mode, sandhi=args.sandhi,
                      erhua=args.erhua))
    elif args.command == 'slug':
        text = _read_text(args)
        if not text:
            parser.error('缺少待转换文本，请提供参数或使用 --stdin')
        print(slug(text, separator=args.separator, tone=args.tone))
    elif args.command == 'initials':
        text = _read_text(args)
        if not text:
            parser.error('缺少待转换文本，请提供参数或使用 --stdin')
        print(initials(text, style='initial' if args.full else 'first'))
    elif args.command == 'sort':
        if getattr(args, 'stdin', False):
            items = [line for line in sys.stdin.read().splitlines() if line.strip()]
        else:
            items = args.items
        if not items:
            parser.error('缺少待排序内容')
        for item in sorted(items, key=lambda x: sort_key(x, tone=not args.no_tone)):
            print(item)
    elif args.command == 'lookup':
        char = args.char
        if len(char) != 1:
            parser.error('lookup 只接受单个汉字')
        info = explain(char)
        if info is None:
            print(f'未收录汉字: {char}')
            return 1
        print(f'汉字: {info["char"]}  码点: {info["code_point"]}')
        print(f'拼音: {" / ".join(info["pinyin"])}')
        print(f'数字: {" / ".join(info["pinyin_number"])}')
        print(f'注音: {" / ".join(info["zhuyin"])}')
        if info['meaning']:
            print(f'释义: {info["meaning"]}')
        print(f'多音字: {"是" if info["heteronym"] else "否"}')
        # 展示该字在词组规则中的实际读音
        from . import rules
        matched = [(ph, rd) for ph, rd in rules.PHRASE_RULES.items() if char in ph]
        if matched:
            from .style import render
            sample = []
            for ph, rd in matched[:8]:
                idx = ph.index(char)
                sample.append(f'{ph}={render(rd[idx], args.style)}')
            print(f'词组读音: {", ".join(sample)}')
    elif args.command == 'info':
        print(f'HanTone {__version__}')
        print(f'收录汉字: {hanzi_count()}')
        print(f'音节数量: {syllable_count()}')
        print(f'释义条目: {len(definitions())}')
        from . import rules
        print(f'词组规则: {len(rules.PHRASE_RULES)}')
        print(f'姓氏规则: {len(rules.SURNAME_RULES)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
