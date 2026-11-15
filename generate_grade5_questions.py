#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人教版（2026 秋新修订教材）五年级上册 语文 / 数学 / 英语 4000 题生成器。
输出符合「题了个题」question-format.md v2，可直接导入或 POST /api/questions。

教材依据（2026-11-15 核对）：
  语文：统编版五上 2026 秋版，8 单元（含第七单元《早春呈水部张十八员外》）
  数学：人教版五上 2026 秋版，观察简单组合体 / 小数乘法 / 小数除法 / 图形的运动 /
        用字母表示数和数量关系 / 多边形的面积 / 有趣的密铺 / 可能性 / 复习与关联
        （已删除：位置数对、简易方程解方程、循环小数等机械计算）
  英语：人教 PEP(2024) 五上，Unit 1 Different friends / 2 My feelings / 3 Work and play /
        4 Healthy habits / 5 Food we eat / 6 Nature and us
"""
import itertools
import json
import os
import random
from decimal import Decimal, ROUND_HALF_UP

R = random.Random(20261115)
TARGET = {"数学": 1400, "语文": 1300, "英语": 1300}
LEVEL = "五年级"
GROUPS = {"数学": [], "语文": [], "英语": []}

# ---------------------------------------------------------------- 基础工具

def fmt(x):
    if isinstance(x, str):
        return x
    return format(Decimal(str(x)).normalize(), "f")


def diff():
    return R.choices([1, 2, 3, 4, 5], [0.27, 0.37, 0.29, 0.06, 0.01])[0]


def opts(correct, distractors):
    c = fmt(correct)
    vals = [c]
    for d in distractors:
        s = fmt(d)
        if s != c and s not in vals:
            vals.append(s)
    if len(vals) < 3:
        return None
    vals = vals[:4]
    R.shuffle(vals)
    return vals, vals.index(c)


def S(q, correct, distractors, tip, d=None):
    o = opts(correct, distractors)
    if not o:
        return None
    a, k = o
    return {"type": "single", "q": q, "a": a, "k": k,
            "difficulty": d or diff(), "tip": tip}


def B(q, truth, tip, d=None):
    return {"type": "boolean", "q": q, "a": ["正确", "错误"],
            "k": 0 if truth else 1, "difficulty": d or diff(), "tip": tip}


def M(q, a, idx, tip, d=None):
    if len(idx) < 2 or len(a) > 8:
        return None
    return {"type": "multiple", "q": q, "a": a,
            "correctIndices": sorted(idx), "difficulty": d or diff(), "tip": tip}


def T(q, answers, tip, d=None):
    return {"type": "text", "q": q,
            "answers": list(dict.fromkeys(fmt(x) for x in answers)),
            "difficulty": d or diff(), "tip": tip}


def J(q, model, rubric, tip, d=None):
    return {"type": "subjective", "q": q, "modelAnswer": model,
            "rubric": rubric, "difficulty": d or diff(), "tip": tip}


def group(subj, bank, items):
    GROUPS[subj].append((bank, [x for x in items if x]))


# ================================================================ 数学

def gen_math():
    # 一 观察简单组合体
    t = []
    view = ["从前面看", "从上面看", "从左面看"]
    concepts = [
        ("从同一方向观察不同的组合体，看到的图形可能相同，也可能不同。", True, "不同摆法可能得到相同的视图，也可能不同。"),
        ("从不同方向观察同一个组合体，看到的图形一定完全相同。", False, "方向不同，看到的图形往往不同。"),
        ("观察组合体时，只能从前面和上面两个方向观察。", False, "通常从前面、上面、左面三个方向观察。"),
        ("用同样的小正方体摆组合体，小正方体个数相同，摆法一定只有一种。", False, "个数相同可以有多种摆法。"),
        ("从上面看两个不同的组合体，看到的图形相同，说明它们用的小正方体个数一定相同。", False, "俯视图相同，各位置叠放的个数也可能不同。"),
        ("根据从三个方向看到的图形，一般可以还原出唯一的组合体。", True, "三视图能帮助确定每个位置的高度。"),
        ("组合体中的每一个小正方体至少要有一个面与其他小正方体重合。", True, "这是课本摆组合体的要求。"),
        ("从前面看到的图形，能反映组合体每一列最高的层数。", True, "正视图显示每列的最大高度。"),
    ]
    for q, truth, tip in concepts:
        t.append(B(q, truth, tip))
    for n in range(2, 10):
        for pos in view:
            t.append(S("用 %d 个同样的小正方体排成一排摆成组合体，%s是什么形状？" % (n, pos),
                       "%d 个正方形排成一行" % n if pos != "从左面看" else "1 个正方形",
                       ["%d 个正方形排成一列" % n, "1 个正方形", "%d 个正方形排成两行" % n],
                       "排成一排时，从前面和上面看是一行 n 个，从左面看只有 1 个正方形。"))
    for n in range(2, 9):
        t.append(T("用 %d 个同样的小正方体摆成一摞（竖直叠放），从上面看是几个正方形？" % n,
                   [str(1), "一", "1 个"], "竖直叠放时俯视图只有 1 个正方形，与个数无关。"))
    group("数学", "五上数学·一 观察简单组合体", t)

    # 二 小数乘法
    t = []
    for i in range(11, 96, 2):
        for j in range(3, 10):
            a, b = Decimal(i) / 10, Decimal(j)
            c = a * b
            t.append(S("计算 %s × %d = ?" % (fmt(a), j), c,
                       [c + Decimal("1"), c + Decimal("0.5"), c * Decimal("10"), c + Decimal("2")],
                       "先按 %s × %d 算成整数，再按因数的小数位数点小数点。" % (fmt(a * 10), j)))
    for i in range(11, 90, 3):
        for j in range(11, 90, 7):
            a, b = Decimal(i) / 10, Decimal(j) / 10
            c = a * b
            t.append(S("计算 %s × %s = ?" % (fmt(a), fmt(b)), c,
                       [c + Decimal("0.1"), c * Decimal("10"), c / Decimal("10"), c + Decimal("0.01")],
                       "两个因数共 %d 位小数，积应有相应小数位数，结果是 %s。" % (2, fmt(c))))
    laws = [("a × b = b × a", "乘法交换律"), ("(a × b) × c = a × (b × c)", "乘法结合律"),
            ("(a + b) × c = a × c + b × c", "乘法分配律")]
    for expr, name in laws:
        t.append(S("用字母表示「%s」，下面哪个式子正确？" % name, expr,
                   ["a + b = b + a", "a × (b + c) = a × b + c", "(a + b) + c = a + (b + c)"],
                   "%s：%s。" % (name, expr)))
        t.append(B("整数乘法的运算定律，对小数乘法同样适用。", True,
                   "整数乘法运算定律可以推广到小数。"))
    for a in [Decimal("0.25"), Decimal("1.25"), Decimal("2.5"), Decimal("0.5"), Decimal("0.8")]:
        for b in [4, 8, 2, 10, 20]:
            c = a * b
            t.append(T("简便计算：%s × %d = ?" % (fmt(a), b), [fmt(c)],
                       "%s × %d 可以凑整，得 %s。" % (fmt(a), b, fmt(c))))
            t.append(B("%s × %d = %s。" % (fmt(a), b, fmt(c)), True, "直接计算即可验证。"))
    for n in range(1, 40):
        p = Decimal(n) / 10
        t.append(B("一个数（0 除外）乘 %s，积比原数小。" % fmt(p), p < 1,
                   "乘小于 1 的数积变小；乘大于 1 的数积变大。"))
    group("数学", "五上数学·二 小数乘法", t)

    # 三 小数除法
    t = []
    for a in range(12, 200, 3):
        for b in [2, 3, 4, 5, 6]:
            x = Decimal(a) / 10
            c = x / b
            if c * b != x:          # 跳过除不尽、答案为无限小数的组合
                continue
            t.append(S("计算 %s ÷ %d = ?" % (fmt(x), b), c,
                       [c + Decimal("0.1"), c * b, c + Decimal("0.5"), c * Decimal("10")],
                       "按整数除法算，商的小数点要和被除数对齐。"))
    bs = [Decimal("0.2"), Decimal("0.4"), Decimal("0.5"), Decimal("0.8"),
          Decimal("1.2"), Decimal("1.5"), Decimal("2.5"), Decimal("0.3"), Decimal("0.6")]
    for b in bs:
        for q0 in range(2, 25):
            a = b * q0
            t.append(S("计算 %s ÷ %s = ?" % (fmt(a), fmt(b)), q0,
                       [q0 + 1, q0 - 1, q0 * 2, q0 + 2],
                       "把除数 %s 扩大成整数，被除数也扩大相同倍数，商不变。" % fmt(b)))
            t.append(T("%s ÷ %s = ?" % (fmt(a), fmt(b)), [str(q0)],
                       "商不变的性质：被除数和除数同时扩大相同倍数。"))
    for b in [Decimal("0.5"), Decimal("0.2"), Decimal("0.25"), Decimal("0.1")]:
        t.append(B("一个数（0 除外）除以 %s，等于这个数乘 %s。" % (fmt(b), fmt(Decimal(1) / b)), True,
                   "除以一个数等于乘它的倒数，如除以 0.5 就是乘 2。"))
    group("数学", "五上数学·三 小数除法", t)

    # 四 图形的运动
    t = []
    sym = [("正方形", 4), ("长方形", 2), ("等边三角形", 3), ("等腰三角形", 1),
           ("圆", "无数"), ("平行四边形", 0), ("正六边形", 6)]
    for name, n in sym:
        t.append(S("%s有几条对称轴？" % name, "%s条" % n,
                   ["%s条" % (n + 1 if isinstance(n, int) else 1), "%s条" % (n + 2 if isinstance(n, int) else 2),
                    "%s条" % (max(0, n - 1) if isinstance(n, int) else 3)],
                   "%s的对称轴：%s条。" % (name, n)))
        t.append(B("%s是轴对称图形。" % name, n != 0,
                   "沿某条直线对折后两边能完全重合才是轴对称图形。"))
    moves = [("把一个图形沿直线翻过来，大小和形状不变。", "轴对称", True),
             ("把一个图形沿某个方向移动一定距离，大小和形状不变。", "平移", True),
             ("把一个图形绕一个点转动一定角度，大小和形状不变。", "旋转", True),
             ("平移会改变图形的大小。", "平移", False),
             ("旋转会改变图形的形状。", "旋转", False),
             ("轴对称、平移、旋转都不改变图形的形状和大小。", "图形的运动", True)]
    for q, kind, truth in moves:
        t.append(B(q, truth, "%s只改变位置或方向，不改变形状和大小。" % kind))
    for deg in [90, 180, 270, 360]:
        t.append(S("一个图形绕点 O 顺时针旋转 %d° 后，与原图形相比？" % deg,
                   "形状大小不变，方向或位置改变" if deg != 360 else "与原图形完全重合",
                   ["形状变大", "形状变小", "变成另一个图形"],
                   "旋转不改变形状和大小；旋转 360° 回到原位。"))
    group("数学", "五上数学·四 图形的运动", t)

    # 五 用字母表示数和数量关系（新版不学解方程！）
    t = []
    letters = ["a", "b", "m", "n", "x", "y"]
    for L in letters:
        for k in range(2, 15):
            for c in range(1, 30, 3):
                t.append(S("用含字母的式子表示：%s 的 %d 倍再加 %d，结果是？" % (L, k, c),
                           "%d%s + %d" % (k, L, c),
                           ["%d(%s + %d)" % (k, L, c), "%s + %d" % (L, c + k), "%d%s - %d" % (k, L, c)],
                           "数字写在字母前面，乘号可省略：%d%s + %d。" % (k, L, c)))
                t.append(T("当 %s = %d 时，求 %d%s + %d 的值。" % (L, c, k, L, c),
                           [str(k * c + c)], "把 %s = %d 代入：%d×%d + %d = %d。" % (L, c, k, c, c, k * c + c)))
    for L in letters:
        for n in range(2, 12):
            t.append(S("%s × %d 可以简写成？" % (L, n), "%d%s" % (n, L),
                       ["%s%d" % (L, n), "%s + %d" % (L, n), "%d + %s" % (n, L)],
                       "省略乘号时一般把数字写在字母前面。"))
            t.append(B("1 × %s 通常写成 1%s。" % (L, L), False,
                       "1 与字母相乘时，1 通常省略不写，直接写成 %s。" % L))
    words = [("每支铅笔 a 元，买 5 支要多少元", "5a", ["a + 5", "a - 5", "a ÷ 5"]),
             ("汽车每小时行 m 千米，6 小时行多少千米", "6m", ["m + 6", "m ÷ 6", "6 + m"]),
             ("爸爸比小红大 25 岁，小红 a 岁，爸爸多少岁", "a + 25", ["25a", "a - 25", "25 - a"]),
             ("正方形边长 a，周长是多少", "4a", ["a²", "a + 4", "a ÷ 4"]),
             ("正方形边长 a，面积是多少", "a²", ["4a", "2a", "a + a"]),
             ("长方形长 a、宽 b，面积是多少", "ab", ["a + b", "2(a + b)", "a - b"]),
             ("长方形长 a、宽 b，周长是多少", "2(a + b)", ["ab", "a + b", "4a"])]
    for q, correct, ds in words:
        t.append(S(q + "？", correct, ds, "用字母表示数量关系时，乘号省略、数字写在字母前。"))
        t.append(B("上面这个数量关系可以写成 " + correct + "。", True, "用字母表示数与数量关系是第五单元的重点。"))
    group("数学", "五上数学·五 用字母表示数和数量关系", t)

    # 六 多边形的面积
    t = []
    for a in range(3, 20):
        for h in range(2, 15):
            s = a * h
            t.append(S("平行四边形的底是 %d 厘米，高是 %d 厘米，面积是多少平方厘米？" % (a, h), s,
                       [s + a, s - h, s * 2, s // 2],
                       "平行四边形面积 = 底 × 高 = %d × %d = %d。" % (a, h, s)))
            tri = Decimal(a * h) / 2
            t.append(S("三角形的底是 %d 厘米，高是 %d 厘米，面积是多少平方厘米？" % (a, h), tri,
                       [tri * 2, tri + Decimal("1"), tri / 2, tri + a],
                       "三角形面积 = 底 × 高 ÷ 2 = %d × %d ÷ 2 = %s。" % (a, h, fmt(tri))))
    for a in range(2, 15):
        for b in range(a + 1, 20, 3):
            for h in range(2, 13):
                s = Decimal((a + b) * h) / 2
                t.append(S("梯形上底 %d 厘米、下底 %d 厘米、高 %d 厘米，面积是多少平方厘米？" % (a, b, h), s,
                           [s * 2, s + Decimal("1"), s - Decimal("1"), Decimal((a + b) * h)],
                           "梯形面积 =（上底 + 下底）× 高 ÷ 2 = (%d + %d) × %d ÷ 2 = %s。" % (a, b, h, fmt(s))))
    for q, truth, tip in [
        ("平行四边形的面积等于底乘高。", True, "S = ah。"),
        ("三角形的面积等于底乘高，不用除以 2。", False, "三角形面积要除以 2。"),
        ("两个完全一样的三角形可以拼成一个平行四边形。", True, "倍拼法是推导三角形面积公式的基础。"),
        ("梯形面积公式是（上底 + 下底）× 高 ÷ 2。", True, "S = (a + b)h ÷ 2。"),
        ("面积相等的平行四边形，形状一定相同。", False, "底和高不同也可能面积相等。"),
        ("求平行四边形面积时，底和高必须互相对应。", True, "底和高要垂直对应。"),
    ]:
        t.append(B(q, truth, tip))
    group("数学", "五上数学·六 多边形的面积", t)

    # ☆ 有趣的密铺
    t = []
    tiles = [("三角形", True), ("平行四边形", True), ("梯形", True), ("正方形", True),
             ("长方形", True), ("正六边形", True), ("圆", False), ("正五边形", False),
             ("正八边形", False)]
    for name, can in tiles:
        t.append(B("%s可以单独密铺平面（既无重叠也无空隙）。" % name, can,
                   "能密铺的关键是拼接点处各角之和恰好为 360°；圆和正五边形不能密铺。"))
        t.append(S("下面哪种图形不能单独密铺？", "圆" if can else "正五边形",
                   ["三角形", "正方形", "梯形"] if can else ["三角形", "平行四边形", "正六边形"],
                   "圆之间有空隙；正五边形内角 108° 无法凑成 360°。"))
    group("数学", "五上数学·有趣的密铺", t)

    # 七 可能性
    t = []
    for r in range(1, 11):
        for w in range(1, 11):
            t.append(S("盒子里有 %d 个红球、%d 个白球（除颜色外相同），任意摸一个，摸到哪种球的可能性大？" % (r, w),
                       "红球" if r > w else ("白球" if w > r else "一样大"),
                       ["白球", "红球", "无法判断"] if r != w else ["红球", "白球", "都不是"],
                       "数量多的那种球被摸到的可能性大；数量相同时可能性一样大。"))
            t.append(B("盒子里全是 %d 个红球时，任意摸一个一定是红球。" % r, r > 0,
                       "全部是红球时摸到红球是「一定」，不可能摸到别的颜色。"))
    group("数学", "五上数学·七 可能性", t)

    # 八 复习与关联（含选学植树问题）
    t = []
    for price in [Decimal("2.5"), Decimal("3.6"), Decimal("4.8"), Decimal("1.2"), Decimal("6.5")]:
        for n in range(2, 12):
            total = price * n
            t.append(S("每本练习本 %s 元，买 %d 本一共要多少元？" % (fmt(price), n), total,
                       [total + price, total - price, total * 2],
                       "总价 = 单价 × 数量 = %s × %d = %s 元。" % (fmt(price), n, fmt(total))))
            t.append(J("每本练习本 %s 元，小明买 %d 本，付了 %d 元，应找回多少钱？写出计算过程。" %
                       (fmt(price), n, int(total) + 10),
                       "%s × %d = %s（元），%d - %s = %.2f（元）。" %
                       (fmt(price), n, fmt(total), int(total) + 10, fmt(total), 10),
                       "算出总价 50 分；算出找零 50 分。", "先算总价，再用付的钱减去总价。"))
    for L in range(20, 121, 10):
        for d in [2, 4, 5, 10]:
            for mode, delta in [("两端都栽", 1), ("只栽一端", 0), ("两端都不栽", -1)]:
                n = L // d + delta
                t.append(S("一条 %d 米长的小路，每隔 %d 米栽一棵树（%s），一共栽多少棵？" % (L, d, mode), n,
                           [n + 1, n - 1, n + 2],
                           "间隔数 = %d ÷ %d = %d；%s 时棵数 = 间隔数 %s。" %
                           (L, d, L // d, mode, "+1" if delta == 1 else ("不变" if delta == 0 else "-1"))))
    group("数学", "五上数学·八 复习与关联", t)


# ================================================================ 语文

POEMS = [
    ("示儿", "陆游", [("死去元知万事空", "但悲不见九州同"), ("王师北定中原日", "家祭无忘告乃翁")]),
    ("题临安邸", "林升", [("山外青山楼外楼", "西湖歌舞几时休"), ("暖风熏得游人醉", "直把杭州作汴州")]),
    ("己亥杂诗", "龚自珍", [("九州生气恃风雷", "万马齐喑究可哀"), ("我劝天公重抖擞", "不拘一格降人才")]),
    ("山居秋暝", "王维", [("空山新雨后", "天气晚来秋"), ("明月松间照", "清泉石上流"),
                       ("竹喧归浣女", "莲动下渔舟"), ("随意春芳歇", "王孙自可留")]),
    ("枫桥夜泊", "张继", [("月落乌啼霜满天", "江枫渔火对愁眠"), ("姑苏城外寒山寺", "夜半钟声到客船")]),
    ("早春呈水部张十八员外", "韩愈", [("天街小雨润如酥", "草色遥看近却无"),
                                ("最是一年春好处", "绝胜烟柳满皇都")]),
]

DUOYIN = [
    ("角落", "jiǎo"), ("角色", "jué"), ("行走", "xíng"), ("银行", "háng"),
    ("快乐", "lè"), ("音乐", "yuè"), ("发现", "fā"), ("头发", "fà"),
    ("重复", "chóng"), ("重要", "zhòng"), ("干净", "gān"), ("干活", "gàn"),
    ("好人", "hǎo"), ("爱好", "hào"), ("睡觉", "jiào"), ("觉得", "jué"),
    ("长短", "cháng"), ("长大", "zhǎng"), ("少数", "shǎo"), ("少年", "shào"),
    ("中间", "zhōng"), ("中弹", "zhòng"), ("空地", "kòng"), ("天空", "kōng"),
    ("几乎", "jī"), ("几个", "jǐ"), ("朝向", "cháo"), ("朝阳", "zhāo"),
    ("便宜", "pián"), ("方便", "biàn"), ("传说", "chuán"), ("传记", "zhuàn"),
    ("似乎", "sì"), ("似的", "shì"), ("露水", "lù"), ("露面", "lòu"),
    ("折断", "zhé"), ("折腾", "zhē"), ("投降", "xiáng"), ("降落", "jiàng"),
    ("测量", "liáng"), ("重量", "liàng"), ("店铺", "pù"), ("铺开", "pū"),
    ("种子", "zhǒng"), ("种地", "zhòng"), ("背诵", "bèi"), ("背包", "bēi"),
    ("划船", "huá"), ("计划", "huà"), ("鲜血", "xuè"), ("削铅笔", "xiāo"),
]

JINYI = [
    ("高兴", "快乐"), ("美丽", "漂亮"), ("立刻", "马上"), ("著名", "有名"),
    ("寒冷", "严寒"), ("盼望", "渴望"), ("爱护", "爱惜"), ("宽阔", "广阔"),
    ("坚强", "顽强"), ("安静", "宁静"), ("著名", "闻名"), ("灵敏", "敏捷"),
    ("朴素", "朴实"), ("疲倦", "疲劳"), ("叮嘱", "嘱咐"), ("欣赏", "观赏"),
    ("格外", "特别"), ("仿佛", "好像"), ("赶紧", "连忙"), ("沉思", "深思"),
    ("寻常", "平常"), ("精巧", "精致"), ("恩惠", "恩情"), ("悠然", "悠闲"),
    ("担忧", "担心"), ("居然", "竟然"), ("爱慕", "喜爱"), ("分辨", "辨别"),
    ("体面", "得体"), ("吩咐", "嘱咐"), ("姿态", "姿势"), ("茂盛", "繁茂"),
    ("呵斥", "斥责"), ("轻易", "容易"), ("谴责", "指责"), ("协调", "和谐"),
    ("理所当然", "天经地义"), ("不计其数", "数不胜数"), ("无穷无尽", "无边无际"),
    ("震天动地", "惊天动地"), ("千真万确", "确凿无疑"), ("相依为命", "相濡以沫"),
]

FANYI = [
    ("宽阔", "狭窄"), ("谦虚", "骄傲"), ("勤奋", "懒惰"), ("诚实", "虚伪"),
    ("朴素", "华丽"), ("敏捷", "迟钝"), ("清晰", "模糊"), ("热闹", "安静"),
    ("简单", "复杂"), ("丰富", "贫乏"), ("节约", "浪费"), ("光明", "黑暗"),
    ("伟大", "渺小"), ("坚强", "软弱"), ("正确", "错误"), ("安全", "危险"),
    ("容易", "困难"), ("雪白", "乌黑"), ("笔直", "弯曲"), ("增加", "减少"),
    ("开始", "结束"), ("喜欢", "讨厌"), ("表扬", "批评"), ("精致", "粗糙"),
    ("柔软", "坚硬"), ("炎热", "寒冷"), ("干燥", "潮湿"), ("慌张", "镇定"),
    ("稀疏", "茂密"), ("崭新", "破旧"), ("遵守", "违反"), ("聚集", "分散"),
    ("进攻", "撤退"), ("聪明", "愚笨"), ("勇敢", "怯懦"), ("善良", "凶恶"),
    ("温暖", "寒冷"), ("活泼", "呆板"), ("整洁", "凌乱"), ("沉重", "轻盈"),
    ("缓慢", "迅速"), ("熟悉", "陌生"), ("犹豫", "果断"), ("平凡", "伟大"),
    ("短暂", "长久"), ("欢乐", "悲伤"), ("繁忙", "清闲"), ("公开", "秘密"),
    ("赞成", "反对"), ("上涨", "下降"), ("扩大", "缩小"), ("肯定", "否定"),
    ("活跃", "沉闷"), ("主动", "被动"), ("成功", "失败"), ("优点", "缺点"),
]

CHENGYU = [
    ("一心一意", "心思、意念专一"), ("三心二意", "犹豫不决或用心不专"),
    ("五颜六色", "形容色彩繁多"), ("七上八下", "形容心神慌乱不安"),
    ("九牛一毛", "极大数量中微不足道的一小部分"), ("十全十美", "各方面都非常完美"),
    ("百发百中", "每次都命中目标，比喻做事有充分把握"), ("千军万马", "形容雄壮的队伍或浩大的声势"),
    ("自言自语", "自己跟自己说话"), ("无边无际", "没有边际，形容范围极为广阔"),
    ("无影无踪", "没有一点踪影，形容完全消失"), ("有始有终", "做事能坚持到底"),
    ("大惊小怪", "对平常的事情过分惊讶"), ("东张西望", "向四处张望"),
    ("左顾右盼", "向左右两边看"), ("南辕北辙", "行动和目的相反"),
    ("画蛇添足", "做了多余的事，反而不恰当"), ("守株待兔", "死守狭隘经验，不知变通"),
    ("亡羊补牢", "出了问题及时补救"), ("掩耳盗铃", "自己欺骗自己"),
    ("刻舟求剑", "拘泥成法，不知变通"), ("井底之蛙", "见识狭小的人"),
    ("狐假虎威", "倚仗别人的势力欺压人"), ("对牛弹琴", "对不懂的人讲道理，白费口舌"),
    ("自相矛盾", "言行前后抵触"), ("拔苗助长", "违反规律强求速成，反而坏事"),
    ("望梅止渴", "用空想安慰自己"), ("闻鸡起舞", "勤奋刻苦，及时奋发"),
    ("凿壁偷光", "形容勤学苦读"), ("手不释卷", "手里的书舍不得放下，形容勤奋好学"),
    ("废寝忘食", "顾不得睡觉吃饭，形容非常专心"), ("专心致志", "一心一意，集中精神"),
    ("聚精会神", "集中精神，专心一意"), ("全神贯注", "全部精神集中在一点"),
    ("一丝不苟", "做事认真细致，一点不马虎"), ("精益求精", "已经很好还求更好"),
    ("锲而不舍", "坚持不懈，不放弃"), ("持之以恒", "长久坚持下去"),
    ("水滴石穿", "力量虽小，坚持下去就能成功"), ("脚踏实地", "做事踏实认真"),
    ("实事求是", "从实际情况出发，不夸大不缩小"), ("名副其实", "名声或名称与实际相符"),
    ("画龙点睛", "在关键处点明要点，使内容更精彩"), ("锦上添花", "好上加好"),
    ("雪中送炭", "在别人急需时给予帮助"), ("助人为乐", "把帮助别人当作快乐"),
    ("拾金不昧", "拾到财物不隐藏、不占为己有"), ("见义勇为", "看到正义的事勇敢去做"),
    ("大公无私", "完全为公，没有私心"), ("任劳任怨", "做事不辞劳苦，不怕别人埋怨"),
    ("风和日丽", "天气晴朗暖和"), ("鸟语花香", "形容春天美好的景象"),
    ("山清水秀", "形容山水风景优美"), ("万紫千红", "形容百花齐放，色彩艳丽"),
    ("生机勃勃", "形容生命力旺盛"), ("欣欣向荣", "形容草木茂盛，事业蓬勃发展"),
    ("硕果累累", "形容取得的成果很多"), ("五谷丰登", "粮食丰收"),
    ("天高云淡", "天空高远，云彩淡薄"), ("秋高气爽", "秋天天空晴朗，空气清爽"),
    ("冰天雪地", "形容非常寒冷的景象"), ("狂风暴雨", "猛烈的风雨"),
    ("电闪雷鸣", "雷电交加，形容雨势猛烈"), ("水平如镜", "水面平静得像镜子"),
    ("连绵不断", "接连不断，不间断"), ("络绎不绝", "行人车马来往不断"),
    ("人山人海", "聚集的人极多"), ("川流不息", "像水流一样连续不断"),
    ("应接不暇", "来人或事情太多，接待应付不过来"), ("琳琅满目", "眼前全是珍贵美好的东西"),
    ("美不胜收", "美好的东西太多，一时看不过来"), ("别具一格", "另有一种独特的风格"),
    ("巧夺天工", "人工的精巧胜过天然"), ("栩栩如生", "形容艺术形象非常逼真"),
    ("惟妙惟肖", "描写或模仿得非常逼真"), ("绘声绘色", "讲述、描写生动逼真"),
    ("娓娓动听", "说话婉转生动，使人爱听"), ("口若悬河", "说话滔滔不绝，能言善辩"),
    ("滔滔不绝", "像流水那样毫不间断，指话很多"), ("对答如流", "回答问话像流水一样流畅"),
    ("出口成章", "说出话来就是一篇文章，形容文思敏捷"), ("一气呵成", "文章或做事连贯不断，一次完成"),
    ("理直气壮", "理由正当充分，说话有气势"), ("完璧归赵", "把原物完好地归还本人"),
    ("负荆请罪", "主动向人认错赔罪"), ("同心协力", "团结一致，共同努力"),
    ("难以置信", "很难让人相信"), ("不计其数", "没法计算数目，形容很多"),
    ("无穷无尽", "没有止境，没有限度"), ("震天动地", "声音或声势极大"),
    ("千真万确", "形容情况非常确实"), ("相依为命", "互相依靠着过日子"),
    ("举世闻名", "全世界都知道，形容非常著名"), ("众星拱月", "许多星星环绕着月亮"),
    ("金碧辉煌", "形容建筑物华丽光彩"), ("玲珑剔透", "形容器物精致通明"),
    ("诗情画意", "像诗画里所描摹的意境"), ("奇珍异宝", "奇异罕见的珍宝"),
]

CUOBIE = [
    ("再接再厉", "再接再励"), ("迫不及待", "迫不急待"), ("一如既往", "一如继往"),
    ("川流不息", "穿流不息"), ("名列前茅", "名列前矛"), ("谈笑风生", "谈笑风声"),
    ("走投无路", "走头无路"), ("世外桃源", "世外桃园"), ("滥竽充数", "烂竽充数"),
    ("脍炙人口", "烩炙人口"), ("一如既往", "一如即往"), ("变本加厉", "变本加利"),
    ("按部就班", "按步就班"), ("不胫而走", "不径而走"), ("出类拔萃", "出类拔粹"),
    ("甘拜下风", "甘败下风"), ("汗流浃背", "汗流夹背"), ("好高骛远", "好高鹜远"),
    ("焕然一新", "换然一新"), ("记忆犹新", "记忆尤新"), ("金榜题名", "金榜提名"),
    ("鞠躬尽瘁", "鞠躬尽粹"), ("苦心孤诣", "苦心孤旨"), ("流连忘返", "留连忘返"),
    ("漫不经心", "慢不经心"), ("名列前茅", "名列前毛"), ("莫名其妙", "莫明其妙"),
    ("目不暇接", "目不瑕接"), ("迫不及待", "迫不急侍"), ("气势磅礴", "气势磅薄"),
    ("恰如其分", "恰如其份"), ("融会贯通", "融汇贯通"), ("首屈一指", "手屈一指"),
    ("水龙头", "水笼头"), ("度假", "渡假"), ("即使", "既使"),
    ("既然", "即然"), ("部署", "布署"), ("竣工", "峻工"),
]


def gen_chinese():
    # 课文与文学常识（严格按 2026 秋版目录）
    t = []
    lessons = [
        ("《桂花雨》", "琦君", "一", "借桂花抒发对故乡和童年的思念"),
        ("《落花生》", "许地山", "一", "借花生说明要做有用的人"),
        ("《珍珠鸟》", "冯骥才", "一", "信赖，往往创造出美好的境界"),
        ("《冀中的地道战》", "", "二", "介绍地道战这种特殊的斗争方式"),
        ("《将相和》", "司马迁（据《史记》改编）", "二", "由完璧归赵、渑池会面、负荆请罪三个故事组成"),
        ("《什么比猎豹的速度更快》", "", "二", "按速度由慢到快介绍事物"),
        ("《“诺曼底号”遇难记》", "雨果", "二", "歌颂哈尔威船长临危不乱、忠于职守"),
        ("《猎人海力布》", "", "三", "民间故事，海力布为救乡亲变成石头"),
        ("《牛郎织女（一）》", "叶圣陶（整理）", "三", "民间故事"),
        ("《牛郎织女（二）》", "叶圣陶（整理）", "三", "民间故事"),
        ("《古诗三首》", "陆游、林升、龚自珍", "四", "表达爱国情怀"),
        ("《少年中国说（节选）》", "梁启超", "四", "少年强则国强"),
        ("《圆明园的毁灭》", "", "四", "写圆明园的辉煌与被毁，激发爱国情感"),
        ("《梅兰芳蓄须明志》", "", "四", "表现梅兰芳的民族气节"),
        ("《太阳》", "", "五", "说明文，用列数字、作比较等说明方法"),
        ("《金字塔》", "", "五", "说明性文章"),
        ("《慈母情深》", "梁晓声", "六", "通过细节描写表现母爱"),
        ("《父爱之舟》", "吴冠中", "六", "以梦境回忆父亲的爱"),
        ("《航天员写给孩子的信》", "", "六", "体会父母之爱"),
        ("《古诗词三首》", "王维、张继、韩愈", "七", "描写自然景致"),
        ("《第一场雪》", "峻青", "七", "写景散文"),
        ("《白鹭》", "郭沫若", "七", "白鹭是一首精巧的诗"),
        ("《古人谈读书》", "《论语》、朱熹", "八", "谈读书态度与方法"),
        ("《忆读书》", "冰心", "八", "回忆读书经历，谈读书体会"),
        ("《走遍天下书为侣》", "尤安·艾肯", "八", "把书当作伴侣，反复阅读"),
    ]
    for name, author, unit, point in lessons:
        t.append(S("%s在 2026 秋版语文五年级上册的第几单元？" % name, "第%s单元" % unit,
                   ["第一单元", "第三单元", "第五单元", "第八单元"],
                   "%s属于第%s单元，单元要点：%s。" % (name, unit, point)))
        t.append(B("%s是 2026 秋版五年级上册的课文。" % name, True,
                   "%s：%s。" % (name, point)))
        if author:
            t.append(T("%s的作者（或出处）是什么？" % name, [author.split("（")[0]],
                       "%s的作者/出处是%s。" % (name, author)))
    for si, story in enumerate(["完璧归赵", "渑池会面", "负荆请罪"], 1):
        t.append(S("（第%d组）下面哪个是《将相和》里的故事？" % si, story,
                   ["草船借箭", "三打白骨精", "田忌赛马"],
                   "《将相和》由完璧归赵、渑池会面、负荆请罪三个小故事组成。"))
    group("语文", "五上语文·课文与单元", t)

    # 古诗（新版六首）
    t = []
    for title, author, lines in POEMS:
        for up, down in lines:
            t.append(T("补全诗句：「%s」，下一句是？" % up, [down],
                       "出自%s《%s》：「%s，%s。」" % (author, title, up, down)))
            t.append(T("补全诗句：「%s」，上一句是？" % down, [up],
                       "出自%s《%s》：「%s，%s。」" % (author, title, up, down)))
            t.append(S("「%s」出自哪首诗？" % up, title,
                       [p[0] for p in POEMS if p[0] != title][:3],
                       "「%s，%s。」出自%s《%s》。" % (up, down, author, title)))
            t.append(B("「%s」是《%s》中的诗句。" % (up, title), True,
                       "%s《%s》原句：「%s，%s。」" % (author, title, up, down)))
        t.append(S("《%s》的作者是谁？" % title, author,
                   [a for _, a, _ in POEMS if a != author][:3],
                   "《%s》的作者是%s。" % (title, author)))
        t.append(B("《%s》是 2026 秋版五年级上册课本里的古诗词。" % title, True,
                   "《%s》收在第四或第七单元的古诗（词）三首中。" % title))
    t.append(T("《古人谈读书》中「知之为知之，不知为不知」的下一句是？", ["是知也"],
               "出自《论语》：知之为知之，不知为不知，是知也。"))
    t.append(T("朱熹说读书有三到，指的是哪三到？", ["心到、眼到、口到", "心到眼到口到"],
               "余尝谓读书有三到，谓心到、眼到、口到。"))
    t.append(S("「三到之中，心到最急」的「急」是什么意思？", "要紧、重要",
               ["着急", "急速", "急忙"], "这里的「急」是要紧、重要的意思。"))
    group("语文", "五上语文·古诗文与日积月累", t)

    # 字词基础（多音字、错别字、近反义、成语）
    t = []
    allpy = list({p for _, p in DUOYIN})
    for word, py in DUOYIN:
        ds = [p for p in allpy if p != py][:3]
        t.append(S("「%s」中加点字的正确读音是？" % word, py, ds,
                   "「%s」读 %s，注意多音字在不同词语中的读音。" % (word, py)))
        t.append(B("「%s」的「%s」读作 %s。" % (word, word[0], py), True,
                   "多音字要结合词义定音，「%s」读 %s。" % (word, py)))
    for right, wrong in CUOBIE:
        t.append(B("「%s」这个词语中没有错别字。" % right, True,
                   "正确写法是「%s」，「%s」是常见错写。" % (right, wrong)))
        t.append(B("「%s」这个词语没有错别字。" % wrong, False,
                   "正确写法是「%s」。" % right))
        t.append(S("「%s」和「%s」中，书写正确的是哪一个？" % (wrong, right), right,
                   [wrong, "一如继往", "迫不急待"],
                   "正确写法是「%s」，「%s」是常见错写。" % (right, wrong)))
    for a, b in JINYI:
        t.append(S("「%s」的近义词是？" % a, b,
                   [x for _, x in FANYI[:3]], "「%s」和「%s」意思相近。" % (a, b)))
        t.append(B("「%s」和「%s」是一对近义词。" % (a, b), True, "两词意思相近。"))
    for a, b in FANYI:
        t.append(S("「%s」的反义词是？" % a, b,
                   [x for x, _ in JINYI[:3]], "「%s」和「%s」意思相反。" % (a, b)))
        t.append(B("「%s」和「%s」意思相反。" % (a, b), True, "这是一对反义词。"))
    for cy, mean in CHENGYU:
        t.append(S("成语「%s」的意思是？" % cy, mean,
                   [m for _, m in R.sample(CHENGYU, 3) if m != mean][:3],
                   "「%s」：%s。" % (cy, mean)))
        t.append(T("把成语补充完整：「%s」" % cy.replace(cy[0], "＿", 1), [cy],
                   "完整成语是「%s」，意思是：%s。" % (cy, mean)))
        t.append(B("「%s」形容：%s。" % (cy, mean), True, "「%s」：%s。" % (cy, mean)))
    for i in range(0, len(CHENGYU) - 4, 5):
        chunk = CHENGYU[i:i + 4]
        t.append(M("下面哪些成语含有数字？", [c[0] for c in chunk],
                   [j for j, (c, _) in enumerate(chunk) if any(ch in c for ch in "一二三四五六七八九十百千万")],
                   "带数字的成语如一心一意、七上八下、百发百中等。"))
    group("语文", "五上语文·字词句基础", t)

    # 阅读与表达（说明方法、修辞、句式、标点）
    t = []
    methods = ["列数字", "作比较", "打比方", "举例子", "分类别"]
    examples = [
        ("太阳离我们约有一亿五千万千米远。", "列数字"),
        ("约一百三十万个地球的体积才能抵得上一个太阳。", "作比较"),
        ("太阳会发光，会发热，是个大火球。", "打比方"),
        ("到太阳上去，如果步行，日夜不停地走，差不多要走三千五百年。", "举例子"),
        ("鲸的种类很多，总的来说可以分为须鲸和齿鲸两大类。", "分类别"),
    ]
    for sent, m in examples:
        t.append(S("「%s」主要用了哪种说明方法？" % sent, m,
                   [x for x in methods if x != m][:3],
                   "这句话用的是「%s」。" % m))
        t.append(B("「%s」这句话用了「%s」的说明方法。" % (sent, m), True,
                   "说明方法要配合说明目的，《太阳》一课是重点。"))
    rhetoric = [
        ("白鹭是一首精巧的诗。", "比喻"),
        ("桂花树的样子笨笨的，不像梅树那样有姿态。", "对比"),
        ("红嘴红脚，灰蓝色的毛，只是后背还没生出珍珠似的圆圆的白点。", "比喻"),
        ("它好肥，整个身子好像一个蓬松的球儿。", "比喻"),
        ("晴天的清晨，每每看见它孤独地站立于小树的绝顶。", "拟人"),
        ("山洪咆哮着，像一群受惊的野马。", "比喻"),
    ]
    for sent, r in rhetoric:
        t.append(S("「%s」主要运用了什么修辞（或表达）手法？" % sent, r,
                   ["夸张", "设问", "反问", "排比"],
                   "这里用的是「%s」，体会这样写的好处。" % r))
    for q, ans, tip in [
        ("把「我把作业写完了」改成「被」字句。", "作业被我写完了。", "把字句改被字句：把受事对象提前。"),
        ("把「这本书被我看完了」改成「把」字句。", "我把这本书看完了。", "被字句改把字句：把施事者提前。"),
        ("把「这里的风景很美」改成反问句。", "难道这里的风景不美吗？", "陈述句改反问句要加反问词、改肯定否定、句末用问号。"),
        ("把「难道我们不应该珍惜粮食吗？」改成陈述句。", "我们应该珍惜粮食。", "反问句改陈述句：去掉反问词，否定改肯定。"),
    ]:
        t.append(T(q, [ans], tip))
    for sent, correct in [
        ("你今天去图书馆吗", "？"), ("多么美丽的白鹭啊", "！"),
        ("桂花雨落下来了", "。"), ("他喜欢读书、画画和唱歌", "。"),
    ]:
        t.append(S("给句子「%s」选择正确的句末标点。" % sent, correct, ["。", "！", "？", "，"],
                   "根据句子语气选择句号、问号或叹号。"))
    ZAOCI = ["高兴", "美丽", "立刻", "著名", "盼望", "爱护", "宽阔", "安静", "坚强",
             "疲倦", "叮嘱", "欣赏", "格外", "仿佛", "赶紧", "沉思", "寻常", "精巧",
             "悠然", "担忧", "居然", "爱慕", "分辨", "吩咐", "茂盛", "谴责", "协调",
             "纯洁", "诚实", "勤奋", "谦虚", "朴素", "敏捷", "清晰", "热闹", "节约",
             "伟大", "勇敢", "整洁", "熟悉", "犹豫", "平凡", "繁忙", "赞成", "主动"]
    for i in range(120):
        a = ZAOCI[i % len(ZAOCI)]
        b = ZAOCI[(i * 7 + 3) % len(ZAOCI)]
        t.append(J("（第%d组）用「%s」和「%s」各写一句话，注意把意思写清楚。" % (i + 1, a, b),
                   "示例：%s；%s。" % (a, b),
                   "两个词语各造一个句子 50 分；句子完整通顺 30 分；用词准确 20 分。",
                   "造句要先想清楚词语的意思。", 3))
    group("语文", "五上语文·阅读与表达", t)

    # 综合运用：成语变式、量词、关联词、词语归类、课文理解
    t2 = []
    for cy, mean in CHENGYU:
        cs = list(cy)
        for pos in (0, 1, len(cs) - 1):
            if pos >= len(cs):
                continue
            blank = "".join("＿" if j == pos else c for j, c in enumerate(cs))
            t2.append(T("补全成语：%s（意思：%s）" % (blank, mean), [cy],
                        "完整成语是「%s」：%s。" % (cy, mean)))
    LC = [("花", "朵"), ("树", "棵"), ("书", "本"), ("鸟", "只"), ("鱼", "条"),
          ("马", "匹"), ("牛", "头"), ("桥", "座"), ("山", "座"), ("河", "条"),
          ("船", "只"), ("画", "幅"), ("歌", "首"), ("诗", "首"), ("信", "封"),
          ("灯", "盏"), ("伞", "把"), ("笔", "支"), ("纸", "张"), ("桌子", "张"),
          ("椅子", "把"), ("衣服", "件"), ("鞋", "双"), ("帽子", "顶"),
          ("房子", "间"), ("门", "扇"), ("课", "节"), ("车", "辆"),
          ("飞机", "架"), ("云", "朵"), ("星", "颗"), ("米", "粒"),
          ("水", "滴"), ("雨", "阵"), ("风", "阵"), ("饼", "块"),
          ("石头", "块"), ("绳子", "根"), ("头发", "根")]
    for noun, lw in LC:
        t2.append(T("填上合适的量词：一（ ）%s" % noun, [lw],
                    "通常说「一%s%s」。" % (lw, noun)))
        t2.append(S("「一（ ）%s」中，哪个量词最合适？" % noun, lw,
                    ["条", "座", "支"], "搭配「%s」常用量词「%s」。" % (noun, lw)))
    GUAN = [
        ("（ ）明天不下雨，我们（ ）去爬山。", "如果……就……"),
        ("（ ）他平时很努力，（ ）成绩一直很好。", "因为……所以……"),
        ("（ ）天气很冷，（ ）同学们仍然坚持晨跑。", "虽然……但是……"),
        ("他（ ）会画画，（ ）会弹钢琴。", "不但……而且……"),
        ("（ ）遇到多大困难，我们（ ）不能放弃。", "无论……都……"),
        ("（ ）多读多练，（ ）能把字写好。", "只有……才……"),
        ("（ ）你答应了别人，（ ）要做到。", "既然……就……"),
        ("（ ）太阳离我们很远，（ ）它看上去不大。", "因为……所以……"),
        ("（ ）是刮风还是下雨，他（ ）按时到校。", "无论……都……"),
        ("这本书（ ）内容有趣，（ ）插图精美。", "不但……而且……"),
    ]
    others = ["如果……就……", "因为……所以……", "虽然……但是……", "不但……而且……",
              "无论……都……", "只有……才……", "既然……就……"]
    for sent, ans in GUAN:
        t2.append(S("选择合适的关联词：%s" % sent, ans,
                    [x for x in others if x != ans][:3],
                    "先分清分句之间是因果、转折、条件还是假设关系。"))
    CATS = {
        "表示心情": ["高兴", "难过", "兴奋", "担忧", "害怕", "激动", "愤怒", "喜悦"],
        "表示颜色": ["雪白", "乌黑", "金黄", "碧绿", "火红", "湛蓝", "灰白", "粉红"],
        "表示看": ["注视", "端详", "眺望", "凝视", "俯视", "环顾", "打量", "张望"],
        "表示说": ["叮嘱", "吩咐", "议论", "争辩", "讲述", "呼喊", "回答", "商议"],
        "表示时间短暂": ["立刻", "马上", "顿时", "霎时", "瞬间", "转眼", "忽然", "顷刻"],
    }
    flat = [(c, w) for c, ws in CATS.items() for w in ws]
    for i in range(60):
        cat = list(CATS)[i % len(CATS)]
        k = (i * 3) % 6
        inside = CATS[cat][k:k + 2]
        outside = [w for c, w in flat if c != cat][(i * 5) % 24:(i * 5) % 24 + 2]
        if len(outside) < 2:
            outside = [w for c, w in flat if c != cat][:2]
        a = inside + outside
        R.shuffle(a)
        idx = [j for j, w in enumerate(a) if w in inside]
        t2.append(M("（第%d组）下面哪些词属于「%s」这一类？" % (i + 1, cat), a, idx,
                    "按词义归类，先找这些词的共同点。"))
    for name, author, unit, point in lessons:
        t2.append(B("%s%s。" % (name, point), True,
                    "这是第%s单元课文《%s》的主要内容或写法。" % (unit, name.strip("《》"))))
    for i, (name, author, unit, point) in enumerate(lessons):
        other = lessons[(i + 5) % len(lessons)][3]
        t2.append(B("%s%s。" % (name, other), False,
                    "《%s》的内容不是这样，别把课文特点张冠李戴。" % name.strip("《》")))
    group("语文", "五上语文·综合运用", t2)


# ================================================================ 英语

WORDS = {
    "Unit 1 Different friends": [
        ("team", "队；组"), ("player", "运动员"), ("him", "他（宾格）"),
        ("lovely", "可爱的；优美的"), ("clever", "聪明的"), ("young", "年轻的"),
        ("hard-working", "工作努力的"), ("science", "科学"), ("robot", "机器人"),
        ("jump", "跳"), ("rope", "绳"), ("piano", "钢琴"), ("chess", "国际象棋"),
        ("front", "前部"), ("easy", "容易的"), ("star", "明星"),
        ("wonderful", "精彩的"), ("Australia", "澳大利亚"),
        ("tall", "高的"), ("strong", "强壮的"), ("friendly", "友好的"),
        ("quiet", "文静的"), ("helpful", "乐于助人的"), ("jump rope", "跳绳"),
        ("play the piano", "弹钢琴"), ("play Chinese chess", "下中国象棋"),
        ("make robots", "制作机器人"), ("be good at", "擅长"),
    ],
    "Unit 2 My feelings": [
        ("sad", "难过的"), ("matter", "事情；问题"), ("project", "项目"),
        ("centre", "中心"), ("agree", "同意"), ("finish", "完成"),
        ("Monday", "星期一"), ("worried", "担心的"), ("both", "两者"),
        ("excited", "兴奋的"), ("wrong", "错误的"), ("angry", "生气的"),
        ("afraid", "害怕的"), ("parent", "父亲或母亲"), ("ask", "问"),
        ("move", "搬家；移动"), ("yours", "您的"), ("happy", "高兴的"),
        ("tired", "疲倦的"), ("What's the matter?", "怎么了？"),
    ],
    "Unit 3 Work and play": [
        ("Wednesday", "星期三"), ("subject", "科目"), ("Monday", "星期一"),
        ("Tuesday", "星期二"), ("Friday", "星期五"), ("because", "因为"),
        ("Thursday", "星期四"), ("start", "开始"), ("usually", "通常"),
        ("weekend", "周末"), ("sometimes", "有时"), ("Saturday", "星期六"),
        ("Sunday", "星期日"), ("lesson", "课"), ("evening", "晚上"),
        ("answer", "回答"), ("ping-pong", "乒乓球"), ("night", "夜晚"),
        ("visit", "拜访"), ("grandparent", "祖父母"), ("Chinese", "语文"),
        ("maths", "数学"), ("English", "英语"), ("music", "音乐"),
    ],
    "Unit 4 Healthy habits": [
        ("stay", "保持"), ("should", "应该"), ("flu", "流感"),
        ("else", "其他的"), ("exercise", "锻炼"), ("enough", "足够的"),
        ("if", "如果"), ("habit", "习惯"), ("show", "节目"),
        ("phone", "电话"), ("then", "那么"), ("rest", "休息"),
        ("take care of", "照顾"), ("check", "查看"), ("less", "较少的"),
        ("brush", "刷"), ("tooth", "牙齿"), ("twice", "两次"),
        ("hour", "小时"), ("free", "空闲的"), ("healthy", "健康的"),
        ("wash your hands", "洗手"), ("brush your teeth", "刷牙"),
        ("eat breakfast", "吃早餐"), ("see a doctor", "看医生"),
    ],
    "Unit 5 Food we eat": [
        ("hungry", "饥饿的"), ("beef", "牛肉"), ("ice cream", "冰激凌"),
        ("little", "少许"), ("dumpling", "饺子"), ("tea", "茶"),
        ("hamburger", "汉堡包"), ("Mrs", "太太"), ("coconut", "椰子"),
        ("interesting", "有趣的"), ("seed", "种子"), ("pull up", "拔出"),
        ("stem", "茎"), ("root", "根"), ("lotus", "莲"),
        ("lake", "湖"), ("world", "世界"), ("round", "圆形的"),
        ("different", "不同的"), ("way", "方法"), ("milk", "牛奶"),
        ("noodles", "面条"), ("soup", "汤"), ("salad", "沙拉"),
        ("juice", "果汁"), ("chicken", "鸡肉"), ("cake", "蛋糕"),
    ],
    "Unit 6 Nature and us": [
        ("river", "河流"), ("nature", "大自然"), ("waterfall", "瀑布"),
        ("forest", "森林"), ("famous", "著名的"), ("mountain", "高山"),
        ("wind", "风"), ("trip", "旅行"), ("dangerous", "危险的"),
        ("heavy", "严重的；重的"), ("hotel", "旅馆"), ("close", "关闭"),
        ("umbrella", "雨伞"), ("raincoat", "雨衣"), ("worry", "担心"),
        ("fine", "晴朗的"), ("fog", "雾"), ("flood", "洪水"),
        ("fire", "火"), ("know", "知道"), ("before", "在……之前"),
        ("go hiking", "去徒步"), ("bring", "带来"), ("lake", "湖"),
        ("tree", "树"), ("sky", "天空"), ("cloud", "云"),
    ],
}


def gen_english():
    all_words = [(en, zh, unit) for unit, ws in WORDS.items() for en, zh in ws]
    for unit, ws in WORDS.items():
        t = []
        pool = [x[1] for x in all_words]
        for en, zh in ws:
            ds = [z for z in R.sample(pool, 8) if z != zh][:3]
            t.append(S("单词 %s 的中文意思是？" % en, zh, ds,
                       "%s：%s。（%s）" % (en, zh, unit)))
            ds2 = [w for w, _, _ in R.sample(all_words, 8) if w != en][:3]
            t.append(S("「%s」对应的英文单词是？" % zh, en, ds2,
                       "%s = %s。" % (zh, en)))
            t.append(T("写出英文单词：%s" % zh, [en, en.lower()],
                       "%s 的英文是 %s，注意拼写。" % (zh, en)))
            t.append(B("%s 的意思是「%s」。" % (en, zh), True,
                       "%s = %s。" % (en, zh)))
            wrong = [z for z in pool if z != zh][0]
            t.append(B("%s 的意思是「%s」。" % (en, wrong), False,
                       "%s 的意思是「%s」，不是「%s」。" % (en, zh, wrong)))
        # 分类多选
        for i in range(0, len(ws) - 3, 4):
            chunk = [w for w, _ in ws[i:i + 4]]
            cand = [p for p in all_words if p[0] not in chunk]
            outside = [p[0] for p in R.sample(cand, 2)]
            a = chunk + outside
            R.shuffle(a)
            idx = [j for j, w in enumerate(a) if w in chunk]
            t.append(M("（%s 单元 第%d组）下面哪些是本单元学过的单词？" % (unit.split()[1], i),
                       a, idx, "按单元主题归类记单词效果更好。"))
        group("英语", "五上英语·" + unit.split()[1] + " 词汇", t)

    # 句型与语法（按新教材核心句型）
    t = []
    for i in range(1, 60):
        adj = ["lovely", "clever", "young", "hard-working", "tall", "strong", "friendly", "quiet", "helpful"][i % 9]
        pron, be = [("he", "He's"), ("she", "She's")][i % 2]
        t.append(S("—What's %s like?（提示：%s）  —______" % (pron, adj), be + " " + adj + ".",
                   ["He's " + ("sad" if adj != "sad" else "happy") + ".", "She can dance.", "I'm fine."],
                   "问外貌性格用 What's ... like?，答语用 He's / She's + 形容词。"))
        t.append(S("—What can %s do?（第%d组）  —______" % (pron, i), "He can make robots." if pron == "he" else "She can jump rope.",
                   ["He's clever.", "She is young.", "I'd like some tea."],
                   "问能力用 What can ... do?，答语用 can + 动词原形。"))
        t.append(S("—Can you play the piano?（第%d组）  —______" % i, "Yes, I can.",
                   ["Yes, I am.", "Yes, I do.", "No, I don't."],
                   "Can 引导的一般疑问句，用 can / can't 回答。"))
    for feeling in ["sad", "worried", "excited", "angry", "afraid", "tired"]:
        t.append(S("—What's the matter?  —______", "I'm %s." % feeling,
                   ["I'm fine, thank you.", "I'd like some tea.", "It's Monday."],
                   "What's the matter? 用来询问对方怎么了，回答用 I'm + 情绪词。"))
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        t.append(S("—What do you have on %ss?  —______" % day, "We have Chinese and maths.",
                   ["I'd like some beef.", "There is a river.", "He's clever."],
                   "on + 星期几（复数）表示每逢那天，回答用 have + 科目。"))
        t.append(T("写出英文：%s" % {"Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三",
                                   "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六",
                                   "Sunday": "星期日"}[day], [day],
                   "星期首字母要大写：%s。" % day))
    for good, bad in [("eat healthy food", "eat less candy"), ("exercise every day", "stay up late"),
                      ("drink enough water", "drink too much cola"), ("brush your teeth", "eat too much candy")]:
        t.append(S("为了保持健康，你应该：You should ______.", good,
                   [bad, "play computer games all day", "never rest"],
                   "should + 动词原形表示建议：You should %s." % good))
        t.append(B("You shouldn't %s." % good, False,
                   "%s 是好习惯，应该用 should，不该用 shouldn't。" % good))
        t.append(S("—How can I stay healthy?  —______", "You should %s." % good,
                   ["He's hard-working.", "It comes from plants.", "There is a forest."],
                   "给建议用 You should + 动词原形。"))
    for food in ["beef", "dumplings", "tea", "hamburger", "ice cream", "salad", "noodles", "soup", "juice"]:
        t.append(S("—What would you like to eat?  —______", "I'd like some %s." % food,
                   ["I'm worried.", "He can jump rope.", "There are two rivers."],
                   "What would you like ...? 用 I'd like ... 回答。"))
        t.append(S("—Would you like some %s?  —______" % food, "Yes, please.",
                   ["Yes, I can.", "Yes, I am.", "Yes, I do."],
                   "Would you like ...? 的礼貌答语是 Yes, please. / No, thanks."))
    for thing in ["tea", "beef", "milk", "rice", "coconut"]:
        t.append(S("—Where does %s come from?  —______" % thing, "It comes from plants." if thing in ("tea", "rice", "coconut") else "It comes from cows.",
                   ["I come from China.", "They come from school.", "He comes from Australia."],
                   "第三人称单数用 does 提问、comes from 回答。"))
        t.append(B("Where does %s come from? 中的 does 可以换成 do。" % thing, False,
                   "主语是第三人称单数，助动词要用 does。"))
    for place in ["river", "forest", "mountain", "lake", "waterfall", "tree", "hill"]:
        t.append(S("—Is there a %s in the nature park?  —______" % place, "Yes, there is.",
                   ["Yes, there are.", "Yes, it is.", "Yes, I can."],
                   "Is there a ...? 用 Yes, there is. / No, there isn't. 回答。"))
        t.append(T("写出英文：%s" % {"river": "河流", "forest": "森林", "mountain": "高山",
                                   "lake": "湖泊", "waterfall": "瀑布", "tree": "树", "hill": "小山"}[place],
                   [place], "%s = %s。" % (place, {"river": "河流", "forest": "森林", "mountain": "高山",
                                                  "lake": "湖泊", "waterfall": "瀑布", "tree": "树", "hill": "小山"}[place])))
    group("英语", "五上英语·核心句型与语法", t)

    # 综合与主观表达
    t = []
    topics = [
        ("介绍你的一位朋友：他/她是什么样的人，会做什么？", "My friend is clever and helpful. He can play the piano and jump rope.",
         "写出外貌或性格 40 分；写出才能（can）40 分；句子正确 20 分。"),
        ("写一写你的一周：周几有什么课，周末通常做什么？", "I have Chinese and maths on Mondays. I usually play ping-pong on the weekend.",
         "写出星期与课程 40 分；写出周末活动 40 分；语句通顺 20 分。"),
        ("给同学提三条保持健康的建议。", "You should eat healthy food. You should exercise every day. You should brush your teeth twice a day.",
         "三条建议各 30 分；should 用法正确 10 分。"),
        ("模拟点餐：写出你想吃的和想喝的。", "I'd like some beef noodles and a cup of tea.",
         "写出食物 40 分；写出饮品 30 分；I'd like 句型正确 30 分。"),
        ("描述一处自然风景，用上 There is / There are。", "There is a river in the park. There are many tall trees near the river.",
         "There is 30 分；There are 30 分；自然景物词汇 40 分。"),
        ("说说你为什么喜欢某一种食物。", "I like dumplings because they are delicious.",
         "说出食物 40 分；用 because 说明原因 40 分；句子完整 20 分。"),
        ("介绍你的新朋友 Oliver：他来自哪里，有什么特长？", "Oliver is from Australia. He is tall and strong. He can run very fast.",
         "写出来自哪里 30 分；写出外貌性格 30 分；写出特长 40 分。"),
        ("说一说你和好朋友有什么不同。", "I am quiet, but my friend is lively. I can draw pictures and she can play the piano.",
         "写出一处不同 50 分；用 can 写各自特长 50 分。"),
        ("用 be good at 写两句话介绍同学的才艺。", "Chen Jie is good at playing the piano. Binbin is good at making robots.",
         "每句 50 分；be good at 后接动名词用法正确加分。"),
        ("你今天心情怎么样？为什么？", "I am excited because we have a music lesson today.",
         "写出情绪词 40 分；用 because 说明原因 40 分；句子正确 20 分。"),
        ("同学有点难过，你会怎么问、怎么安慰？", "What's the matter? Don't worry. Let's play together.",
         "用 What's the matter? 提问 40 分；给出安慰或建议 60 分。"),
        ("写一写你周三有哪些课、放学后做什么。", "I have Chinese, maths and PE on Wednesdays. I play ping-pong after school.",
         "写出课程 50 分；写出课后活动 50 分。"),
        ("用 usually 和 sometimes 各写一句关于周末的话。", "I usually read books on the weekend. Sometimes I visit my grandparents.",
         "usually 句 50 分；sometimes 句 50 分。"),
        ("写出两条你不该做的不健康习惯。", "You shouldn't stay up late. You shouldn't eat too much candy.",
         "每条建议 50 分；shouldn't 用法正确。"),
        ("感冒了应该怎么办？写两条建议。", "You should see a doctor. You should drink enough water and rest.",
         "每条建议 50 分；should + 动词原形正确。"),
        ("写一写你今天三餐想吃什么。", "I'd like some milk and dumplings for breakfast. I'd like beef noodles for lunch.",
         "写出一餐 50 分；两餐齐全、I'd like 正确 50 分。"),
        ("用 Where does ... come from? 写一组问答。", "Where does tea come from? It comes from plants.",
         "问句用 does 50 分；答句用 comes from 50 分。"),
        ("介绍一种植物的哪一部分可以吃。", "We eat the roots of the lotus. Its seeds are food too.",
         "写出植物部位 50 分；语句正确 50 分。"),
        ("描述你去过的一处自然景点，用上 There is / There are。", "There is a famous mountain in the park. There are many tall trees and a small lake.",
         "There is 30 分；There are 30 分；自然景物词汇 40 分。"),
        ("天气不好去徒步，你会提醒大家带什么？", "It is foggy and rainy. Please bring an umbrella and a raincoat.",
         "写出天气 40 分；写出要带的物品 60 分。"),
        ("用 should / shouldn't 给准备去徒步的同学两条建议。", "You should bring enough water. You shouldn't go hiking in heavy rain.",
         "每条 50 分；should / shouldn't 使用正确。"),
    ]
    for i in range(150):
        q, model, rubric = topics[i % len(topics)]
        t.append(J("（第%d组）%s（写 2—4 句即可）" % (i + 1, q), model, rubric,
                   "先想好要用的句型（can / should / I'd like / There is），再组织句子。", 3))
    group("英语", "五上英语·综合表达", t)

    # 词汇与语法变式：首字母拼写、单元归类、be 动词、复数、三单、情景句型
    t3 = []
    pool_zh = [zh for _, zh, _ in all_words]
    for en, zh, unit in all_words:
        tag = unit.split()[1]
        if " " not in en and len(en) > 1:
            t3.append(T("根据中文和首字母补全单词：%s（%s%s）" % (zh, en[0], "＿" * (len(en) - 1)),
                        [en], "%s = %s，注意拼写。" % (zh, en)))
        t3.append(T("（%s 单元）写出英文：%s" % (tag, zh), [en, en.lower()],
                    "%s 的英文是 %s。" % (zh, en)))
        wrong_zh = [z for z in pool_zh if z != zh][0]
        t3.append(B("在 %s 单元里，%s 的意思是「%s」。" % (tag, en, wrong_zh), False,
                    "%s 的意思是「%s」，不是「%s」。" % (en, zh, wrong_zh)))
    for pron, be in [("I", "am"), ("He", "is"), ("She", "is"), ("We", "are"),
                     ("They", "are"), ("You", "are"), ("It", "is")]:
        for adj in ["lovely", "clever", "young", "happy", "sad", "tired", "excited", "helpful", "quiet"]:
            t3.append(S("%s ______ %s. 选择正确的 be 动词。" % (pron, adj), be,
                        [x for x in ["am", "is", "are", "be"] if x != be],
                        "be 动词随主语变化：I am / he is / they are。"))
    for n in range(2, 11):
        for noun in ["river", "tree", "mountain", "lake", "book", "apple",
                     "flower", "student", "seed", "player"]:
            t3.append(T("用所给名词的适当形式填空：There are %d ______ (%s) in the picture." % (n, noun),
                        [noun + "s"], "数量大于 1 用复数，一般在词尾加 -s：%s。" % (noun + "s")))
    V3 = {"like": "likes", "play": "plays", "do": "does", "go": "goes", "have": "has",
          "make": "makes", "read": "reads", "watch": "watches", "brush": "brushes"}
    for pron in ["He", "She", "My friend", "Oliver"]:
        for v, v3 in V3.items():
            t3.append(S("%s ______ (%s). 主语是第三人称单数，选择正确的动词形式。" % (pron, v), v3,
                        [v, "to " + v, v + "ing"],
                        "第三人称单数动词加 -s/-es，特殊变化：go→goes、have→has、watch→watches。"))
    boys = ["Oliver", "Binbin", "Mike", "Zhang Peng"]
    for name in boys + ["Sarah", "Amy", "Chen Jie"]:
        for act in ["jump rope", "play the piano", "play Chinese chess", "make robots", "dance", "sing"]:
            ans = ("He can %s." if name in boys else "She can %s.") % act
            t3.append(S("—What can %s do?（提示：%s）  —______" % (name, act), ans,
                        ["He's clever.", "She's young.", "I'd like some tea."],
                        "问能力用 can，答语用「主语 + can + 动词原形」。"))
    group("英语", "五上英语·词汇与语法变式", t3)


# ================================================================ 汇总 / 校验 / 输出

def take(subj):
    seen, picked = set(), []
    groups = [(b, list(v)) for b, v in GROUPS[subj]]
    for _, v in groups:
        R.shuffle(v)
    for slot in itertools.zip_longest(*[v for _, v in groups]):
        for gi, x in enumerate(slot):
            if x is None:
                continue
            if x["q"] in seen:
                continue
            seen.add(x["q"])
            x["subject"] = subj
            x["level"] = LEVEL
            x["bank"] = groups[gi][0]
            picked.append(x)
            if len(picked) >= TARGET[subj]:
                return picked
    return picked


def validate(items):
    errs, seen = [], set()
    for i, x in enumerate(items):
        tag = "#%d" % (i + 1)
        q = x.get("q", "")
        if not isinstance(q, str) or not q.strip() or len(q) > 5000:
            errs.append(tag + " 题干为空或过长")
        if "<" in q and ">" in q:
            errs.append(tag + " 题干疑似含 HTML 标签")
        if q in seen:
            errs.append(tag + " 题干重复")
        seen.add(q)
        if x.get("difficulty") not in (1, 2, 3, 4, 5):
            errs.append(tag + " difficulty 越界")
        if not x.get("tip"):
            errs.append(tag + " 缺 tip")
        ty = x.get("type")
        if ty in ("single", "multiple", "boolean"):
            a = x.get("a")
            if not isinstance(a, list) or not (2 <= len(a) <= 8) or any(not str(v).strip() for v in a):
                errs.append(tag + " 选项不合法")
                continue
            if ty == "single":
                if not isinstance(x.get("k"), int) or not (0 <= x["k"] < len(a)):
                    errs.append(tag + " k 越界")
            elif ty == "boolean":
                if a != ["正确", "错误"] or x.get("k") not in (0, 1):
                    errs.append(tag + " boolean 选项或 k 不合法")
            else:
                ci = x.get("correctIndices")
                if not isinstance(ci, list) or len(ci) < 2 or any(not isinstance(j, int) or not (0 <= j < len(a)) for j in ci):
                    errs.append(tag + " correctIndices 不合法")
        elif ty == "text":
            ans = x.get("answers")
            if not isinstance(ans, list) or not ans or any(not str(v).strip() for v in ans):
                errs.append(tag + " answers 不合法")
        elif ty == "subjective":
            if not x.get("modelAnswer") or not x.get("rubric"):
                errs.append(tag + " 主观题缺 modelAnswer/rubric")
        else:
            errs.append(tag + " 未知题型")
    return errs


def main():
    gen_math()
    gen_chinese()
    gen_english()
    all_items = []
    for subj in ("数学", "语文", "英语"):
        picked = take(subj)
        print("%s：候选 %d，取 %d" % (subj, sum(len(v) for _, v in GROUPS[subj]), len(picked)))
        all_items.extend(picked)
    errs = validate(all_items)
    if errs:
        print("校验失败 %d 条，前 10 条：" % len(errs))
        for e in errs[:10]:
            print("  ", e)
        raise SystemExit(1)
    if len(all_items) != sum(TARGET.values()):
        print("题数不足：", len(all_items))
        raise SystemExit(1)

    out = os.path.dirname(os.path.abspath(__file__))
    files = {}
    files[os.path.join(out, "五年级上-语数外-4000题（人教版2026秋新教材）.json")] = all_items
    for subj, fname in [("数学", "五年级上-数学-1400题.json"),
                        ("语文", "五年级上-语文-1300题.json"),
                        ("英语", "五年级上-英语-1300题.json")]:
        files[os.path.join(out, fname)] = [x for x in all_items if x["subject"] == subj]
    for path, data in files.items():
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"version": 2, "items": data}, f, ensure_ascii=False, indent=None)
        print("写出 %s：%d 题，%.2f MB" % (os.path.basename(path), len(data), os.path.getsize(path) / 1048576))

    from collections import Counter
    print("题型：", dict(Counter(x["type"] for x in all_items)))
    print("难度：", dict(sorted(Counter(x["difficulty"] for x in all_items).items())))
    print("题库数：", len(set(x["bank"] for x in all_items)))
    print("校验：全部通过，题干唯一，格式合法。")


if __name__ == "__main__":
    main()
