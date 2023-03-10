# 文件形参 ： ..\Data\共产党宣言.pdf

import numpy as np
import argparse
from io import open
from xpinyin import Pinyin
import sys
sys.path.append(r'.\tools')
from read_pdf import read_pdf
from Excel_to_Matrix import excel_to_Matrix


parser = argparse.ArgumentParser(description='Generate a keyboard heatmap from a PDF file.')
parser.add_argument('input_filename', metavar='input_file', type=str,
                    help='the name of the file to process')
args = parser.parse_args()

# 韵母
finals_dict = {
    "a": " ", "ai": " ",
    "an": " ", "ang": " ",
    "ao": " ", "e": " ",
    "ei": " ", "en": " ",
    "eng": " ", "i": " ",
    "ia": " ","ian": " ",
    "iang": " ","iao": " ",
    "ie": " ","ong": " ",
    "in": " ","ing": " ",
    "iu": " ","o": " ",
    "ou": " ","u": " ",
    "uan": " ","ue": " ",
    "un": " ","v": " ",
}

# 复用韵母
reuse_dict = {
    "uang": " ",
    "iong": " ",
    "uai": " ",
    "ua": " ",
    "ve": " ",
    "uo": " ",
    "ui": " "
}

# 存放声母、介母韵母、无声韵母统计数据
phrase_fi = {}

# 统计出现频次
def count(org):
    tmp = org
    # 从长到短，统计后替换以免多次计算
    for key, value in finals_dict.items():
        if len(key) == 4:
            phrase_fi[key] = tmp.count(key)
            tmp = tmp.replace(key, '    ')
    for key, value in reuse_dict.items():
        if len(key) == 4:
            phrase_fi[key] = tmp.count(key)
            tmp = tmp.replace(key, '    ')

    for key, value in finals_dict.items():
        if len(key) == 3:
            phrase_fi[key] = tmp.count(key)
            tmp = tmp.replace(key, '   ')
    for key, value in reuse_dict.items():
        if len(key) == 3:
            phrase_fi[key] = tmp.count(key)
            tmp = tmp.replace(key, '   ')

    for key, value in finals_dict.items():
        if len(key) == 2:
            phrase_fi[key] = tmp.count(key)
            tmp = tmp.replace(key, '  ')
    for key, value in reuse_dict.items():
        if len(key) == 2:
            phrase_fi[key] = tmp.count(key)
            tmp = tmp.replace(key, '  ')

    for key, value in finals_dict.items():
        if len(key) == 1:
            phrase_fi[key] = tmp.count(key)

def calu(phrase_fi):
    Sum = 0
    pro = {}
    for key in phrase_fi:
        Sum += phrase_fi[key]  # 敲击键盘总次数
    for key in phrase_fi:
        pro[key] = phrase_fi[key] / Sum
    return pro

def main():
    # 解析参数
    file_input = args.input_filename
    if file_input is None:
        parser.error('Please specify the filename of the PDF file to process.')

    # 读取 PDF
    with open(file_input, 'rb') as my_pdf:
        text_ch = read_pdf(my_pdf)

    # 解析拼音
    text_py = Pinyin().get_pinyin(text_ch, '')
    count(text_py)

    Matrix = excel_to_Matrix("../Data/table.xlsx")

    # print(Matrix)
    dic_s = ['*', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'zh', 'ch', 'sh', 'r', 'z', 'c',
             's', 'y', 'w']  # 声母码表
    dic_y = ['a', 'o', 'e', 'i', 'u', 'v', 'ai', 'ei', 'ui', 'ao', 'ou', 'iu', 'ie', 've', 'an', 'en', 'in', 'un',
             'ang', 'eng', 'ing', 'ong', 'ia'
        , 'ua', 'uan', 'ue', 'uai', 'uo', 'iong', 'iang', 'uang', 'iao', 'ian']  # 韵母码表 (去掉'er')

    for i in range(len(dic_y)):
        vec = np.zeros((len(dic_y) - 1 - i))
        for j in range(len(dic_s)):
            if Matrix[i, j] == 1:
                for k in range(i + 1, len(dic_y)):
                    if Matrix[k, j] == 1:
                        vec[k - i - 1] = 1
        for z in range(i + 1, len(dic_y)):
            if vec[z - i - 1] == 0:
                # print(dic_y[i], " - ", dic_y[z])
                with open("../Data/process.txt", 'a') as f:
                    f.write(dic_y[i] + " - " + dic_y[z] + " : " + str(phrase_fi[dic_y[i]] + phrase_fi[dic_y[z]]) + '\n')

    print(phrase_fi)  # 33个韵母（不考虑'er'）


if __name__ == '__main__':
    main()


