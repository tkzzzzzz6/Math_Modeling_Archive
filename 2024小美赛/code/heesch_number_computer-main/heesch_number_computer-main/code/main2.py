from hexshapes import Hexagon, HShape
import ast
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Circle

import numpy as np

def parametrization(el):
    xcoord = el[0]-0.5 * el[1]
    ycoord = 0.5*np.sqrt(3)*el[1]
    return (xcoord, ycoord)

def shapedrawer(shape, axes, color):
    for hex in shape.hexes:
        hexagon = RegularPolygon(parametrization(hex.origin), numVertices=6, orientation = 1/6 *np.pi ,radius= 1, alpha=1, color= color)
        axes.add_patch(hexagon)
        edgedata = hex.edgedata
        for i in range(len(edgedata)):
            if edgedata[i] == 1:
                coord = parametrization(hex.origin)
                coord = (coord[0]+2/3*np.cos(i*1/6*2*np.pi-1/2*np.pi), coord[1]+2/3*np.sin(i*1/6*2*np.pi-1/2*np.pi))
                circle = Circle(coord, radius = 1/16, color="k")
                axes.add_patch(circle)
            elif edgedata[i] == -1:
                coord = parametrization(hex.origin)
                coord = (coord[0]+2/3*np.cos(i*1/6*2*np.pi-1/2*np.pi), coord[1]+2/3*np.sin(i*1/6*2*np.pi-1/2*np.pi))
                circle = Circle(coord, radius = 1/16, color="w")
                axes.add_patch(circle)
with open('./plotlist.txt', 'r') as text:
    data = ast.literal_eval(text.readline())

axs = plt.subplot()
plottinglist = []
if data["type"] == "base":
    base = HShape( [Hexagon(*elem) for elem in data["data"]["base"]])
    shapedrawer(base, axs, "thistle")
    plottinglist.extend(base.plot_data("blue"))

elif data["type"] == "corona":
    config = data["data"]["corona"]
    for pre_shape in config:
        shape = HShape( [Hexagon(*elem) for elem in pre_shape] )
        shapedrawer(shape, axs, "lightseagreen")
        plottinglist.extend(shape.plot_data("red"))
    base = HShape( [Hexagon(*elem) for elem in data["data"]["base"]])
    shapedrawer(base, axs, "turquoise")
    plottinglist.extend(base.plot_data("blue"))

elif data["type"] == "heesch":
    heesch_data = data["data"]["heesch"]
    for index in range(len(heesch_data)):
        corona = heesch_data[index]
        for pre_shape in corona:
            shape = HShape( [Hexagon(*elem) for elem in pre_shape] )
            color = "lightseagreen" if index%2 == 0 else "aquamarine"
            shapedrawer(shape, axs, color)
            plottinglist.extend(shape.plot_data("blue"))

    base = HShape( [Hexagon(*elem) for elem in data["data"]["base"]])
    shapedrawer(base, axs, "aquamarine")
    plottinglist.extend(base.plot_data("blue"))

elif data["type"] == "corona2":
    first = data["data"]["first"]
    for pre_shape in first:
        shape = HShape( [Hexagon(*elem) for elem in pre_shape] )
        shapedrawer(shape, axs, "lightseagreen")
        plottinglist.extend(shape.plot_data("red"))

    second = data["data"]["second"]
    for pre_shape in second:
        shape = HShape( [Hexagon(*elem) for elem in pre_shape] )
        shapedrawer(shape, axs, "turquoise")
        plottinglist.extend(shape.plot_data("blue"))

    base = HShape( [Hexagon(*elem) for elem in data["data"]["base"]])
    shapedrawer(base, axs, "aquamarine")
    plottinglist.extend(base.plot_data("k"))


axs.plot(*(plottinglist), linewidth=0.3)
plt.autoscale(enable = True)
axs.set_aspect("equal")
plt.axis('off')
plt.show()
