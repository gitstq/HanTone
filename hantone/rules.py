# -*- coding: utf-8 -*-
"""多音字消歧规则库（HanTone 自研）。

拼音数据只能给出「某个字有哪些读音」，无法决定「在这个词里读什么」。
本模块提供三层自研规则来消解多音字：

1. **词组规则**：高频多音字搭配的直接映射，最长匹配优先。
2. **姓氏规则**：姓氏专用读音（如「单」读 shàn、「仇」读 qiú）。
3. **语流音变**：轻声叠词、儿化，以及「一」「不」变调与三声变调。

规则以「数字调拼音」书写（如 ``yin2 hang2``），加载时解析为内部音节。
所有规则均为本项目整理，未使用第三方词典数据。
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple

from ._table import Syllable

# ---------------------------------------------------------------------------
# 1. 词组消歧规则：词组 -> 逐字读音（数字调）
# ---------------------------------------------------------------------------
_PHRASE_SOURCE: Dict[str, str] = {
    # —— 行 hang2 / xing2 ——
    '银行': 'yin2 hang2', '行业': 'hang2 ye4', '行情': 'hang2 qing2',
    '行列': 'hang2 lie4', '排行': 'pai2 hang2', '商行': 'shang1 hang2',
    '同行': 'tong2 hang2', '外行': 'wai4 hang2', '内行': 'nei4 hang2',
    '字里行间': 'zi4 li3 hang2 jian1', '行款': 'hang2 kuan3',
    '行走': 'xing2 zou3', '行动': 'xing2 dong4', '行人': 'xing2 ren2',
    '行为': 'xing2 wei2', '旅行': 'lv3 xing2', '举行': 'ju3 xing2',
    '执行': 'zhi2 xing2', '流行': 'liu2 xing2', '进行': 'jin4 xing2',
    '运行': 'yun4 xing2', '发行': 'fa1 xing2', '行驶': 'xing2 shi3',
    # —— 重 zhong4 / chong2 ——
    '重复': 'chong2 fu4', '重新': 'chong2 xin1', '重叠': 'chong2 die2',
    '重来': 'chong2 lai2', '双重': 'shuang1 chong2', '重阳': 'chong2 yang2',
    '重整': 'chong2 zheng3', '重建': 'chong2 jian4',
    '重要': 'zhong4 yao4', '重量': 'zhong4 liang4',
    '重视': 'zhong4 shi4', '严重': 'yan2 zhong4', '重点': 'zhong4 dian3',
    '沉重': 'chen2 zhong4', '重大': 'zhong4 da4', '重点': 'zhong4 dian3',
    '重心': 'zhong4 xin1', '重伤': 'zhong4 shang1',
    # —— 长 chang2 / zhang3 ——
    '长度': 'chang2 du4', '长久': 'chang2 jiu3', '长期': 'chang2 qi1',
    '长江': 'chang2 jiang1', '漫长': 'man4 chang2', '擅长': 'shan4 chang2',
    '长寿': 'chang2 shou4', '长途': 'chang2 tu2',
    '长大': 'zhang3 da4', '生长': 'sheng1 zhang3', '增长': 'zeng1 zhang3',
    '校长': 'xiao4 zhang3', '成长': 'cheng2 zhang3', '首长': 'shou3 zhang3',
    '长相': 'zhang3 xiang4', '年长': 'nian2 zhang3',
    # —— 乐 le4 / yue4 ——
    '音乐': 'yin1 yue4', '乐队': 'yue4 dui4', '乐器': 'yue4 qi4',
    '乐曲': 'yue4 qu3', '声乐': 'sheng1 yue4', '乐谱': 'yue4 pu3',
    '奏乐': 'zou4 yue4', '民乐': 'min2 yue4',
    '快乐': 'kuai4 le4', '欢乐': 'huan1 le4', '娱乐': 'yu2 le4',
    '乐园': 'le4 yuan2', '乐意': 'le4 yi4', '乐观': 'le4 guan1',
    # —— 的 / 了 / 为 / 得 / 地 / 着 ——
    '的确': 'di2 que4', '目的': 'mu4 di4', '有的放矢': 'you3 di4 fang3 shi3',
    '了解': 'liao3 jie3', '了不起': 'liao3 bu4 qi3', '不得了': 'bu4 de2 liao3',
    '为了': 'wei4 le5', '因为': 'yin1 wei4', '为什么': 'wei4 shen2 me5',
    '为何': 'wei4 he2', '为此': 'wei4 ci3',
    '作为': 'zuo4 wei2', '认为': 'ren4 wei2', '成为': 'cheng2 wei2',
    '行为': 'xing2 wei2', '以为': 'yi3 wei2',
    '得到': 'de2 dao4', '获得': 'huo4 de2', '得意': 'de2 yi4',
    '记得': 'ji4 de2', '值得': 'zhi2 de2',
    '地方': 'di4 fang1', '土地': 'tu3 di4', '地图': 'di4 tu2',
    '地址': 'di4 zhi3', '地面': 'di4 mian4', '地球': 'di4 qiu2',
    '着急': 'zhao2 ji2', '着火': 'zhao2 huo3', '睡着': 'shui4 zhao2',
    '着落': 'zhuo2 luo4', '着手': 'zhuo2 shou3', '沉着': 'chen2 zhuo2',
    # —— 只 / 要 / 好 / 觉 / 背 ——
    '只有': 'zhi3 you3', '只是': 'zhi3 shi4', '只要': 'zhi3 yao4',
    '只好': 'zhi3 hao3', '只能': 'zhi3 neng2',
    '一只': 'yi4 zhi1', '两只': 'liang3 zhi1', '只身': 'zhi1 shen1',
    '要求': 'yao1 qiu2', '要挟': 'yao1 xie2',
    '需要': 'xu1 yao4', '重要': 'zhong4 yao4', '要是': 'yao4 shi4',
    '爱好': 'ai4 hao4', '好奇': 'hao4 qi2', '喜好': 'xi3 hao4',
    '好吃': 'hao3 chi1', '好听': 'hao3 ting1', '好像': 'hao3 xiang4',
    '觉得': 'jue2 de5', '感觉': 'gan3 jue2', '自觉': 'zi4 jue2',
    '睡觉': 'shui4 jiao4', '午觉': 'wu3 jiao4',
    '背后': 'bei4 hou4', '背景': 'bei4 jing3', '背诵': 'bei4 song4',
    '背包': 'bei1 bao1', '背带': 'bei1 dai4',
    # —— 发 / 教 / 省 / 血 / 熟 / 给 ——
    '头发': 'tou2 fa4', '理发': 'li3 fa4', '白发': 'bai2 fa4',
    '发现': 'fa1 xian4', '发生': 'fa1 sheng1', '发展': 'fa1 zhan3',
    '出发': 'chu1 fa1', '发现': 'fa1 xian4',
    '教育': 'jiao4 yu4', '教师': 'jiao4 shi1', '教室': 'jiao4 shi4',
    '教学': 'jiao4 xue2', '教书': 'jiao1 shu1',
    '省份': 'sheng3 fen4', '节省': 'jie2 sheng3',
    '反省': 'fan3 xing3', '省悟': 'xing3 wu4',
    '血液': 'xue4 ye4', '心血': 'xin1 xue4', '血压': 'xue4 ya1',
    '流血': 'liu2 xue4', '血淋淋': 'xie3 lin1 lin1',
    '成熟': 'cheng2 shu2', '熟练': 'shu2 lian4', '熟悉': 'shu2 xi1',
    '供给': 'gong1 ji3', '给予': 'ji3 yu3', '自给': 'zi4 ji3',
    # —— 剥 / 露 / 薄 / 差 / 还 / 少 / 都 / 会 ——
    '剥削': 'bo1 xue1', '剥夺': 'bo1 duo2', '剥皮': 'bao1 pi2',
    '暴露': 'bao4 lu4', '揭露': 'jie1 lu4', '露水': 'lu4 shui3',
    '露馅': 'lou4 xian4', '露脸': 'lou4 lian3',
    '薄弱': 'bo2 ruo4', '单薄': 'dan1 bo2', '刻薄': 'ke4 bo2',
    '薄饼': 'bao2 bing3',
    '差别': 'cha1 bie2', '差距': 'cha1 ju4', '差错': 'cha1 cuo4',
    '差不多': 'cha4 bu4 duo1', '很差': 'hen3 cha4',
    '出差': 'chu1 chai1', '差事': 'chai1 shi4', '参差': 'cen1 ci1',
    '归还': 'gui1 huan2', '还钱': 'huan2 qian2', '偿还': 'chang2 huan2',
    '还有': 'hai2 you3', '还是': 'hai2 shi4', '还能': 'hai2 neng2',
    '少年': 'shao4 nian2', '少女': 'shao4 nv3', '少爷': 'shao4 ye2',
    '多少': 'duo1 shao3', '减少': 'jian3 shao3', '少数': 'shao3 shu4',
    '首都': 'shou3 du1', '都市': 'du1 shi4',
    '会计': 'kuai4 ji4', '财会': 'cai2 kuai4',
    '会议': 'hui4 yi4', '学会': 'xue2 hui4', '机会': 'ji1 hui4',
    # —— 参 / 中 / 空 / 间 / 干 / 脏 ——
    '参加': 'can1 jia1', '参与': 'can1 yu4', '人参': 'ren2 shen1',
    '中奖': 'zhong4 jiang3', '看中': 'kan4 zhong4', '中毒': 'zhong4 du2',
    '中国': 'zhong1 guo2', '中间': 'zhong1 jian1', '其中': 'qi2 zhong1',
    '空气': 'kong1 qi4', '天空': 'tian1 kong1', '空间': 'kong1 jian1',
    '空闲': 'kong4 xian2', '空白': 'kong4 bai2', '有空': 'you3 kong4',
    '时间': 'shi2 jian1', '房间': 'fang2 jian1', '间隔': 'jian4 ge2',
    '间接': 'jian4 jie1',
    '干净': 'gan1 jing4', '若干': 'ruo4 gan1', '饼干': 'bing3 gan1',
    '干活': 'gan4 huo2', '干部': 'gan4 bu4', '才干': 'cai2 gan4',
    '心脏': 'xin1 zang4', '内脏': 'nei4 zang4', '肝脏': 'gan1 zang4',
    '肮脏': 'ang1 zang1',
    # —— 便 / 应 / 兴 / 冠 / 处 / 调 ——
    '方便': 'fang1 bian4', '便利': 'bian4 li4', '便宜': 'pian2 yi5',
    '应该': 'ying1 gai1', '应当': 'ying1 dang1',
    '应用': 'ying4 yong4', '答应': 'da1 ying5', '反应': 'fan3 ying4',
    '兴奋': 'xing1 fen4', '兴起': 'xing1 qi3', '高兴': 'gao1 xing4',
    '兴趣': 'xing4 qu4', '兴致': 'xing4 zhi4',
    '冠军': 'guan4 jun1', '夺冠': 'duo2 guan4', '鸡冠': 'ji1 guan1',
    '处理': 'chu3 li3', '相处': 'xiang1 chu3', '处方': 'chu3 fang1',
    '到处': 'dao4 chu4', '好处': 'hao3 chu4', '住处': 'zhu4 chu4',
    '调动': 'diao4 dong4', '调查': 'diao4 cha2', '声调': 'sheng1 diao4',
    '调节': 'tiao2 jie2', '调整': 'tiao2 zheng3', '空调': 'kong1 tiao2',
    # —— 尽 / 假 / 强 / 称 / 撒 / 散 / 似 / 系 / 降 ——
    '尽管': 'jin3 guan3', '尽量': 'jin3 liang4',
    '尽力': 'jin4 li4', '用尽': 'yong4 jin4', '尽头': 'jin4 tou2',
    '放假': 'fang4 jia4', '假期': 'jia4 qi1', '请假': 'qing3 jia4',
    '假设': 'jia3 she4', '真假': 'zhen1 jia3',
    '强大': 'qiang2 da4', '坚强': 'jian1 qiang2', '强调': 'qiang2 diao4',
    '勉强': 'mian3 qiang3', '强迫': 'qiang3 po4', '倔强': 'jue2 jiang4',
    '称呼': 'cheng1 hu5', '名称': 'ming2 cheng1', '简称': 'jian3 cheng1',
    '称心': 'chen4 xin1', '对称': 'dui4 chen4', '匀称': 'yun2 chen4',
    '撒谎': 'sa1 huang3', '撒种': 'sa3 zhong3',
    '分散': 'fen1 san4', '解散': 'jie3 san4', '散步': 'san4 bu4',
    '散文': 'san3 wen2', '松散': 'song1 san3',
    '似乎': 'si4 hu1', '相似': 'xiang1 si4', '类似': 'lei4 si4',
    '似的': 'shi4 de5',
    '关系': 'guan1 xi4', '系统': 'xi4 tong3', '联系': 'lian2 xi4',
    '系鞋带': 'ji4 xie2 dai4',
    '下降': 'xia4 jiang4', '降落': 'jiang4 luo4', '降低': 'jiang4 di1',
    '投降': 'tou2 xiang2',
    # —— 其它高频 ——
    '便宜': 'pian2 yi5', '便宜行事': 'bian4 yi2 xing2 shi4',
    '和平': 'he2 ping2', '暖和': 'nuan3 huo5', '和面': 'huo2 mian4',
    '和睦': 'he2 mu4', '和解': 'he2 jie3', '和诗': 'he4 shi1',
    '睡觉': 'shui4 jiao4', '午觉': 'wu3 jiao4',
    '朝阳': 'chao2 yang2', '朝霞': 'zhao1 xia2', '朝向': 'chao2 xiang4',
    '朝廷': 'chao2 ting2', '今朝': 'jin1 zhao1',
    '倒车': 'dao4 che1', '倒闭': 'dao3 bi4', '打倒': 'da3 dao3',
    '倒数': 'dao4 shu4',
    '唱片': 'chang4 pian4', '唱片儿': 'chang4 pian4 er5',
    '舒展': 'shu1 zhan3',     '舒服': 'shu1 fu5',
    # —— 地名专用读音（多音字高发场景） ——
    '重庆': 'chong2 qing4', '长春': 'chang2 chun1', '长沙': 'chang2 sha1',
    '大连': 'da4 lian2', '厦门': 'xia4 men2', '蚌埠': 'beng4 bu4',
    '六安': 'lu4 an1', '台州': 'tai1 zhou1', '丽水': 'li2 shui3',
    '亳州': 'bo2 zhou1', '涪陵': 'fu2 ling2', '铅山': 'yan2 shan1',
    '蔚县': 'yu4 xian4', '泌阳': 'bi4 yang2', '单县': 'shan4 xian4',
    '乐清': 'yue4 qing1', '华容': 'hua4 rong2', '隰县': 'xi2 xian4',
    '西藏': 'xi1 zang4', '拉萨': 'la1 sa4', '呼和浩特': 'hu1 he2 hao2 te4',
    '乌鲁木齐': 'wu1 lu3 mu4 qi2', '哈尔滨': 'ha1 er3 bin1',
    '厦门大学': 'xia4 men2 da4 xue2', '燕山': 'yan1 shan1',
    # —— 其它高频多音词 ——
    '曾经': 'ceng2 jing1', '曾祖': 'zeng1 zu3',
    '宿舍': 'su4 she4', '星宿': 'xing1 xiu4', '一宿': 'yi1 xiu3',
    '畜牧': 'xu4 mu4', '牲畜': 'sheng1 chu4',
    '屏风': 'ping2 feng1', '屏障': 'ping2 zhang4', '屏息': 'bing3 xi1',
    '刊载': 'kan1 zai3', '载重': 'zai4 zhong4', '下载': 'xia4 zai4',
    '攒钱': 'zan3 qian2', '攒聚': 'cuan2 ju4',
    '折腾': 'zhe1 teng5', '折本': 'she2 ben3', '折断': 'zhe2 duan4',
    '吓唬': 'xia4 hu5', '恐吓': 'kong3 he4', '大厦': 'da4 sha4',
    '任丘': 'ren2 qiu1', '华山': 'hua4 shan1', '姓氏': 'xing4 shi4',
    '几乎': 'ji1 hu1', '几个': 'ji3 ge4', '几何': 'ji3 he2',
    '茶几': 'cha2 ji1',
    '冠军': 'guan4 jun1', '冠状': 'guan1 zhuang4',
    '宁可': 'ning4 ke3', '安宁': 'an1 ning2', '宁静': 'ning2 jing4',
    '多少': 'duo1 shao3', '多么': 'duo1 me5',
    '朝鲜': 'chao2 xian3', '新鲜': 'xin1 xian1', '鲜有': 'xian3 you3',
    '鲜明': 'xian1 ming2',
    '大夫': 'dai4 fu5', '大小': 'da4 xiao3', '大王': 'da4 wang2',
    '石头': 'shi2 tou5', '木头': 'mu4 tou5', '念头': 'nian4 tou5',
    '桌子': 'zhuo1 zi5', '椅子': 'yi3 zi5', '孩子': 'hai2 zi5',
    '房子': 'fang2 zi5', '日子': 'ri4 zi5', '杯子': 'bei1 zi5',
    '时候': 'shi2 hou5', '时候儿': 'shi2 hou5',
    '明白': 'ming2 bai5', '朋友': 'peng2 you5', '东西': 'dong1 xi5',
    '衣服': 'yi1 fu5', '认识': 'ren4 shi5', '消息': 'xiao1 xi5',
    '客气': 'ke4 qi5', '厉害': 'li4 hai5', '月亮': 'yue4 liang5',
    '太阳': 'tai4 yang5', '耳朵': 'er3 duo5', '眼睛': 'yan3 jing5',
    '喜欢': 'xi3 huan5', '知道': 'zhi1 dao5', '意思': 'yi4 si5',
    '任务': 'ren4 wu5', '关系': 'guan1 xi5',
}

# ---------------------------------------------------------------------------
# 2. 姓氏专用读音
# ---------------------------------------------------------------------------
_SURNAME_SOURCE: Dict[str, str] = {
    '单': 'shan4', '仇': 'qiu2', '查': 'zha1', '曾': 'zeng1',
    '解': 'xie4', '华': 'hua4', '任': 'ren2', '朴': 'piao2',
    '覃': 'qin2', '区': 'ou1', '缪': 'miao4', '种': 'chong2',
    '折': 'she2', '乐': 'yue4', '翟': 'zhai2', '祭': 'zhai4',
    '蔚': 'yu4', '尉': 'yu4', '燕': 'yan1', '盖': 'ge3',
    '员': 'yun4', '祭': 'zhai4', '郄': 'qie4', '郇': 'xun2',
    '隗': 'kui2', '句': 'gou1', '苟': 'gou3', '过': 'guo1',
    '纪': 'ji3', '俱': 'ju1', '贾': 'jia3', '相': 'xiang4',
    '召': 'shao4', '过': 'guo1', '蒙': 'meng3', '万': 'wan4',
    '佟': 'tong2', '冼': 'xian3', '郗': 'xi1', '郜': 'gao4',
    # 复姓
    '尉迟': 'yu4 chi2', '长孙': 'zhang3 sun1', '万俟': 'mo4 qi2',
    '澹台': 'tan2 tai2', '单于': 'chan2 yu2', '夏侯': 'xia4 hou2',
    '诸葛': 'zhu1 ge3', '公孙': 'gong1 sun1', '轩辕': 'xuan1 yuan2',
    '端木': 'duan1 mu4', '令狐': 'ling2 hu2', '皇甫': 'huang2 fu3',
    '上官': 'shang4 guan1', '司马': 'si1 ma3', '欧阳': 'ou1 yang2',
    '东方': 'dong1 fang1', '南宫': 'nan2 gong1', '第五': 'di4 wu3',
    '呼延': 'hu1 yan2', '慕容': 'mu4 rong2', '司徒': 'si1 tu2',
}

# ---------------------------------------------------------------------------
# 3. 语流音变规则
# ---------------------------------------------------------------------------
# 语法轻声词：在词尾或句中作助词时读轻声
_NEUTRAL_WORDS = frozenset(
    '的了着得地们子头吗呢吧啊么嘛啦呀哦呗咯喽哇哪'
)
# 叠词（亲属称呼 / 动词重叠）第二个音节读轻声
_REDUP_PARTS = frozenset('爸妈哥姐弟妹爷爷奶奶公婆叔姑舅侄孙娃星')

# 「一」的变调：后接音节声调 -> 实际声调
_YI_TONE_SHIFT: Dict[int, int] = {1: 4, 2: 4, 3: 4, 4: 2, 5: 5}
# 「不」的变调：仅四声前变二声
_BU_TONE_SHIFT: Dict[int, int] = {4: 2}

_NEUTRAL_TONE = 5
_SYLLABLE_RE = re.compile(r'^([a-z]+)([1-5])$')


def _parse_sequence(text: str) -> Tuple[Syllable, ...]:
    """把 ``'yin2 hang2'`` 解析为内部音节元组。"""
    result: List[Syllable] = []
    for token in text.split():
        m = _SYLLABLE_RE.match(token)
        if not m:
            raise ValueError(f'非法音节写法: {token!r}')
        result.append((m.group(1).replace('u', 'u'), int(m.group(2))))
    return tuple(result)


def _build_phrase_rules() -> Dict[str, Tuple[Syllable, ...]]:
    rules: Dict[str, Tuple[Syllable, ...]] = {}
    for phrase, reading in _PHRASE_SOURCE.items():
        parsed = _parse_sequence(reading)
        if len(parsed) != len(phrase):
            # 规则书写错误时跳过，避免运行时错位
            continue
        rules[phrase] = parsed
    return rules


def _build_surname_rules() -> Dict[str, Tuple[Syllable, ...]]:
    return {name: _parse_sequence(reading)
            for name, reading in _SURNAME_SOURCE.items()}


PHRASE_RULES: Dict[str, Tuple[Syllable, ...]] = _build_phrase_rules()
SURNAME_RULES: Dict[str, Tuple[Syllable, ...]] = _build_surname_rules()

# 最大词组长度，用于最大正向匹配时的窗口上限
MAX_PHRASE_LEN = max(len(p) for p in PHRASE_RULES)


def apply_tone_sandhi(syllables: List[Syllable],
                      protected: Optional[set] = None) -> List[Syllable]:
    """应用语流音变： 「一」「不」变调 + 三声变调。

    规则（依据《现代汉语》普通话音变规范）：

    * 「一」单念或收尾读一声；在四声前读二声；在一二三声前读四声。
    * 「不」在四声前读二声，其余读四声。
    * 两个三声相连时，前一个变读二声。

    :param protected: 需要保持不变的下标集合。词组规则已经明确给出
        读音时，不应再被自动音变改写（否则「快乐」会被读成 kuài le）。
    """
    protected = protected or set()
    result = list(syllables)
    n = len(result)
    for i, (base, tone) in enumerate(result):
        if i in protected:
            continue
        if base == 'yi':
            if n == 1 or i == n - 1:
                result[i] = ('yi', 1)
            else:
                result[i] = ('yi', _YI_TONE_SHIFT.get(result[i + 1][1], 1))
        elif base == 'bu':
            if i + 1 < n and result[i + 1][1] in _BU_TONE_SHIFT:
                result[i] = ('bu', _BU_TONE_SHIFT[result[i + 1][1]])
            else:
                result[i] = ('bu', 4)
    # 三声变调：连续两个三声且均未被词组规则锁定，前者变二声
    for i in range(n - 1):
        if i in protected or (i + 1) in protected:
            continue
        if result[i][1] == 3 and result[i + 1][1] == 3:
            result[i] = (result[i][0], 2)
    return result


def apply_neutral(syllables: List[Syllable],
                  protected: Optional[set] = None) -> List[Syllable]:
    """把句尾常见语法助词归为轻声（5），并识别亲属叠词。

    :param protected: 需要保持不变的下标集合，用于保护词组规则读音。
    """
    protected = protected or set()
    result = list(syllables)
    n = len(result)
    for i, (base, tone) in enumerate(result):
        if i in protected:
            continue
        if i == n - 1 and base in (
            'de', 'le', 'zhe', 'men', 'zi', 'ma', 'ne',
            'ba', 'me', 'a', 'ya', 'la', 'bei', 'lou',
        ) and tone != 5:
            result[i] = (base, _NEUTRAL_TONE)
        # 亲属叠词：妈妈、爸爸、哥哥……
        if i > 0 and base == result[i - 1][0] and base in _REDUP_PARTS:
            result[i] = (base, _NEUTRAL_TONE)
    return result
