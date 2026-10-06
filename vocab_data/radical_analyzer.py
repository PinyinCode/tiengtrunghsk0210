# -*- coding: utf-8 -*-
r"""
radical_analyzer.py
Phân tích bộ thủ của chữ Hán.

Cung cấp:
    get_radical_for_word(zh) -> dict | None
        Trả về {"zh", "pinyin", "meaning", "base_zh"?} cho chữ Hán.
"""

import re
from vocab_data.radicals_db import (
    RADICALS,
    SIMPLIFIED_VARIANTS,
    VARIANT_MEANINGS,
    get_radical_info,
)


# ═══════════════════════════════════════════════════════════════
#  UNICODE NORMALIZATION — Convert Kangxi Radical về CJK
# ═══════════════════════════════════════════════════════════════
# Một số mnemonic cũ dùng Kangxi Radical (U+2F00-2FDF) thay vì
# CJK Ideograph (U+4E00-9FFF). Cần normalize về CJK để so sánh.
KANGXI_TO_CJK = {
    0x2F00: 0x4E00,  # ⼀ → 一
    0x2F01: 0x4E28,  # ⼁ → 丨
    0x2F02: 0x4E36,  # ⼂ → 丶
    0x2F03: 0x4E3F,  # ⼃ → 丿
    0x2F04: 0x4E59,  # ⼄ → 乙
    0x2F05: 0x4E85,  # ⼅ → 亅
    0x2F06: 0x4E8C,  # ⼆ → 二
    0x2F07: 0x4EA0,  # ⼇ → 亠
    0x2F08: 0x4EBA,  # ⼈ → 人
    0x2F09: 0x513F,  # ⼉ → 儿
    0x2F0A: 0x5165,  # ⼊ → 入
    0x2F0B: 0x516B,  # ⼋ → 八
    0x2F0C: 0x5182,  # ⼌ → 冂
    0x2F0D: 0x5196,  # ⼍ → 冖
    0x2F0E: 0x51AB,  # ⼎ → 冫
    0x2F0F: 0x51E0,  # ⼏ → 几
    0x2F10: 0x51F5,  # ⼐ → 凵
    0x2F11: 0x5200,  # ⼑ → 刀
    0x2F12: 0x529B,  # ⼒ → 力
    0x2F13: 0x52F9,  # ⼓ → 勹
    0x2F14: 0x5315,  # ⼔ → 匕
    0x2F15: 0x531A,  # ⼕ → 匚
    0x2F16: 0x5338,  # ⼖ → 匸
    0x2F17: 0x5341,  # ⼗ → 十   ← QUAN TRỌNG
    0x2F18: 0x535C,  # ⼘ → 卜
    0x2F19: 0x5369,  # ⼙ → 卩
    0x2F1A: 0x5382,  # ⼚ → 厂
    0x2F1B: 0x53B6,  # ⼛ → 厶
    0x2F1C: 0x53C8,  # ⼜ → 又
    0x2F1D: 0x53E3,  # ⼝ → 口
    0x2F1E: 0x56D7,  # ⼞ → 囗
    0x2F1F: 0x571F,  # ⼟ → 土
    0x2F20: 0x58EB,  # ⼠ → 士
    0x2F21: 0x5902,  # ⼡ → 夂
    0x2F22: 0x590A,  # ⼢ → 夊
    0x2F23: 0x5915,  # ⼣ → 夕
    0x2F24: 0x5927,  # ⼤ → 大
    0x2F25: 0x5973,  # ⼥ → 女
    0x2F26: 0x5B50,  # ⼦ → 子
    0x2F27: 0x5B80,  # ⼧ → 宀
    0x2F28: 0x5BF8,  # ⼨ → 寸
    0x2F29: 0x5C0F,  # ⼩ → 小
    0x2F2A: 0x5C22,  # ⼪ → 尢
    0x2F2B: 0x5C38,  # ⼫ → 尸
    0x2F2C: 0x5C6E,  # ⼬ → 屮
    0x2F2D: 0x5C71,  # ⼭ → 山
    0x2F2E: 0x5DDB,  # ⼮ → 巛
    0x2F2F: 0x5DE5,  # ⼯ → 工
    0x2F30: 0x5DF1,  # ⼰ → 己
    0x2F31: 0x5DFE,  # ⼱ → 巾
    0x2F32: 0x5E72,  # ⼲ → 干
    0x2F33: 0x5E7A,  # ⼳ → 幺
    0x2F34: 0x5E7F,  # ⼴ → 广
    0x2F35: 0x5EF4,  # ⼵ → 廴
    0x2F36: 0x5EFE,  # ⼶ → 廾
    0x2F37: 0x5F0B,  # ⼷ → 弋
    0x2F38: 0x5F13,  # ⼸ → 弓
    0x2F39: 0x5F50,  # ⼹ → 彐
    0x2F3A: 0x5F61,  # ⼺ → 彡
    0x2F3B: 0x5F73,  # ⼻ → 彳
    0x2F3C: 0x5FC3,  # ⼼ → 心
    0x2F3D: 0x6208,  # ⼽ → 戈
    0x2F3E: 0x6236,  # ⼾ → 戶
    0x2F3F: 0x624B,  # ⼿ → 手
    0x2F40: 0x652F,  # ⽀ → 支
    0x2F41: 0x6534,  # ⽁ → 攴
    0x2F42: 0x6587,  # ⽂ → 文
    0x2F43: 0x6597,  # ⽃ → 斗
    0x2F44: 0x65A4,  # ⽄ → 斤
    0x2F45: 0x65B9,  # ⽅ → 方
    0x2F46: 0x65E0,  # ⽆ → 无
    0x2F47: 0x65E5,  # ⽇ → 日
    0x2F48: 0x66F0,  # ⽈ → 曰
    0x2F49: 0x6708,  # ⽉ → 月
    0x2F4A: 0x6728,  # ⽊ → 木
    0x2F4B: 0x6B20,  # ⽋ → 欠
    0x2F4C: 0x6B62,  # ⽌ → 止
    0x2F4D: 0x6B79,  # ⽍ → 歹
    0x2F4E: 0x6BB3,  # ⽎ → 殳
    0x2F4F: 0x6BCB,  # ⽏ → 毋
    0x2F50: 0x6BD4,  # ⽐ → 比
    0x2F51: 0x6BDB,  # ⽑ → 毛
    0x2F52: 0x6C0F,  # ⽒ → 氏
    0x2F53: 0x6C14,  # ⽓ → 气
    0x2F54: 0x6C34,  # ⽔ → 水
    0x2F55: 0x706B,  # ⽕ → 火
    0x2F56: 0x722A,  # ⽖ → 爪
    0x2F57: 0x7236,  # ⽗ → 父
    0x2F58: 0x723B,  # ⽘ → 爻
    0x2F59: 0x723F,  # ⽙ → 爿
    0x2F5A: 0x7247,  # ⽚ → 片
    0x2F5B: 0x7259,  # ⽛ → 牙
    0x2F5C: 0x725B,  # ⽜ → 牛
    0x2F5D: 0x72AC,  # ⽝ → 犬
    0x2F5E: 0x7384,  # ⽞ → 玄
    0x2F5F: 0x7389,  # ⽟ → 玉
    0x2F60: 0x74DC,  # ⽠ → 瓜
    0x2F61: 0x74E6,  # ⽡ → 瓦
    0x2F62: 0x7518,  # ⽢ → 甘
    0x2F63: 0x751F,  # ⽣ → 生
    0x2F64: 0x7528,  # ⽤ → 用
    0x2F65: 0x7530,  # ⽥ → 田
    0x2F66: 0x758B,  # ⽦ → 疋
    0x2F67: 0x7592,  # ⽧ → 疒
    0x2F68: 0x7676,  # ⽨ → 癶
    0x2F69: 0x767D,  # ⽩ → 白
    0x2F6A: 0x76AE,  # ⽪ → 皮
    0x2F6B: 0x76BF,  # ⽫ → 皿
    0x2F6C: 0x76EE,  # ⽬ → 目
    0x2F6D: 0x77DB,  # ⽭ → 矛
    0x2F6E: 0x77E2,  # ⽮ → 矢
    0x2F6F: 0x77F3,  # ⽯ → 石
    0x2F70: 0x793A,  # ⽰ → 示
    0x2F71: 0x79B8,  # ⽱ → 禸
    0x2F72: 0x79BE,  # ⽲ → 禾
    0x2F73: 0x7A74,  # ⽳ → 穴
    0x2F74: 0x7ACB,  # ⽴ → 立
    0x2F75: 0x7AF9,  # ⽵ → 竹
    0x2F76: 0x7C73,  # ⽶ → 米
    0x2F77: 0x7CF8,  # ⽷ → 糸
    0x2F78: 0x7F36,  # ⽸ → 缶
    0x2F79: 0x7F51,  # ⽹ → 网
    0x2F7A: 0x7F8A,  # ⽺ → 羊
    0x2F7B: 0x7FBD,  # ⽻ → 羽
    0x2F7C: 0x8001,  # ⽼ → 老
    0x2F7D: 0x800C,  # ⽽ → 而
    0x2F7E: 0x8012,  # ⽾ → 耒
    0x2F7F: 0x8033,  # ⽿ → 耳
    0x2F80: 0x807F,  # ⾀ → 聿
    0x2F81: 0x8089,  # ⾁ → 肉
    0x2F82: 0x81E3,  # ⾂ → 臣
    0x2F83: 0x81EA,  # ⾃ → 自
    0x2F84: 0x81F3,  # ⾄ → 至
    0x2F85: 0x81FC,  # ⾅ → 臼
    0x2F86: 0x820C,  # ⾆ → 舌
    0x2F87: 0x821B,  # ⾇ → 舛
    0x2F88: 0x821F,  # ⾈ → 舟
    0x2F89: 0x826E,  # ⾉ → 艮
    0x2F8A: 0x8272,  # ⾊ → 色
    0x2F8B: 0x8278,  # ⾋ → 艸
    0x2F8C: 0x864D,  # ⾌ → 虍
    0x2F8D: 0x866B,  # ⾍ → 虫
    0x2F8E: 0x8840,  # ⾎ → 血
    0x2F8F: 0x884C,  # ⾏ → 行
    0x2F90: 0x8863,  # ⾐ → 衣
    0x2F91: 0x897E,  # ⾑ → 襾
    0x2F92: 0x898B,  # ⾒ → 見
    0x2F93: 0x89D2,  # ⾓ → 角
    0x2F94: 0x8A00,  # ⾔ → 言
    0x2F95: 0x8C37,  # ⾕ → 谷
    0x2F96: 0x8C46,  # ⾖ → 豆
    0x2F97: 0x8C55,  # ⾗ → 豕
    0x2F98: 0x8C78,  # ⾘ → 豸
    0x2F99: 0x8C9D,  # ⾙ → 貝
    0x2F9A: 0x8D64,  # ⾚ → 赤
    0x2F9B: 0x8D70,  # ⾛ → 走
    0x2F9C: 0x8DB3,  # ⾜ → 足
    0x2F9D: 0x8EAB,  # ⾝ → 身
    0x2F9E: 0x8ECA,  # ⾞ → 車
    0x2F9F: 0x8F9B,  # ⾟ → 辛
    0x2FA0: 0x8FB0,  # ⾠ → 辰
    0x2FA1: 0x8FB5,  # ⾡ → 辵
    0x2FA2: 0x9091,  # ⾢ → 邑
    0x2FA3: 0x9149,  # ⾣ → 酉
    0x2FA4: 0x91C6,  # ⾤ → 釆
    0x2FA5: 0x91CC,  # ⾥ → 里
    0x2FA6: 0x91D1,  # ⾦ → 金
    0x2FA7: 0x9577,  # ⾧ → 長
    0x2FA8: 0x9580,  # ⾨ → 門
    0x2FA9: 0x961C,  # ⾩ → 阜
    0x2FAA: 0x96B6,  # ⾪ → 隶
    0x2FAB: 0x96B9,  # ⾫ → 隹
    0x2FAC: 0x96E8,  # ⾬ → 雨
    0x2FAD: 0x9751,  # ⾭ → 青
    0x2FAE: 0x975E,  # ⾮ → 非
    0x2FAF: 0x9762,  # ⾯ → 面
    0x2FB0: 0x9769,  # ⾰ → 革
    0x2FB1: 0x97CB,  # ⾱ → 韋
    0x2FB2: 0x97ED,  # ⾲ → 韭
    0x2FB3: 0x97F3,  # ⾳ → 音
    0x2FB4: 0x9801,  # ⾴ → 頁
    0x2FB5: 0x98A8,  # ⾵ → 風
    0x2FB6: 0x98DB,  # ⾶ → 飛
    0x2FB7: 0x98DF,  # ⾷ → 食
    0x2FB8: 0x9996,  # ⾸ → 首
    0x2FB9: 0x9999,  # ⾹ → 香
    0x2FBA: 0x99AC,  # ⾺ → 馬
    0x2FBB: 0x9AA8,  # ⾻ → 骨
    0x2FBC: 0x9AD8,  # ⾼ → 高
    0x2FBD: 0x9ADF,  # ⾽ → 髟
    0x2FBE: 0x9B25,  # ⾾ → 鬥
    0x2FBF: 0x9B2F,  # ⾿ → 鬯
    0x2FC0: 0x9B32,  # ⿀ → 鬲
    0x2FC1: 0x9B3C,  # ⿁ → 鬼
    0x2FC2: 0x9B5A,  # ⿂ → 魚
    0x2FC3: 0x9CE5,  # ⿃ → 鳥
    0x2FC4: 0x9E75,  # ⿄ → 鹵
    0x2FC5: 0x9E7F,  # ⿅ → 鹿
    0x2FC6: 0x9EA5,  # ⿆ → 麥
    0x2FC7: 0x9EBB,  # ⿇ → 麻
    0x2FC8: 0x9EC3,  # ⿈ → 黃
    0x2FC9: 0x9ECD,  # ⿉ → 黍
    0x2FCA: 0x9ED1,  # ⿊ → 黑
    0x2FCB: 0x9EF9,  # ⿋ → 黹
    0x2FCC: 0x9EFD,  # ⿌ → 黽
    0x2FCD: 0x9F0E,  # ⿍ → 鼎
    0x2FCE: 0x9F13,  # ⿎ → 鼓
    0x2FCF: 0x9F20,  # ⿏ → 鼠
    0x2FD0: 0x9F3B,  # ⿐ → 鼻
    0x2FD1: 0x9F4A,  # ⿑ → 齊
    0x2FD2: 0x9F52,  # ⿒ → 齒
    0x2FD3: 0x9F8D,  # ⿓ → 龍
    0x2FD4: 0x9F9C,  # ⿔ → 龜
    0x2FD5: 0x9FA0,  # ⿕ → 龠
}


def normalize_kangxi(text):
    """Convert Kangxi Radicals (U+2F00-2FDF) về CJK Ideograph (U+4E00-9FFF)."""
    if not text:
        return text
    result = []
    for ch in text:
        cp = ord(ch)
        if 0x2F00 <= cp <= 0x2FDF and cp in KANGXI_TO_CJK:
            result.append(chr(KANGXI_TO_CJK[cp]))
        else:
            result.append(ch)
    return ''.join(result)


# ═══════════════════════════════════════════════════════════════
#  CÁC BIẾN THỂ THƯỜNG GẶP Ở CÁC VỊ TRÍ
# ═══════════════════════════════════════════════════════════════
# Mapping: vị trí trong chữ -> bộ thủ biến thể thường xuất hiện
POSITION_VARIANTS = {
    "left": {   # bên trái
        "氵": "水", "忄": "心", "扌": "手", "讠": "言", "钅": "金",
        "饣": "食", "纟": "糸", "犭": "犬", "艹": "艸", "亻": "人",
        "刂": "刀", "⺮": "竹", "⻊": "足", "⺼": "肉", "⻖": "阜",
    },
    "top": {    # bên trên
        "⺮": "竹", "艹": "艸", "爫": "爪", "罒": "网", "⻗": "雨",
    },
    "bottom": { # bên dưới
        "灬": "火", "⺼": "肉", "心": "心",
    },
    "right": {  # bên phải
        "⻏": "邑", "刂": "刀", "欠": "欠",
    },
}


def get_radical_for_word(zh):
    """
    Tra bộ thủ của chữ Hán (1-2 ký tự).
    Trả về dict {"zh", "pinyin", "meaning", "base_zh"?} hoặc None.
    """
    if not zh:
        return None

    # Normalize Kangxi → CJK trước
    zh_norm = normalize_kangxi(zh.strip())

    # Chỉ hỗ trợ chữ đơn
    if len(zh_norm) == 0:
        return None

    # Nếu là chữ đơn → tra trực tiếp
    if len(zh_norm) == 1:
        return _find_radical_for_char(zh_norm)

    # Nếu là chữ ghép (2+ ký tự) → thử decompose
    return _find_radical_for_compound(zh_norm)


def _find_radical_for_char(ch):
    """Tra bộ thủ cho 1 chữ Hán đơn."""
    # 1. Nếu chính chữ đó là bộ thủ → trả về luôn
    info = get_radical_info(ch)
    if info:
        return {
            "zh": info.get("zh", ch),
            "pinyin": info.get("pinyin", ""),
            "meaning": info.get("meaning", ""),
            "base_zh": info.get("base_zh", ""),
        }

    # 2. Nếu chữ là biến thể giản thể của bộ thủ
    if ch in SIMPLIFIED_VARIANTS:
        base = SIMPLIFIED_VARIANTS[ch]
        base_info = get_radical_info(base)
        if base_info:
            return {
                "zh": ch,
                "base_zh": base,
                "pinyin": base_info.get("pinyin", ""),
                "meaning": VARIANT_MEANINGS.get(ch, base_info.get("meaning", "")),
            }

    # 3. Decompose chữ thành các thành phần
    components = _decompose(ch)
    for comp in components:
        # Bỏ qua nét đơn (一 丨 丶 丿 乙 亅)
        if comp in "一丨丶丿乙亅":
            continue
        # Nếu component là biến thể
        if comp in SIMPLIFIED_VARIANTS:
            base = SIMPLIFIED_VARIANTS[comp]
            base_info = get_radical_info(base)
            if base_info:
                return {
                    "zh": comp,
                    "base_zh": base,
                    "pinyin": base_info.get("pinyin", ""),
                    "meaning": VARIANT_MEANINGS.get(comp, base_info.get("meaning", "")),
                }
        # Nếu component là bộ thủ
        if comp in RADICALS:
            pinyin, strokes, meaning = RADICALS[comp]
            return {
                "zh": comp,
                "pinyin": pinyin,
                "meaning": meaning,
            }

    return None


def _find_radical_for_compound(zh):
    """Chữ ghép: lấy bộ thủ của ký tự đầu tiên có bộ thủ."""
    for ch in zh:
        rad = _find_radical_for_char(ch)
        if rad:
            return rad
    return None


# ═══════════════════════════════════════════════════════════════
#  DECOMPOSE CHỮ HÁN
# ═══════════════════════════════════════════════════════════════
# Decompose dựa trên radical + các nét còn lại
# Đây là logic đơn giản, không dùng bảng decompose đầy đủ

# Các bộ thủ phổ biến và vị trí thường gặp
# Format: { char: [(component, position), ...] }
DECOMPOSE_DB = {
    # ═══ 1 nét ═══
    "一": [("一", "all")],
    "丨": [("丨", "all")],
    "丶": [("丶", "all")],
    "丿": [("丿", "all")],
    "乙": [("乙", "all")],
    "亅": [("亅", "all")],

    # ═══ 2 nét ═══
    "二": [("二", "all")],
    "十": [("十", "all")],
    "丁": [("一", "top"), ("亅", "bottom")],
    "厂": [("厂", "all")],
    "七": [("一", "top"), ("乚", "bottom")],
    "卜": [("卜", "all")],
    "八": [("八", "all")],
    "人": [("人", "all")],
    "入": [("入", "all")],
    "儿": [("儿", "all")],
    "几": [("几", "all")],
    "九": [("丿", "left"), ("乙", "right")],
    "刀": [("刀", "all")],
    "力": [("力", "all")],
    "又": [("又", "all")],
    "三": [("一", "all")],

    # ═══ 3 nét ═══
    "口": [("口", "all")],
    "土": [("土", "all")],
    "士": [("士", "all")],
    "大": [("大", "all")],
    "女": [("女", "all")],
    "子": [("子", "all")],
    "寸": [("寸", "all")],
    "小": [("小", "all")],
    "山": [("山", "all")],
    "工": [("工", "all")],
    "己": [("己", "all")],
    "巾": [("巾", "all")],
    "干": [("干", "all")],
    "广": [("广", "all")],
    "弓": [("弓", "all")],
    "也": [("乙", "left"), ("丨", "right")],
    "飞": [("飞", "all")],
    "马": [("马", "all")],

    # ═══ 4 nét ═══
    "心": [("心", "all")],
    "戈": [("戈", "all")],
    "手": [("手", "all")],
    "文": [("文", "all")],
    "斗": [("斗", "all")],
    "斤": [("斤", "all")],
    "方": [("方", "all")],
    "无": [("无", "all")],
    "日": [("日", "all")],
    "月": [("月", "all")],
    "木": [("木", "all")],
    "欠": [("欠", "all")],
    "止": [("止", "all")],
    "比": [("比", "all")],
    "毛": [("毛", "all")],
    "气": [("气", "all")],
    "水": [("水", "all")],
    "火": [("火", "all")],
    "爪": [("爪", "all")],
    "父": [("父", "all")],
    "片": [("片", "all")],
    "牙": [("牙", "all")],
    "牛": [("牛", "all")],
    "犬": [("犬", "all")],
    "王": [("王", "all")],

    # ═══ 5 nét ═══
    "玉": [("玉", "all")],
    "瓜": [("瓜", "all")],
    "瓦": [("瓦", "all")],
    "甘": [("甘", "all")],
    "生": [("生", "all")],
    "用": [("用", "all")],
    "田": [("田", "all")],
    "白": [("白", "all")],
    "皮": [("皮", "all")],
    "皿": [("皿", "all")],
    "目": [("目", "all")],
    "矛": [("矛", "all")],
    "矢": [("矢", "all")],
    "石": [("石", "all")],
    "示": [("示", "all")],
    "禾": [("禾", "all")],
    "穴": [("穴", "all")],
    "立": [("立", "all")],

    # ═══ 6 nét ═══
    "竹": [("竹", "all")],
    "米": [("米", "all")],
    "糸": [("糸", "all")],
    "羊": [("羊", "all")],
    "羽": [("羽", "all")],
    "老": [("老", "all")],
    "耳": [("耳", "all")],
    "肉": [("肉", "all")],
    "自": [("自", "all")],
    "至": [("至", "all")],
    "舌": [("舌", "all")],
    "舟": [("舟", "all")],
    "色": [("色", "all")],
    "虫": [("虫", "all")],
    "血": [("血", "all")],
    "行": [("行", "all")],
    "衣": [("衣", "all")],
    "西": [("西", "all")],
    "而": [("而", "all")],
    "页": [("页", "all")],
    "齐": [("齐", "all")],

    # ═══ 7+ nét ═══
    "見": [("見", "all")],
    "见": [("见", "all")],
    "角": [("角", "all")],
    "言": [("言", "all")],
    "讠": [("讠", "left")],
    "谷": [("谷", "all")],
    "豆": [("豆", "all")],
    "豕": [("豕", "all")],
    "贝": [("贝", "all")],
    "貝": [("貝", "all")],
    "赤": [("赤", "all")],
    "走": [("走", "all")],
    "足": [("足", "all")],
    "身": [("身", "all")],
    "车": [("车", "all")],
    "車": [("車", "all")],
    "辛": [("辛", "all")],
    "金": [("金", "all")],
    "钅": [("钅", "left")],
    "长": [("长", "all")],
    "門": [("門", "all")],
    "门": [("门", "all")],
    "隶": [("隶", "all")],
    "隹": [("隹", "all")],
    "雨": [("雨", "all")],
    "青": [("青", "all")],
    "非": [("非", "all")],
    "面": [("面", "all")],
    "革": [("革", "all")],
    "音": [("音", "all")],
    "风": [("风", "all")],
    "風": [("風", "all")],
    "飞": [("飞", "all")],
    "食": [("食", "all")],
    "饣": [("饣", "left")],
    "首": [("首", "all")],
    "香": [("香", "all")],
    "马": [("马", "all")],
    "馬": [("馬", "all")],
    "骨": [("骨", "all")],
    "高": [("高", "all")],
    "鱼": [("鱼", "all")],
    "魚": [("魚", "all")],
    "鸟": [("鸟", "all")],
    "鳥": [("鳥", "all")],
    "鹿": [("鹿", "all")],
    "麦": [("麦", "all")],
    "麻": [("麻", "all")],
    "黄": [("黄", "all")],
    "黑": [("黑", "all")],
    "鼓": [("鼓", "all")],
    "鼠": [("鼠", "all")],
    "鼻": [("鼻", "all")],
    "齐": [("齐", "all")],
    "龙": [("龙", "all")],
    "龍": [("龍", "all")],
    "龟": [("龟", "all")],
    "龜": [("龜", "all")],

    # ═══ HSK1 phổ biến ═══
    "半": [("八", "top"), ("十", "bottom")],
    "的": [("白", "left"), ("勺", "right")],
    "读": [("讠", "left"), ("卖", "right")],
    "对": [("又", "left"), ("寸", "right")],
    "多": [("夕", "top"), ("夕", "bottom")],
    "分": [("八", "top"), ("刀", "bottom")],
    "歌": [("哥", "left"), ("欠", "right")],
    "关": [("八", "top"), ("天", "bottom")],
    "国": [("囗", "around"), ("玉", "inside")],
    "很": [("彳", "left"), ("艮", "right")],
    "话": [("讠", "left"), ("舌", "right")],
    "会": [("人", "top"), ("云", "bottom")],
    "记": [("讠", "left"), ("己", "right")],
    "间": [("门", "around"), ("日", "inside")],
    "开": [("一", "top"), ("廾", "bottom")],
    "来": [("木", "top"), ("一", "bottom")],
    "哪": [("口", "left"), ("那", "right")],
    "那": [("月", "left"), ("阝", "right")],
    "能": [("月", "left"), ("匕", "bottom")],
}


def _decompose(ch):
    """
    Decompose chữ Hán thành các components.
    Trả về list các components theo thứ tự ưu tiên bộ thủ.
    """
    if ch in DECOMPOSE_DB:
        return [comp for comp, _ in DECOMPOSE_DB[ch]]

    # Fallback: trả về chính nó (coi là bộ thủ)
    return [ch]
