import math
from enum import Enum

import numpy as np
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart import Node


# Author: Claudia
# Reviewer: Martina
class FlowchartType(Enum):
    dippid = "DIPPID"
    buffer = "Buffer"
    plot_widget = "PlotWidget"
    normal_vector = "NormalVector"
    log = "Log"


class NormalVectorNode(Node):
    nodeName = FlowchartType.normal_vector.value

    def __init__(self, name):
        terminals = {
            "accelX": dict(io="in"),
            "accelZ": dict(io="in"),
            "rotation": dict(io="out")
        }

        self.__rotation_vectors = np.array([])
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        # TODO which one
        #   this looks a bit different from video
        # normal_x = kwargs["accelZ"][0]
        # normal_y = kwargs["accelX"][0]

        # perspective from lying on the table (similar to video)
        normal_x = -kwargs["accelX"][0]
        normal_y = kwargs["accelZ"][0]

        self.__rotation_vectors = np.array(((0, 0), (normal_x, normal_y)))

        return {"rotation": self.__rotation_vectors}

    @staticmethod
    def calculate_rotation_in_degrees(point):
        y = point[0]
        x = point[1]

        # arc tangent of y/x in degrees
        return math.degrees(math.atan2(y, x))


fclib.registerNodeType(NormalVectorNode, [(FlowchartType.normal_vector.value,)])


class LogNode(Node):
    nodeName = FlowchartType.log.value

    def __init__(self, name):
        terminals = {
            "accelX": dict(io="in"),
            "accelY": dict(io="in"),
            "accelZ": dict(io="in"),
            "rotation": dict(io="in"),
            "dataOut": dict(io="out")
        }

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        log = {
            "accelX": kwargs["accelX"][0],
            "accelY": kwargs["accelY"][0],
            "accelZ": kwargs["accelZ"][0],
            "rotation_in_degrees": NormalVectorNode.calculate_rotation_in_degrees(kwargs["rotation"][1])
        }

        print(log)

        return log


fclib.registerNodeType(LogNode, [(FlowchartType.log.value,)])
