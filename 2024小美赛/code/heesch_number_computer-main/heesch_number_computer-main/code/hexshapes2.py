from math import sqrt
import numpy as np

class Hexagon:
    def __init__(self, x, y, edgedata = [0, 0, 0, 0, 0, 0]):
        self.origin = (x, y)
        self.edgedata = edgedata
        self.verts = {
        "v1": (x-1,y-1),
        "v2": (x, y-1),
        "v3": (x+1, y),
        "v4": (x+1, y+1),
        "v5": (x, y+1),
        "v6": (x-1, y),
        }
        # we making the edges starting at the bottom, and then going counter-clockwise

        self.edges = [
        {"edge": {self.verts["v1"], self.verts["v2"]}, "type": edgedata[0]},
        {"edge": {self.verts["v2"], self.verts["v3"]}, "type": edgedata[1]},
        {"edge": {self.verts["v3"], self.verts["v4"]}, "type": edgedata[2]},
        {"edge": {self.verts["v4"], self.verts["v5"]}, "type": edgedata[3]},
        {"edge": {self.verts["v5"], self.verts["v6"]}, "type": edgedata[4]},
        {"edge": {self.verts["v6"], self.verts["v1"]}, "type": edgedata[5]},
        ]


    def to_data(self):
        return [self.origin[0], self.origin[1], self.edgedata]

    def __eq__(self, other):
        return (self.origin == other.origin and self.edgedata == other.edgedata)

    def flip(self):

        def edgedata_flip(edgedata):
            new_edgedata = [
            edgedata[0],
            edgedata[5],
            edgedata[4],
            edgedata[3],
            edgedata[2],
            edgedata[1],
            ]

            return new_edgedata

        return Hexagon(-self.origin[0] + self.origin[1], self.origin[1], edgedata_flip(self.edgedata))

    def turn60(self):

        def edgedata_turn60(edgedata):
            new_edgedata = [
            edgedata[5],
            edgedata[0],
            edgedata[1],
            edgedata[2],
            edgedata[3],
            edgedata[4],
            ]
            return new_edgedata

        new_origin = (-self.origin[1]+self.origin[0], self.origin[0])
        return Hexagon(new_origin[0], new_origin[1], edgedata_turn60(self.edgedata))

    def translate(self, xval, yval):
        newx = self.origin[0] + xval
        newy = self.origin[1] + yval
        return Hexagon(newx, newy, edgedata = self.edgedata)

    def plot_data(self):
        plottinglist = []
        for elem in self.edges:
            el = list(elem["edge"])
            xcoords = [el[0][0]-0.5 * el[0][1], el[1][0]- 0.5 * el[1][1]]
            ycoords = [0.5*sqrt(3)*el[0][1], 0.5*sqrt(3)*el[1][1]]
            if elem["type"] == 0:
                plottinglist.extend([xcoords, ycoords, "b-"])
            elif elem["type"] == 1 or elem["type"]  == -1:
                plottinglist.extend([xcoords, ycoords, "b--"])
        return plottinglist


class HShape:
    def __init__(self, hexes, priority = [], shapecode = {"translation": np.array([0,0]),"flipped": False,  "rotation": 0}):
        self.hexes = hexes
        self.edges = self.edgemaker()
        self.priority = priority
        self.shapecode = shapecode

    def to_data(self):
        return [hex.to_data() for hex in self.hexes]

    def __eq__(self, other):
        xmin_s = min([hex.origin[0] for hex in self.hexes])
        ymin_s = min([hex.origin[1] for hex in self.hexes])
        xmin_o = min([hex.origin[0] for hex in other.hexes])
        ymin_o = min([hex.origin[1] for hex in other.hexes])
        return all(hex in other.translate(xmin_s-xmin_o,ymin_s-ymin_o).hexes for hex in self.hexes)

    """ With these functions we instantiate some stuff"""
    def edgemaker(self):
        hexes_edge_list = [edge for hex in self.hexes for edge in hex.edges]
        total_edge_list = [edge for edge in hexes_edge_list if hexes_edge_list.count(edge) == 1]
        return total_edge_list

    def vertmaker(self):
        return [hex.origin for hex in self.hexes]

    def orientations(self, equality = False):
        orientation_list =[
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

        if equality:
            representatives = []
            equality_list = []
            for i in range(len(orientation_list)):
                orientation = orientation_list[i]
                if i == 0:
                    representatives.append(orientation)
                    equality_list.append([orientation.shapecode])
                else:
                    for j in range( len( representatives ) ):
                        if orientation == representatives[j]:
                            equality_list[j].append(orientation.shapecode)
                            break
                        if j == len( representatives )-1:
                            representatives.append(orientation)
                            equality_list.append([orientation.shapecode])
            return equality_list
        else:
            new_orientations_list = []
            for orientation in orientation_list:
                if orientation not in new_orientations_list:
                    new_orientations_list.append(orientation)
            return new_orientations_list

    def flip(self):
        new_hexes = []
        for hex in self.hexes:
            new_hexes.append(hex.flip())

        new_shapecode = {
        "translation": self.shapecode["translation"],
        "flipped": not self.shapecode["flipped"],
        "rotation": self.shapecode["rotation"],
        }


        return HShape(new_hexes, priority = self.priority, shapecode = new_shapecode)

    def translate(self, xval, yval):
        new_hexes = []
        for hex in self.hexes:
            new_hexes.append(hex.translate(xval, yval))


        new_priority = []
        for hex in self.priority:
            new_priority.append(hex.translate(xval, yval))

        new_shapecode = {
        "translation": self.shapecode["translation"] + np.array([xval, yval]),
        "flipped": self.shapecode["flipped"],
        "rotation": self.shapecode["rotation"],
        }

        return HShape(new_hexes, priority = new_priority, shapecode = new_shapecode)

    def translate_rel(self, hex1, hex2):
        return self.translate(hex1.origin[0] - hex2.origin[0], hex1.origin[1] - hex2.origin[1])

    def turn60(self):
        new_hexes = []
        for hex in self.hexes:
            new_hexes.append(hex.turn60())
        new_priority = []
        for hex in self.priority:
            new_priority.append(hex.turn60())

        new_shapecode = {
        "translation": self.shapecode["translation"],
        "flipped": self.shapecode["flipped"],
        "rotation": (self.shapecode["rotation"]+60) % 360,
        }
        return HShape(new_hexes, priority = new_priority, shapecode = new_shapecode)

    def inside_remover(self):
        inside_list = []
        for hex in self.hexes:
            if all(edge not in self.edges for edge in [elem["edge"] for elem in hex.edges]):
                inside_list.append(hex)
        new_hexes = [elem for elem in self.hexes if elem not in inside_list]
        return new_hexes

    def outside(self):
        def rawhexes(hexlist):
            return [Hexagon(hex.origin[0], hex.origin[1]) for hex in hexlist]

        bighexlist = []
        for vert in self.vertmaker():
            bighexlist.extend(bighex_maker(vert[0], vert[1]))
        res = self.priority.copy()
        for hex in bighexlist:
            if hex not in res:
                res.append(hex)
        res = [hex for hex in res if hex not in rawhexes(self.hexes)]
        return res

    def corona_maker(self, base_orientations, bookkeeping=False, heesch=False):

        def not_occupied_in(elem, config, extra = False):
            config_hexes = self.hexes.copy() if extra else []

            for shape in config:
                config_hexes.extend(shape.hexes)
            for hex in config_hexes:
                if elem.origin == hex.origin:
                    return False

            return True

        def edge_filter(edgelist_ns, edgelist_config):
            config_edges = [edge["edge"] for edge in edgelist_config]
            ns_edges = [edge["edge"] for edge in edgelist_ns]
            for i in range(len(ns_edges)):
                if ns_edges[i] in config_edges:
                    if not edgelist_ns[i]["type"] == -1 * edgelist_config[config_edges.index(ns_edges[i])]["type"]:
                        return False
            return True

        def config_edgemaker(config):
            hexes_edge_list = [edge for shape in config+[self] for edge in shape.edges]
            total_edge_list = [edge for edge in hexes_edge_list if hexes_edge_list.count(edge) == 1]
            return total_edge_list

        # base_orientations_boundaries = [orientation.inside_remover() for orientation in base_orientations ]
        bookkeeper = []
        possible_config = []
        outside_list = self.outside()
        for i in range(len(outside_list)):
            print(f" we are now at {int((i+1)/len(outside_list)*100)}% ")
            outs_hex = outside_list[i]
            if len(possible_config) == 0:
                for index in range(len(base_orientations)):
                    for ns_hex in base_orientations[index].hexes:
                        new_shape = base_orientations[index].translate_rel(outs_hex, ns_hex)
                        if all(not_occupied_in(hex, [self]) for hex in new_shape.hexes) and edge_filter(new_shape.edges, self.edges):
                            possible_config.append([new_shape])
                if bookkeeping:
                    bookkeeper.append(possible_config)
                print(len(possible_config))

            else:
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
                        #print(f" its occupied in the config? ")
                        new_possible_config.append(config)
                if new_possible_config == []:
                    return []
                possible_config = new_possible_config.copy()
                if bookkeeping:
                    bookkeeper.append(possible_config)
                print(len(possible_config))
        return [[config] for config in possible_config] if heesch else possible_config

    def second_corona(self):
        next_corona_list = []
        coronalist = self.corona_maker(self.orientations())
        for i in range(len(coronalist)):
            corona = coronalist[i]
            print(f"CORONA we are now at {int((i+1)/len(coronalist)*100)}% ")
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

    """ For computing Heesch numbers """

    def heesch_corona(self, coronalist):
        next_corona_list = []
        for i in range(len(coronalist)):
            print(f" we are now at {int((i+1)/len(coronalist)*100)}% ")
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

    def heesch_computer(self):
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


    def plot_data(self, color= "b"):
        plottinglist = []
        for edge in self.edges:
            el = list(edge["edge"])
            xcoords = [el[0][0]-0.5 * el[0][1], el[1][0]- 0.5 * el[1][1]]
            ycoords = [0.5*sqrt(3)*el[0][1], 0.5*sqrt(3)*el[1][1]]
            plottinglist.extend([xcoords, ycoords, f"{color}-"])
            # if edge["type"] == 0:
            #     plottinglist.extend([xcoords, ycoords, f"{color}-"])
            # elif edge["type"] == 1 or edge["type"]  == -1:
            #     plottinglist.extend([xcoords, ycoords, f"r-"])
        return plottinglist

    def outside_plot_data(self):
        plottinglist = []
        for elem in self.outside():
            for edge in [elem2["edge"] for elem2 in elem.edges]:
                el = list(edge)
                xcoords = [el[0][0]-0.5 * el[0][1], el[1][0]- 0.5 * el[1][1]]
                ycoords = [0.5*sqrt(3)*el[0][1], 0.5*sqrt(3)*el[1][1]]
                plottinglist.extend([xcoords, ycoords, "b-"])
        return plottinglist


def bighex_maker(x,y):
    hexes = [
    Hexagon(x,y),
    Hexagon(x-1, y-2),
    Hexagon(x+1, y-1),
    Hexagon(x+2, y+1),
    Hexagon(x+1, y+2),
    Hexagon(x-1, y+1),
    Hexagon(x-2, y-1),
    ]
    return hexes
