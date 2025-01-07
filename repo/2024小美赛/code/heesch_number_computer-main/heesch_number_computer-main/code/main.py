# 导入所需的模块和类
from shapes import Triangle, Shape  # 从shapes模块导入Triangle和Shape类
from hexshapes import Hexagon, HShape  # 从hexshapes模块导入Hexagon和HShape类
from shapes import hexagon_maker as hexmaker  # 从shapes模块导入hexagon_maker函数并重命名为hexmaker
from shapes import triangle_of_hexes as toh  # 从shapes模块导入triangle_of_hexes函数并重命名为toh
from hexshapes import bighex_maker as bhmaker  # 从hexshapes模块导入bighex_maker函数并重命名为bhmaker
import time  # 导入time模块用于计时

# 定义数据写入函数,接收基础形状和类型参数
def data_writer(base, type = "corona"):
    with open('./plotlist.txt', 'w') as file:  # 打开文件用于写入
        if type == "heesch":  # 如果类型是heesch
            coronalist = base.heesch_computer()[0]  # 计算Heesch数据
            coronadata = []  # 初始化corona数据列表
            for corona_config in coronalist:  # 遍历每个corona配置
                coronadata.append([shape.to_data() for shape in corona_config])  # 将形状数据添加到列表
            datadict = {"type": type, "num": len(coronalist), "data": {"base": base.to_data(), "heesch": coronadata}}  # 创建数据字典

        elif type == "corona2":  # 如果类型是corona2
            coronalist = base.second_corona()[0]  # 计算第二corona数据
            first_data = []  # 初始化第一层数据列表
            for shape in coronalist["first"]:  # 遍历第一层形状
                first_data.append(shape.to_data())  # 添加形状数据
            second_data = []  # 初始化第二层数据列表
            for shape in coronalist["second"][0]:  # 遍历第二层形状
                second_data.append(shape.to_data())  # 添加形状数据
            datadict = {"type": type, "data": {"base": base.to_data(), "first": first_data, "second": second_data}}  # 创建数据字典

        elif type == "corona":  # 如果类型是corona
            coronalist = base.corona_maker(base.orientations())[0]  # 计算corona数据
            corona_data = []  # 初始化corona数据列表
            for shape in coronalist:  # 遍历每个形状
                corona_data.append(shape.to_data())  # 添加形状数据
            datadict = {"type": type, "data": {"base": base.to_data(), "corona": corona_data}}  # 创建数据字典

        elif type == "base":  # 如果类型是base
            datadict = {"type": type, "data": {"base": base.to_data()}}  # 创建只包含基础形状的数据字典

        file.write(str(datadict))  # 将数据字典写入文件

start_time = time.time()  # 记录开始时间

""" Some testing shapes"""  # 一些测试形状的注释
# S1 = Shape(toh())  # 创建三角形六边形的形状
# S1 = Shape(toh() + hexmaker(2,-5) + hexmaker(5, -2) + hexmaker(6, -3))  # 创建复合形状
# S1 = Shape([triangle for triangle in toh() if triangle not in hexmaker(3,-3)+hexmaker(2,-2)])  # 创建过滤后的形状
# S1 = Shape([triangle for triangle in hexmaker(0,0)+[Triangle(1,1)] if triangle not in [Triangle(0,0)]])  # 创建过滤后的形状
# S1 = Shape(hexmaker(-1,1)+hexmaker(1,2)+hexmaker(2,1)+hexmaker(1,-1)+hexmaker(-1,-2))  # 创建多个六边形组合的形状


""" edge data testing """  # 边数据测试的注释
# S1 = HShape([Hexagon(0,0, [1, 1, 1, 0, -1, -1])])  # 创建带边数据的六边形

"""4hex H2
takes too long"""  # 4个六边形的H2形状注释(计算时间太长)

# priority = [  # 优先级列表
# Hexagon(-1, 1),  # 第一个优先六边形
# Hexagon(1, 2),  # 第二个优先六边形
# ]
#
# S1 = HShape([  # 创建H形状
# Hexagon(0, 0, [0, 0, 0, 1, -1, 0]),  # 中心六边形
# Hexagon(1, -1),  # 右下六边形
# Hexagon(2, 1),  # 右上六边形
# Hexagon(3, 0),  # 最右六边形
# ],
# priority = priority  # 设置优先级
# )

"""3hex H2
computes in 13 sec"""  # 3个六边形的H2形状注释(计算时间13秒)

# S1 = HShape(  # 创建H形状
# [Hexagon(0, 0, [0, 0, 0, -1, 0, -1]),  # 第一个六边形
# Hexagon(2, 1, [0, 0, 1, 0, 0, 0]),  # 第二个六边形
# Hexagon(1, -1)],  # 第三个六边形
#
# )

""" 2-hexapillar
computes in 323 sec"""  # 2个六边形的柱状体注释(计算时间323秒)
S1 = HShape(  # 创建H形状
[Hexagon(0, 0, [1, 1, 0, -1, -1, 0]),  # 第一个六边形
Hexagon(2, 1, [1, 1, -1, -1, -1, 0])],  # 第二个六边形

)

# H1 = Hexagon(0, 0, [1, 0, 0, 0, 0, 0])  # 创建第一个六边形
# H2 = Hexagon(1, 2, [0, 0, -1, 0, 0, 0])  # 创建第二个六边形
# S1 = HShape([H1, H2])  # 组合成H形状

# S1 = HShape([  # 创建H形状
# Hexagon(0, 0, [0, 0, 0, 0, -1, 0]),  # 中心六边形
# Hexagon(1, -1, [0, 0, 0, 0, 0, 1]),  # 右下六边形
# Hexagon(2, 1),  # 右上六边形
# Hexagon(3, 0),  # 最右六边形
# Hexagon(0, -3),  # 最下六边形
# ])

""" hexagon testing """  # 六边形测试注释
# S1 = HShape( [Hexagon(0,0), Hexagon(2,1), Hexagon(3,0)])  # 创建简单的三个六边形组合
# S1 = HShape( [hex for hex in bhmaker(0,0) if hex not in [Hexagon(-2,-1), Hexagon(0,0)] ]  )  # 创建过滤后的大六边形
# S1 = HShape( bhmaker(0,0)+[Hexagon(-2,2), Hexagon(-2,-4), Hexagon(4,2), Hexagon(0,-3), Hexagon(3,0), Hexagon(4,-1)] )  # 创建复杂的六边形组合


""" This has types:
    1) Corona
    2) Boundary
    3) Base
"""  # 数据类型说明注释
data_writer(S1, type = "heesch")  # 将形状数据写入文件
print("--- %s seconds ---" % (time.time() - start_time))  # 打印程序运行时间
