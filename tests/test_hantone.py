# -*- coding: utf-8 -*-
"""HanTone 单元测试。

仅依赖标准库 unittest，可直接运行::

    python -m unittest discover -s tests
    # 或
    python tests/test_hantone.py
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hantone
from hantone import core, rules, style
from hantone._table import hanzi_count, lookup, syllable_count


class TestData(unittest.TestCase):
    """内置数据表的完整性校验。"""

    def test_scale(self):
        self.assertGreater(hanzi_count(), 40000)
        self.assertGreater(syllable_count(), 1000)

    def test_common_chars(self):
        for char in '中华人民共和国':
            self.assertIsNotNone(lookup(char), f'未收录常用字: {char}')

    def test_syllable_shape(self):
        for base, tone in [(b, t) for b, t in
                           [(s[0], s[1]) for s in
                            [lookup(c)[0] for c in '中国人民']]]:
            self.assertTrue(base.isalpha())
            self.assertIn(tone, (1, 2, 3, 4, 5))


class TestStyle(unittest.TestCase):
    """标调规则与风格渲染。"""

    def test_tone_mark_rules(self):
        # a 优先
        self.assertEqual(style.apply_tone_mark('hao', 3), 'hǎo')
        self.assertEqual(style.apply_tone_mark('hua', 2), 'huá')
        # 无 a 找 o/e
        self.assertEqual(style.apply_tone_mark('hou', 3), 'hǒu')
        self.assertEqual(style.apply_tone_mark('hei', 1), 'hēi')
        # i/u 并列标在后
        self.assertEqual(style.apply_tone_mark('liu', 2), 'liú')
        self.assertEqual(style.apply_tone_mark('gui', 1), 'guī')
        # ü
        self.assertEqual(style.apply_tone_mark('lv', 4), 'lǜ')
        self.assertEqual(style.apply_tone_mark('nv', 3), 'nǚ')

    def test_styles(self):
        self.assertEqual(style.render(('zhong', 1), 'mark'), 'zhōng')
        self.assertEqual(style.render(('zhong', 1), 'number'), 'zhong1')
        self.assertEqual(style.render(('zhong', 1), 'plain'), 'zhong')
        self.assertEqual(style.render(('zhong', 1), 'initial'), 'zh')
        self.assertEqual(style.render(('zhong', 1), 'first'), 'z')

    def test_zhuyin(self):
        self.assertEqual(style.to_zhuyin('zhong', 1), 'ㄓㄨㄥ')
        self.assertEqual(style.to_zhuyin('hao', 3), 'ㄏㄠˇ')
        self.assertEqual(style.to_zhuyin('ma', 1), 'ㄇㄚ')

    def test_unknown_style_fallback(self):
        self.assertEqual(style.render(('zhong', 1), 'nope'), 'zhōng')


class TestDisambiguation(unittest.TestCase):
    """多音字词组级消歧。"""

    CASES = {
        '银行': 'yín háng',
        '行走': 'xíng zǒu',
        '重庆': 'chóng qìng',
        '重要': 'zhòng yào',
        '重复': 'chóng fù',
        '音乐': 'yīn yuè',
        '快乐': 'kuài lè',
        '厦门': 'xià mén',
        '六安': 'lù ān',
        '曾经': 'céng jīng',
        '下载': 'xià zài',
        '宿舍': 'sù shè',
        '恐吓': 'kǒng hè',
        '华山': 'huà shān',
        '目的': 'mù dì',
        '的确': 'dí què',
        '因为': 'yīn wèi',
        '作为': 'zuò wéi',
        '睡觉': 'shuì jiào',
        '觉得': 'jué de',
        '头发': 'tóu fà',
        '发现': 'fā xiàn',
        '教书': 'jiāo shū',
        '教育': 'jiào yù',
        '反省': 'fǎn xǐng',
        '血液': 'xuè yè',
        '供给': 'gōng jǐ',
        '剥削': 'bō xuē',
        '差别': 'chā bié',
        '出差': 'chū chāi',
        '归还': 'guī huán',
        '少年': 'shào nián',
        '首都': 'shǒu dū',
        '会计': 'kuài jì',
        '人参': 'rén shēn',
        '空闲': 'kòng xián',
        '干净': 'gān jìng',
        '干活': 'gàn huó',
        '心脏': 'xīn zàng',
        '答应': 'dā ying',
        '兴奋': 'xīng fèn',
        '高兴': 'gāo xìng',
        '冠军': 'guàn jūn',
        '处理': 'chǔ lǐ',
        '到处': 'dào chù',
        '空调': 'kōng tiáo',
        '尽管': 'jǐn guǎn',
        '放假': 'fàng jià',
        '勉强': 'miǎn qiǎng',
        '对称': 'duì chèn',
        '似乎': 'sì hū',
        '下降': 'xià jiàng',
        '投降': 'tóu xiáng',
    }

    def test_phrase_cases(self):
        for text, expected in self.CASES.items():
            with self.subTest(text=text):
                self.assertEqual(hantone.convert(text), expected)

    def test_longest_match(self):
        # 「银行」优先于单字默认读音 xíng
        self.assertEqual(hantone.convert('去银行'), 'qù yín háng')


class TestSandhi(unittest.TestCase):
    """语流音变（三声变调、一不变调、轻声）。"""

    def test_default_is_citation_tone(self):
        self.assertEqual(hantone.convert('你好'), 'nǐ hǎo')
        self.assertEqual(hantone.convert('一个'), 'yī gè')

    def test_third_tone_sandhi(self):
        self.assertEqual(hantone.convert('你好', sandhi=True), 'ní hǎo')
        self.assertEqual(hantone.convert('很好', sandhi=True), 'hén hǎo')

    def test_yi_bu_sandhi(self):
        self.assertEqual(hantone.convert('一个', sandhi=True), 'yí gè')
        self.assertEqual(hantone.convert('一天', sandhi=True), 'yì tiān')
        self.assertEqual(hantone.convert('不是', sandhi=True), 'bú shì')
        self.assertEqual(hantone.convert('不好', sandhi=True), 'bù hǎo')

    def test_neutral_redup(self):
        self.assertEqual(hantone.convert('妈妈', sandhi=True), 'mā ma')

    def test_phrase_rules_are_protected(self):
        # 词组规则已指定读音，不应被轻声规则改写
        self.assertEqual(hantone.convert('快乐', sandhi=True), 'kuài lè')
        self.assertEqual(hantone.convert('厦门', sandhi=True), 'xià mén')


class TestSurname(unittest.TestCase):
    """姓氏专用读音。"""

    def test_surname_mode(self):
        cases = {
            '单': 'shàn', '仇': 'qiú', '查': 'zhā',
            '曾': 'zēng', '解': 'xiè',
        }
        for char, expected in cases.items():
            with self.subTest(char=char):
                self.assertEqual(hantone.convert(char, mode='surname'), expected)

    def test_compound_surname(self):
        self.assertEqual(hantone.convert('尉迟', mode='surname'), 'yù chí')
        self.assertEqual(hantone.convert('万俟', mode='surname'), 'mò qí')

    def test_normal_mode_unchanged(self):
        self.assertEqual(hantone.convert('单'), 'dān')


class TestUtilities(unittest.TestCase):
    """slug / initials / sort_key / heteronym / explain。"""

    def test_slug(self):
        self.assertEqual(hantone.slug('汉语拼音'), 'han-yu-pin-yin')
        self.assertEqual(hantone.slug('汉语拼音', separator='_'), 'han_yu_pin_yin')

    def test_initials(self):
        self.assertEqual(hantone.initials('中国银行'), 'zgyh')
        self.assertEqual(hantone.initials('中国银行', style='initial'), 'zhgyh')

    def test_sort_key(self):
        names = ['张三', '李四', '王五', '赵六']
        self.assertEqual(sorted(names, key=hantone.sort_key),
                         ['李四', '王五', '张三', '赵六'])

    def test_heteronym(self):
        readings = hantone.heteronym('行')
        self.assertEqual(readings, [['xíng', 'háng', 'héng']])

    def test_explain(self):
        info = hantone.explain('中')
        self.assertEqual(info['char'], '中')
        self.assertIn('zhōng', info['pinyin'])
        self.assertIn('ㄓㄨㄥ', info['zhuyin'])
        self.assertTrue(info['heteronym'])

    def test_explain_unknown(self):
        # U+FFFF 为非字符，Unihan 不会收录
        self.assertIsNone(hantone.explain('\uFFFF'))


class TestEdgeCases(unittest.TestCase):
    """边界与异常处理。"""

    def test_empty(self):
        self.assertEqual(hantone.convert(''), '')
        self.assertEqual(hantone.lazy_pinyin(''), [])

    def test_non_chinese(self):
        self.assertEqual(hantone.convert('Hello'), 'Hello')
        self.assertEqual(hantone.convert('abc 123'), 'abc 123')

    def test_mixed(self):
        self.assertEqual(hantone.convert('中国ABC'), 'zhōng guó ABC')

    def test_punctuation_kept(self):
        out = hantone.convert('你好，世界！')
        self.assertIn('，', out)
        self.assertIn('！', out)

    def test_unknown_style(self):
        with self.assertRaises(ValueError):
            hantone.lazy_pinyin('中文', style='bad-style')

    def test_unknown_error_mode(self):
        with self.assertRaises(ValueError):
            hantone.lazy_pinyin('中文', errors='bad-mode')

    def test_ignore_errors(self):
        # 全部为非汉字时应被忽略
        self.assertEqual(hantone.lazy_pinyin('abc', errors='ignore'), [])

    def test_rules_integrity(self):
        # 词组规则的长度必须与读音个数一致
        for phrase, readings in rules.PHRASE_RULES.items():
            with self.subTest(phrase=phrase):
                self.assertEqual(len(phrase), len(readings))


class TestCLI(unittest.TestCase):
    """命令行可用性。"""

    def test_pinyin_command(self):
        from hantone.cli import main
        self.assertEqual(main(['pinyin', '中国银行']), 0)

    def test_info_command(self):
        from hantone.cli import main
        self.assertEqual(main(['info']), 0)

    def test_no_command_prints_help(self):
        from hantone.cli import main
        self.assertEqual(main([]), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
