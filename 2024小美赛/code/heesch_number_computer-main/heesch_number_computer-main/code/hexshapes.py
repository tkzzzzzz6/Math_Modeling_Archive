from math import sqrt  # 导入数学库中的平方根函数

# 定义六边形类
class Hexagon:
    def __init__(self, x, y, edgedata = [0, 0, 0, 0, 0, 0]):  # 初始化函数,x,y为中心坐标,edgedata为边的类型数据
        self.origin = (x, y)  # 存储中心点坐标
        self.edgedata = edgedata  # 存储边的类型数据
        self.verts = {  # 存储六个顶点的坐标
        "v1": (x-1,y-1),  # 左下顶点
        "v2": (x, y-1),   # 下顶点
        "v3": (x+1, y),   # 右下顶点
        "v4": (x+1, y+1), # 右上顶点
        "v5": (x, y+1),   # 上顶点
        "v6": (x-1, y),   # 左上顶点
        }
        # 从底部开始逆时针定义六条边
        self.edges = [  # 存储边的信息,包括顶点和类型
        {"edge": {self.verts["v1"], self.verts["v2"]}, "type": edgedata[0]},  # 底边
        {"edge": {self.verts["v2"], self.verts["v3"]}, "type": edgedata[1]},  # 右下边
        {"edge": {self.verts["v3"], self.verts["v4"]}, "type": edgedata[2]},  # 右边
        {"edge": {self.verts["v4"], self.verts["v5"]}, "type": edgedata[3]},  # 右上边
        {"edge": {self.verts["v5"], self.verts["v6"]}, "type": edgedata[4]},  # 左上边
        {"edge": {self.verts["v6"], self.verts["v1"]}, "type": edgedata[5]},  # 左边
        ]

    def to_data(self):  # 将六边形数据转换为列表形式
        return [self.origin[0], self.origin[1], self.edgedata]

    def __eq__(self, other):  # 判断两个六边形是否相等
        return (self.origin == other.origin and self.edgedata == other.edgedata)

    def flip(self):  # 水平翻转六边形

        def edgedata_flip(edgedata):  # 翻转边的类型数据
            new_edgedata = [
            edgedata[0],  # 底边保持不变
            edgedata[5],  # 右下边变为左边
            edgedata[4],  # 右边变为左上边
            edgedata[3],  # 右上边保持不变
            edgedata[2],  # 左上边变为右边
            edgedata[1],  # 左边变为右下边
            ]
            return new_edgedata

        return Hexagon(-self.origin[0] + self.origin[1], self.origin[1], edgedata_flip(self.edgedata))

    def turn60(self):  # 顺时针旋转60度

        def edgedata_turn60(edgedata):  # 旋转边的类型数据
            new_edgedata = [
            edgedata[5],  # 左边变为底边
            edgedata[0],  # 底边变为右下边
            edgedata[1],  # 右下边变为右边
            edgedata[2],  # 右边变为右上边
            edgedata[3],  # 右上边变为左上边
            edgedata[4],  # 左上边变为左边
            ]
            return new_edgedata

        new_origin = (-self.origin[1]+self.origin[0], self.origin[0])  # 计算旋转后的中心点坐标
        return Hexagon(new_origin[0], new_origin[1], edgedata_turn60(self.edgedata))

    def translate(self, xval, yval):  # 平移六边形
        newx = self.origin[0] + xval  # 新的x坐标
        newy = self.origin[1] + yval  # 新的y坐标
        return Hexagon(newx, newy, edgedata = self.edgedata)

    def plot_data(self):  # 生成绘图数据
        plottinglist = []  # 存储绘图数据的列表
        for elem in self.edges:  # 遍历每条边
            el = list(elem["edge"])  # 获取边的顶点
            xcoords = [el[0][0]-0.5 * el[0][1], el[1][0]- 0.5 * el[1][1]]  # 计算x坐标
            ycoords = [0.5*sqrt(3)*el[0][1], 0.5*sqrt(3)*el[1][1]]  # 计算y坐标
            if elem["type"] == 0:  # 如果边的类型为0
                plottinglist.extend([xcoords, ycoords, "k-"])  # 用黑色实线绘制
            elif elem["type"] == 1 or elem["type"]  == -1:  # 如果边的类型为1或-1
                plottinglist.extend([xcoords, ycoords, "k--"])  # 用黑色虚线绘制
        return plottinglist

# 定义由多个六边形组成的形状类
class HShape:
    def __init__(self, hexes, priority = []):  # 初始化函数,hexes为六边形列表,priority为优先级列表
        self.hexes = hexes  # 存储六边形列表
        self.edges = self.edgemaker()  # 生成边的列表
        self.priority = priority  # 存储优先级列表

    def to_data(self):  # 将形状数据转换为列表形式
        return [hex.to_data() for hex in self.hexes]

    def __eq__(self, other):  # 判断两个形状是否相等
        xmin_s = min([hex.origin[0] for hex in self.hexes])  # 当前形状最小x坐标
        ymin_s = min([hex.origin[1] for hex in self.hexes])  # 当前形状最小y坐标
        xmin_o = min([hex.origin[0] for hex in other.hexes])  # 另一个形状最小x坐标
        ymin_o = min([hex.origin[1] for hex in other.hexes])  # 另一个形状最小y坐标
        return all(hex in other.translate(xmin_s-xmin_o,ymin_s-ymin_o).hexes for hex in self.hexes)

    """ 以下是一些实例化相关的函数 """
    def edgemaker(self):  # 生成边的列表
        hexes_edge_list = [edge for hex in self.hexes for edge in hex.edges]  # 获取所有六边形的边
        total_edge_list = [edge for edge in hexes_edge_list if hexes_edge_list.count(edge) == 1]  # 只保留出现一次的边
        return total_edge_list

    def vertmaker(self):  # 生成顶点列表
        return [hex.origin for hex in self.hexes]

    def orientations(self):  # 生成所有可能的方向
        orientation_list =[  # 包括旋转和翻转的所有组合
        self,
        self.turn60(),
        self.turn60().turn60(),
        self.turn60().turn60().turn60(),
        self.turn60().turn60().turn60().turn60(),
        self.turn60().turn60().turn60().turn60().turn60(),
        self.flip(),
        self.flip().turn60(),
        self.flip().turn60().turn60(),
        self.flip().turn60().turn60().turn60(),
        self.flip().turn60().turn60().turn60().turn60(),
        self.flip().turn60().turn60().turn60().turn60().turn60(),
        ]
        new_orientations_list = []  # 存储不重复的方向
        for orientation in orientation_list:
            if orientation not in new_orientations_list:
                new_orientations_list.append(orientation)
        return new_orientations_list

    def flip(self):  # 水平翻转形状
        new_hexes = []
        for hex in self.hexes:
            new_hexes.append(hex.flip())
        return HShape(new_hexes)

    def translate(self, xval, yval):  # 平移形状
        new_hexes = []
        for hex in self.hexes:
            new_hexes.append(hex.translate(xval, yval))

        new_priority = []
        for hex in self.priority:
            new_priority.append(hex.translate(xval, yval))
        return HShape(new_hexes, new_priority)

    def translate_rel(self, hex1, hex2):  # 相对平移形状
        return self.translate(hex1.origin[0] - hex2.origin[0], hex1.origin[1] - hex2.origin[1])

    def turn60(self):  # 顺时针旋转60度
        new_hexes = []
        for hex in self.hexes:
            new_hexes.append(hex.turn60())
        new_priority = []
        for hex in self.priority:
            new_priority.append(hex.turn60())
        return HShape(new_hexes, new_priority)

    def inside_remover(self):  # 移除内部的六边形
        inside_list = []
        for hex in self.hexes:
            if all(edge not in self.edges for edge in [elem["edge"] for elem in hex.edges]):
                inside_list.append(hex)
        new_hexes = [elem for elem in self.hexes if elem not in inside_list]
        return new_hexes

    def outside(self):  # 获取外部的六边形
        def rawhexes(hexlist):  # 将六边形列表转换为原始六边形
            return [Hexagon(hex.origin[0], hex.origin[1]) for hex in hexlist]

        bighexlist = []  # 存储大六边形列表
        for vert in self.vertmaker():
            bighexlist.extend(bighex_maker(vert[0], vert[1]))
        res = self.priority.copy()  # 复制优先级列表
        for hex in bighexlist:
            if hex not in res:
                res.append(hex)
        res = [hex for hex in res if hex not in rawhexes(self.hexes)]  # 移除已存在的六边形
        return res

    def corona_maker(self, base_orientations, bookkeeping=False, heesch=False):  # 生成冠状结构

        def not_occupied_in(elem, config, extra = False):  # 检查位置是否被占用
            config_hexes = self.hexes.copy() if extra else []

            for shape in config:
                config_hexes.extend(shape.hexes)
            for hex in config_hexes:
                if elem.origin == hex.origin:
                    return False

            return True

        def edge_filter(edgelist_ns, edgelist_config):  # 过滤边
            config_edges = [edge["edge"] for edge in edgelist_config]
            ns_edges = [edge["edge"] for edge in edgelist_ns]
            for i in range(len(ns_edges)):
                if ns_edges[i] in config_edges:
                    if not edgelist_ns[i]["type"] == -1 * edgelist_config[config_edges.index(ns_edges[i])]["type"]:
                        return False
            return True

        def config_edgemaker(config):  # 生成配置的边
            hexes_edge_list = [edge for shape in config+[self] for edge in shape.edges]
            total_edge_list = [edge for edge in hexes_edge_list if hexes_edge_list.count(edge) == 1]
            return total_edge_list

        bookkeeper = []  # 存储过程记录
        possible_config = []  # 存储可能的配置
        outside_list = self.outside()  # 获取外部六边形
        for i in range(len(outside_list)):  # 遍历外部六边形
            print(f"test: we are now at {int((i+1)/len(outside_list)*100)}% ")  # 打印进度
            outs_hex = outside_list[i]
            if len(possible_config) == 0:  # 如果没有可能的配置
                for index in range(len(base_orientations)):
                    for ns_hex in base_orientations[index].hexes:
                        new_shape = base_orientations[index].translate_rel(outs_hex, ns_hex)
                        if all(not_occupied_in(hex, [self]) for hex in new_shape.hexes) and edge_filter(new_shape.edges, self.edges):
                            possible_config.append([new_shape])
                if bookkeeping:
                    bookkeeper.append(possible_config)
                print(len(possible_config))

            else:  # 如果已有可能的配置
                new_possible_config = []
                for config in possible_config:
                    if not_occupied_in(outs_hex, config):
                        for index in range(len(base_orientations)):
                            for ns_hex in base_orientations[index].hexes:
                                new_shape = base_orientations[index].translate_rel(outs_hex, ns_hex)
                                if all(not_occupied_in(hex, config, extra=True) for hex in new_shape.hexes) and edge_filter(new_shape.edges, config_edgemaker(config)):
                                    new_config = config.copy()
                                    new_config.append(new_shape)
                                    new_possible_config.append(new_config)
                                else:
                                    continue
                    else:
                        new_possible_config.append(config)
                if new_possible_config == []:
                    return []
                possible_config = new_possible_config.copy()
                if bookkeeping:
                    bookkeeper.append(possible_config)
                print(len(possible_config))
        return [[config] for config in possible_config] if heesch else possible_config

    def second_corona(self):  # 生成第二层冠状结构
        next_corona_list = []
        coronalist = self.corona_maker(self.orientations())  # 生成第一层冠状结构
        for i in range(len(coronalist)):
            corona = coronalist[i]
            print(f"CORONA we are now at {int((i+1)/len(coronalist)*100)}% ")  # 打印进度
            pre_priority = [hex for shape in corona+[self] for hex in shape.priority]
            priority = []
            for hex in  pre_priority:
                if hex not in priority:
                    priority.append(hex)
            new_shape = HShape([hex for shape in corona+[self] for hex in shape.hexes],
            priority = priority)
            new_corona = new_shape.corona_maker(self.orientations())
            if new_corona == []:
                pass
            else:
                next_corona_list.append({"first": corona, "second": new_corona})
        return next_corona_list

    """ 计算Heesch数 """

    def heesch_corona(self, coronalist):  # 计算Heesch冠状结构
        next_corona_list = []
        for i in range(len(coronalist)):
            print(f" heesch_corona:we are now at {int((i+1)/len(coronalist)*100)}% ")  # 打印进度
            corona_config = coronalist[i]
            ns_hexes = self.hexes.copy()
            for corona in corona_config:
                for shape in corona:
                    ns_hexes.extend(shape.hexes)
            new_shape = HShape(ns_hexes)
            new_corona = new_shape.corona_maker(self.orientations())

            for elem in new_corona:
                new_corona_config = corona_config.copy()
                new_corona_config.append(elem)
                next_corona_list.append(new_corona_config)
        return next_corona_list

    def heesch_computer(self):  # 计算Heesch数
        coronalist = self.corona_maker(self.orientations(), heesch=True)
        if coronalist == []:
            return []
        else:
            i = 0
            while True:
                message = f"""
                --------------------------------------
                We are now computing the {i+2}nd corona
                --------------------------------------
                """
                print(message)
                new_corona_list = self.heesch_corona(coronalist)
                if new_corona_list == []:
                    print(f" The heesch number is {i+1}")
                    return coronalist
                else:
                    coronalist = new_corona_list.copy()
                    i += 1

    def plot_data(self, color= "k"):  # 生成绘图数据,默认使用黑色
        plottinglist = []
        for edge in self.edges:
            el = list(edge["edge"])
            xcoords = [el[0][0]-0.5 * el[0][1], el[1][0]- 0.5 * el[1][1]]  # 计算x坐标
            ycoords = [0.5*sqrt(3)*el[0][1], 0.5*sqrt(3)*el[1][1]]  # 计算y坐标
            plottinglist.extend([xcoords, ycoords, f"{color}-"])
        return plottinglist

    def outside_plot_data(self):  # 生成外部六边形的绘图数据
        plottinglist = []
        for elem in self.outside():  # 遍历外部六边形
            for edge in [elem2["edge"] for elem2 in elem.edges]:  # 遍历每条边
                el = list(edge)
                xcoords = [el[0][0]-0.5 * el[0][1], el[1][0]- 0.5 * el[1][1]]  # 计算x坐标
                ycoords = [0.5*sqrt(3)*el[0][1], 0.5*sqrt(3)*el[1][1]]  # 计算y坐标
                plottinglist.extend([xcoords, ycoords, "k:"])  # 用黑色点线绘制
        return plottinglist

# 生成大六边形
def bighex_maker(x,y):  # 根据中心点坐标生成由7个六边形组成的大六边形
    hexes = [
    Hexagon(x,y),  # 中心六边形
    Hexagon(x-1, y-2),  # 左下六边形
    Hexagon(x+1, y-1),  # 右下六边形
    Hexagon(x+2, y+1),  # 右六边形
    Hexagon(x+1, y+2),  # 右上六边形
    Hexagon(x-1, y+1),  # 左上六边形
    Hexagon(x-2, y-1),  # 左六边形
    ]
    return hexes
