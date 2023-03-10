import numpy as np
import os
import math
import re
import argparse
from io import StringIO
from io import open
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf

from xpinyin import Pinyin

parser = argparse.ArgumentParser(description='Generate a keyboard heatmap from a PDF file.')
parser.add_argument('input_filename', metavar='input_file', type=str,
                    help='the name of the file to process')
args = parser.parse_args()

def read_pdf(pdf):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    process_pdf(rsrcmgr, device, pdf)
    device.close()
    content = retstr.getvalue()
    retstr.close()

    # 获取文本并提取汉字
    lines = str(content)
    chinese = ''.join(re.findall('[\u4e00-\u9fa5]', lines))
    return chinese

def main():
    file_answer = 'answer_2.txt'
    # 解析参数
    file_input = args.input_filename
    if file_input is None:
        parser.error('Please specify the filename of the PDF file to process.')

    # 读取 PDF
    with open(file_input, 'rb') as my_pdf:
        text_ch = read_pdf(my_pdf)

    # 解析拼音
    text_py = Pinyin().get_pinyin(text_ch, '')

    # 统计字母出现频次
    diction = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
               'u', 'v', 'w', 'x', 'y', 'z']
    stat = {}
    for i in diction:
        stat[i] = text_py.count(i)

    # 计算输入效率
    len_ch = len(text_ch)
    len_py = len(text_py)
    Hx = 0
    for i in diction:
        p = stat[i] / len_py
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


if __name__ == '__main__':
    main()
