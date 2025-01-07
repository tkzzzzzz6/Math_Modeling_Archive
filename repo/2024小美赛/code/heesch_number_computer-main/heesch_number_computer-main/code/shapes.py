from math import sqrt


class Triangle:

    """ Here we create triangles of side length 1"""

    def __init__(self, x, y, up = True, edgedata = [ 0, 0, 0 ]):
        self.up = up
        self.v1, self.v2, self.v3 = ((x,y), (x+1,y), (x+1, y+1)) if self.up else ((x,y),(x+1,y),(x,y-1))
        self.edgedict = [{ "edge": {self.v1,self.v2}, "type": edgedata[0]},
                    {"edge": {self.v2, self.v3}, "type": edgedata[1]},
                    {"edge": {self.v3, self.v1}, "type": edgedata[2]}]
        self.edges = [elem["edge"] for elem in self.edgedict]

    def translate(self, xval, yval):
        newx = self.v1[0] + xval
        newy = self.v1[1] + yval
        return Triangle(newx,newy, up = self.up)

    def __str__(self):
        return f"{self.v1}, {self.v2}, {self.v3}"

    def __eq__(self, other):
        return(self.v1 == other.v1 and self.up == other.up)

    def common_edge(self, other):
        for edge in self.edges:
            for other_edge in other.edges:
                if edge == other_edge:
                    return edge

    def flip(self):
        return Triangle(-self.v1[0]+self.v1[1],self.v1[1], up=self.up)


    def vertex_returner(self):
        return [self.v1,self.v2,self.v3]

    def turn60(self):
        #print(" a triangle has been turned")
        vertex_list = [self.v1, self.v2, self.v3]
        new_vertex_list = []
        for vert in vertex_list:
            new_vertex = (-vert[1]+vert[0], vert[0])
            new_vertex_list.append(new_vertex)
        xmin = min([elem[0] for elem in new_vertex_list])
        ymin = min([elem[1] for elem in new_vertex_list])
        ymax = max([elem[1] for elem in new_vertex_list])
        if not self.up:
            return Triangle(xmin, ymin)
        else:
            return Triangle(xmin, ymax, up=False)


    def plot_data(self, color= "b-"):
        plottinglist = []
        for edge in self.edges:
            el = list(edge)
            xcoords = [el[0][0]-0.5 * el[0][1], el[1][0]- 0.5 * el[1][1]]
            ycoords = [0.5*sqrt(3)*el[0][1], 0.5*sqrt(3)*el[1][1]]
            plottinglist.extend([xcoords, ycoords, color])
        return plottinglist


class Shape:
    def __init__(self, triangles):
        self.triangles = triangles
        self.edges = self.edgemaker()

    """ With these functions we instantiate some stuff"""
    def edgemaker(self):
        total_edge_list = [edge for triangle in self.triangles for edge in triangle.edges]
        total_edge_list = [edge for edge in total_edge_list if total_edge_list.count(edge) == 1]
        return total_edge_list

    def vertmaker(self):
        vertex_list = []
        for triangle in self.triangles:
            vertex_list.extend(triangle.vertex_returner())
        vertex_list = list(set(vertex_list))
        # vertex_list = [elem for  elem in vertex_list if elem not in self.inside()]
        return vertex_list

    def __eq__(self, other):
        xmin_s = min([elem.v1[0] for elem in self.triangles])
        ymin_s = min([elem.v1[1] for elem in self.triangles])
        xmin_o = min([elem.v1[0] for elem in other.triangles])
        ymin_o = min([elem.v1[1] for elem in other.triangles])
        return all(triangle in other.translate(xmin_s-xmin_o,ymin_s-ymin_o).triangles for triangle in self.triangles)


    def copy(self):
        return Shape(self.triangles)

    def orientations(self):
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
        new_orientations_list = []
        for orientation in orientation_list:
            if orientation not in new_orientations_list:
                new_orientations_list.append(orientation)
        return new_orientations_list

    """ With these functions we edit the shape"""
    def translate(self, xval, yval):
        new_triangles = []
        for triangle in self.triangles:
            new_triangles.append(triangle.translate(xval, yval))
        return Shape(new_triangles)

    def translate_rel(self, tri1, tri2):
        return self.translate(tri1.v1[0]-tri2.v1[0], tri1.v1[1]-tri2.v1[1])

    def flip(self):
        new_triangles = []
        for triangle in self.triangles:
            new_triangles.append(triangle.flip())
        return Shape(new_triangles)

    def turn60(self):
        new_triangles = []
        for triangle in self.triangles:
            new_triangles.append(triangle.turn60())
        return Shape(new_triangles)

    def inside_remover(self):
        inside_list = []
        for triangle in self.triangles:
            if all(edge not in self.edges for edge in triangle.edges):
                inside_list.append(triangle)
        new_triangles = [elem for elem in self.triangles if elem not in inside_list]
        return new_triangles

    def outside(self):
        hexlist = []
        for vert in self.vertmaker():
            hexlist.extend(hexagon_maker(vert[0]-1,vert[1]))
        res = []
        for elem in hexlist:
            if elem not in res:
                res.append(elem)
        res = [elem for elem in res if elem not in self.triangles]
        return res

    def corona_maker(self, base_orientations, bookkeeping=False):
        def not_occupied_in(elem, config):
            config_triangles = []
            for shape in config:
                config_triangles.extend(shape.triangles)
            return (elem not in config_triangles)


        base_orientations_boundaries = [orientation.inside_remover() for orientation in base_orientations ]
        bookkeeper = []
        possible_config = []
        outside_list = self.outside()
        #print(f"the outside list length is {len(outside_list)}")
        for i in range(len(outside_list)):
            print(f" we are now at {int((i+1)/len(outside_list)*100)}% ")
            elem = outside_list[i]
            if len(possible_config) == 0:
                #print("going through the zero loop")
                for index in range(len(base_orientations)):
                    for elem3 in [elem2 for elem2 in base_orientations_boundaries[index] if elem2.up == elem.up]:
                        #print(elem.up, elem3.up)
                        new_shape = base_orientations[index].translate_rel(elem, elem3)
                        if all(triangle not in self.triangles for triangle in new_shape.triangles):
                            possible_config.append([new_shape])
                #print(" zero loop appending ")
                if bookkeeping:
                    bookkeeper.append(possible_config)

            else:
                new_possible_config = []
                for config in possible_config:
                    if not_occupied_in(elem, config):
                        for index in range(len(base_orientations)):
                            for elem3 in [elem2 for elem2 in base_orientations_boundaries[index] if elem2.up == elem.up]:
                                new_shape = base_orientations[index].translate_rel(elem, elem3)
                                if all(triangle not in self.triangles and not_occupied_in(triangle, config) for triangle in new_shape.triangles):
                                    new_config = config.copy()
                                    new_config.append(new_shape)
                                    new_possible_config.append(new_config)
                                else:
                                    continue
                    else:
                        #print(f" its occupied in the config? ")
                        new_possible_config.append(config)

                possible_config = new_possible_config.copy()
                #print(possible_config)
                if bookkeeping:
                    bookkeeper.append(possible_config)
        return bookkeeper if bookkeeping else possible_config

    """ With these function we output a list to be put into a plot
    as input we specify the color we want the line to have

    1) plot_data will give the edges of the shape
    2) outside_plot_data will give the edges of the surrounding triangles """

    def plot_data(self, color= "r"):
        plottinglist = []
        for edge in self.edges:
            el = list(edge)
            xcoords = [el[0][0]-0.5 * el[0][1], el[1][0]- 0.5 * el[1][1]]
            ycoords = [0.5*sqrt(3)*el[0][1], 0.5*sqrt(3)*el[1][1]]
            plottinglist.extend([xcoords, ycoords, color])
        return plottinglist

    def outside_plot_data(self):
        plottinglist = []
        for elem in self.outside():
            for edge in elem.edges:
                el = list(edge)
                xcoords = [el[0][0], el[1][0]]
                ycoords = [el[0][1]-el[0][0], el[1][1]-el[1][0]]
                plottinglist.extend([xcoords, ycoords, "r-"])
        return plottinglist


def hexagon_maker(x,y):
    down_triangles = [Triangle(x,y, up=False), Triangle(x+1,y+1, up=False), Triangle(x+1,y, up=False)]
    up_triangles = [Triangle(x,y), Triangle(x,y-1), Triangle(x+1,y)]
    return down_triangles+up_triangles


def triangle_of_hexes():
    new_list =  [
        hexagon_maker(0,0),
        hexagon_maker(3,0),
        hexagon_maker(6,0),
        hexagon_maker(1,-1),
        hexagon_maker(4,-1),
        hexagon_maker(2,-2),
        hexagon_maker(0,-3),
        hexagon_maker(3,-3),
        hexagon_maker(1,-4),
        hexagon_maker(0,-6),
        ]
    hexlist = []
    for hex in new_list:
        hexlist.extend(hex)
    return hexlist
