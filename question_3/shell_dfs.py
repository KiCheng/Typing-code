import numpy as np
import xlrd

def excel_to_Matrix(path):
#读excel数据转为矩阵函数
    data = xlrd.open_workbook(path)
    table = data.sheets()[0]
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

def load_data(Matrix):
    my_dict = {}
    row = col = len(Matrix[0])
    for i in range(row * col):
        tx = int(i / row)
        ty = i % row
        if Matrix[tx][ty] != 0:
            my_dict[Matrix[tx][ty]] = [tx,ty]
    return my_dict


def calc():
    return np.var(np.array(temp))

def dfs(my_dict,step,minn,diction):
    if step == 7:
        res = calc()
        minn = min(minn, res)
        diction[minn] = temp
        print(temp)
        return
    
    for key, value in my_dict.items():
        tx = value[0]
        ty = value[1]

        if vis[tx][ty] == 1:
            continue

        if visx[tx] or visy[ty]:
            continue

        vis[tx][ty] = 1
        visx[tx] = 1
        visy[ty] = 1
        temp.append(key)
        dfs(my_dict,step + 1,minn,diction)
        temp.pop()
        vis[tx][ty] = 0
        visx[tx] = 0
        visy[ty] = 0


Matrix = excel_to_Matrix("test.xlsx")
row = len(Matrix[0])  # row=33
col = row  # col=33
my_dict = load_data(Matrix)  # 储存可用点的字典

vis = np.zeros((row, col))
visx = np.zeros(row)
visy = np.zeros(col)
temp = []
diction = {}
minn = 10000000007
dfs(my_dict,0,minn,diction)

print('------最小方差--------')
print(diction[minn])
print(minn)



