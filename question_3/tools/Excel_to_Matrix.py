import xlrd
import numpy as np
def excel_to_Matrix(path):
    data = xlrd.open_workbook(path)
    table = data.sheets()[1]  # 读取sheet2内容
    nrows = table.nrows
    ncols = table.ncols
    datamatrix = np.zeros((nrows, ncols))
    for x in range(ncols):
        cols = table.col_values(x)
        cols1 = np.matrix(cols)
        #把list转换为矩阵进行矩阵操作
        datamatrix[:, x] = cols1
        #把数据进行存储
    return datamatrix