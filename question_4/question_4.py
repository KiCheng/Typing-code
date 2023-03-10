# A F 按键失灵
# Q W E R S D 按键寿命只有其他的70%

import numpy as np
import os
import math
import re
import argparse
from io import StringIO
from io import open
import matplotlib.pyplot as plt
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from xpinyin import Pinyin

parser = argparse.ArgumentParser(description='Generate a keyboard heatmap from a PDF file.')
parser.add_argument('input_filename', metavar='input_file', type=str,
                    help='the name of the file to process')
parser.add_argument('output_filename', metavar='output_file', type=str,
                    help='the name of the image file to output')
args = parser.parse_args()

# 声母 23  缺 A E O，注意 "f": "E"
initials_dict = {
    "b": "B", "c": "C", "d": "D", "f": "E", "g": "G", "h": "H", "j": "J", "k": "K", "l": "L", "m": "M",
    "n": "N", "p": "P", "q": "Q", "r": "R", "s": "S", "t": "T", "w": "W", "x": "X", "y": "Y", "z": "Z",
    "ch": "I", "sh": "U", "zh": "V"
}

# 零声母--规则：'O'+ 'X'(对应的韵母)
others_dict = {
    "a": "OS","ai": "OD","an": "OH","ang": "OL","ao": "OG","e": "OT","ei": "OE","en": "OI","eng": "OM","er": "ER",
    "o": "OV","ou": "OY"
}


# 1、 最优设计方案 : 2.003  0.675  0.019
# 韵母 24 没有 A F
finals_dict = {
               "i": "B",
    "u": "C", "ai": "D",
    "ei": "E",
    "ao": "G",  "an": "H",
    "en": "I", "in": "J",
    "un": "K", "ang": "L",
    "eng": "M", "ing": "N",
    "uan": "O", "iao": "P",
     "ian": "Q",

    "ui":"R",
    "a": "S", "e": "T",
    "v": "U", "o": "V",
    "iu": "W", "ie": "X",
    "ou":"Y", "ve": "Z"
}
# 重用韵母 8组
reuse_dict = {
    "iang": "ui",
    "ue": "a",
    "iong": "e",
    "ua": "v",
    "uai": "iu",

    "uo": "o",
    "ia": "ou",
    "ong": "ve"
}

"""
# 2、 一般情况 ： 2.056  0.656  0.020
# 韵母 24 没有 A F
finals_dict = {
               "a": "B",
    "e": "C", "i": "D",
    "u": "E",
    "v": "G",  "ai": "H",
    "ao": "I", "iu": "J",
    "an": "K", "en": "L",
    "in": "M", "un": "N",
    "ang": "O", "eng": "P",
     "ing": "Q", "uan":"R",

    "ei": "S", "ui": "T",
    "ie": "U", "ua": "V",
    "ian": "W", "o": "X",
    "ou":"Y", "ve": "Z"
}
# 重用韵母 8组
reuse_dict = {
    "ue": "ei",
    "iong": "ui",
    "uai": "ie",
    "iang": "ua",
    "uang": "ian",

    "uo": "o",
    "ia": "ou",
    "ong": "ve"
}
"""

reuse_dict_reverse = {v:k for k,v in reuse_dict.items()}

# 无间隙的原始拼音
file_text_nospace = './Data/quanpin_01.txt'
# 空格分隔的原始拼音
file_text_separated = './Data/quanpin_02.txt'
# 无间隙分隔的重编码拼音
file_text_encode_nospace = './Data/text_encode_01.txt'
# 空格分隔的重编码拼音
file_text_encode = './Data/text_encode_02.txt'

file_answer = 'answer_4.txt'

# 从 PDF 读取中文字符文本数据
def read_pdf(pdf):
    # 资源管理器配置
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()

    # 文本转换工具
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    process_pdf(rsrcmgr, device, pdf)
    device.close()
    content = retstr.getvalue()
    retstr.close()

    # 获取内容并提取汉字
    lines = str(content)
    chinese = ''.join(re.findall('[\u4e00-\u9fef]', lines))

    return chinese

phrase_in = {}
phrase_fi = {}
# 统计声母、韵母26种情况--对应26个按键按键次数
def re_count(org):
    tmp = org

    # 替换重用韵母
    for key, value in reuse_dict.items():
        tmp = tmp.replace(key + ' ', value + ' ')

    # 替换零声母
    for key, value in others_dict.items():
        tmp = tmp.replace(' ' + key + ' ', ' ' + value + ' ')

    # 统计韵母频次，从长到短，统计后替换以免多次计算
    for key, value in finals_dict.items():
        if len(key) == 4:
            phrase_fi[key] = tmp.count(key)
            tmp = tmp.replace(key + ' ', '  ')
    for key, value in finals_dict.items():
        if len(key) == 3:
            phrase_fi[key] = tmp.count(key)
            tmp = tmp.replace(key + ' ', '  ')
    for key, value in finals_dict.items():
        if len(key) == 2:
            phrase_fi[key] = tmp.count(key)
            tmp = tmp.replace(key + ' ', '  ')
    for key, value in finals_dict.items():
        if len(key) == 1:
            phrase_fi[key] = tmp.count(key)

    # 统计声母频次，从长到短，统计后替换以免多次计算
    for key,value in initials_dict.items():
        if len(key) == 2:
            phrase_in[key] = tmp.count(key)
            tmp = tmp.replace(' ' + key, '  ')
    for key,value in initials_dict.items():
        if len(key) == 1:
            phrase_in[key] = tmp.count(key)
            tmp = tmp.replace(' ' + key, '  ')

# 重编码
def re_encode(org, list_in, list_fi):
    res = org
    tmp = {}
    print("=========重用韵母(8)===========")
    # 替换重用介母韵母
    for key, value in reuse_dict.items():
        res = res.replace(key + ' ', value + ' ')
        print('"' + value + '"---"' + key + '"')
    print("==========零声母(12)===========")
    # 替换零声母拼音
    for key, value in others_dict.items():
        res = res.replace(' ' + key + ' ', ' ' + value + ' ')
        print(value + ' 代表: ' + key)
    print("==========声母代表(23)============")
    # 固定替换声母
    # for key, value in list_in:
    for key,value in list_in:
        if len(key) == 2:
            res = res.replace(' ' + key, ' ' + initials_dict[key])
            print(initials_dict[key] + ' 代表: ' + key)

    # for key, value in list_in:
    for key,value in list_in:
        if len(key) == 1:
            res = res.replace(' ' + key, ' ' + initials_dict[key])
            print(initials_dict[key] + ' 代表: ' + key)
    print('O 代表: ' + '-'.lower())

    print("===========【韵母分配】=============")
    # list_in 声母: len 23
    for i in range(len(list_in)):
        tmp[i] = initials_dict[list_in[i][0]]
    tmp[23] = 'O'

    # 韵母从大到小 组合 声母从小到大
    for i in range(len(list_fi)):
        if len(list_fi[i][0]) == 4:
            res = res.replace(list_fi[i][0] + ' ', tmp[i] + ' ')
            if list_fi[i][0] in reuse_dict_reverse:
                print(tmp[i] + ' 代表: ' + list_fi[i][0] + ' \ ' + reuse_dict_reverse[list_fi[i][0]])
            else:
                print(tmp[i] + ' 代表: ' + list_fi[i][0])
    for i in range(len(list_fi)):
        if len(list_fi[i][0]) == 3:
            res = res.replace(list_fi[i][0] + ' ', tmp[i] + ' ')
            if list_fi[i][0] in reuse_dict_reverse:
                print(tmp[i] + ' 代表: ' + list_fi[i][0] + ' \ ' + reuse_dict_reverse[list_fi[i][0]])
            else:
                print(tmp[i] + ' 代表: ' + list_fi[i][0])
    for i in range(len(list_fi)):
        if len(list_fi[i][0]) == 2:
            res = res.replace(list_fi[i][0] + ' ', tmp[i] + ' ')
            if list_fi[i][0] in reuse_dict_reverse:
                """
                if reuse_dict_reverse[list_fi[i][0]] == 'ue':
                    print(tmp[i] + ' 代表: ' + list_fi[i][0] + ' \ ' + reuse_dict_reverse[list_fi[i][0]]   #  修改
                          + ' \ ian')
                else:
                    print(tmp[i] + ' 代表: ' + list_fi[i][0] + ' \ ' + reuse_dict_reverse[list_fi[i][0]])
                """
            else:
                print(tmp[i] + ' 代表: ' + list_fi[i][0])
    for i in range(len(list_fi)):
        if len(list_fi[i][0]) == 1:
            res = res.replace(list_fi[i][0] + ' ', tmp[i] + ' ')
            if list_fi[i][0] in reuse_dict_reverse:
                if reuse_dict_reverse[list_fi[i][0]] == 'ue':
                    print(tmp[i] + ' 代表: ' + list_fi[i][0] + ' \ ' + reuse_dict_reverse[list_fi[i][0]]  #  修改
                    + ' \ uang')
                else:
                    print(tmp[i] + ' 代表: ' + list_fi[i][0] + ' \ ' + reuse_dict_reverse[list_fi[i][0]])
            else:
                print(tmp[i] + ' 代表: ' + list_fi[i][0])
                
    res = res.lower()

    return res

def main():
    # 解析参数
    file_input = args.input_filename
    if file_input is None:
        parser.error('Please specify the filename of the PDF file to process.')
    file_output = args.output_filename
    if file_output is None:
        parser.error('Please specify the name of the image to generate.')

    # 读取 PDF
    with open(file_input, 'rb') as my_pdf:
        text = read_pdf(my_pdf)

    # 解析并存储拼音
    # 无间隙全拼文本
    pinyin_nospace = Pinyin().get_pinyin(text, '')
    with open(file_text_nospace, 'w') as f:
        f.write(pinyin_nospace)
    # 有间隙全拼文本
    pinyin_separated = Pinyin().get_pinyin(text, ' ')
    with open(file_text_separated, 'w') as f:
        f.write(pinyin_separated)

    print('\n\n====== Encode ======\n')
    # 统计声母、介母韵母各自频次，两个排序相反
    re_count(pinyin_separated)
    list_in = sorted(phrase_in.items(), key=lambda x: x[1], reverse=True)  #  将字典按 value 的值进行排序 从大到小
    list_fi = sorted(phrase_fi.items(), key=lambda x: x[1], reverse=False)  # 将字典按 value 的值进行排序 从小到大

    pinyin_separated = pinyin_separated.replace('uang', 'nn')  # 特殊情况，打破原本双拼规则
    #  pinyin_separated = pinyin_separated.replace('ian', 'ss')   # 修改
    result_re = re_encode(pinyin_separated, list_in, list_fi)
    with open(file_text_encode, 'w') as f:
        f.write(result_re)

    # 字母使用统计结果
    stat = {}
    # 统计字母出现频次
    diction = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
               'u', 'v', 'w', 'x', 'y', 'z']
    for i in diction:
        stat[i] = result_re.count(i)

    # 计算输入效率
    len_ch = len(text)
    len_py = len(result_re)-len(text)
    Hx = 0
    for i in diction:
        p = stat[i] / len_py
        if p>0:
            Hx += -p * math.log10(p)
    L = len_py / len_ch  # 编码数据需要的位数和字符长度的比值
    eta_input = Hx / L
    print('输入的汉字数量: %d' % len_ch)
    print('敲击键盘总次数: %d' % len_py)
    print('每个汉字平均需要的拼音字母数: %.3f' % L)
    print('【输入效率: %.3f】' % eta_input)
    with open(file_answer, 'a') as f:
        f.write('【输入效率】:' + str(eta_input) + '\n')

    # 计算均衡率
    stat_list = []
    for i in diction:
        stat_list.append(stat[i] / len_py)
    stat_std = np.std(stat_list, ddof=0)
    print('【均衡率: %.3f】' % stat_std)
    with open(file_answer, 'a') as f:
        f.write('【均衡率】:' + str(stat_std) + '\n')

    print("========与问题3方案对比=========")
    """
    输入的汉字数量: 18118
    敲击键盘总次数: 36238
    每个汉字平均需要的拼音字母数: 2.000
    【输入效率: 0.691】
    【均衡率: 0.017】
    """

    # 敲击键盘次数变化量
    delta_

    # 绘制热力图
    encode = ''.join(re.findall('[a-z]', result_re))
    with open(file_text_encode_nospace, 'w') as f:
        f.write(encode)
    cmd = 'tapmap ' + file_text_encode_nospace + ' ' + file_output + ' -c Oranges'
    res = os.popen(cmd).readlines()
    print(res)

    # 辅助作图
    name_list = list(stat)
    num_list = list(stat.values())
    plt.barh(range(len(num_list)), num_list, tick_label=name_list)
    plt.show()


if __name__ == '__main__':
    main()

