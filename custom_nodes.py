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
        # TODO what is needed for normal vector
        terminals = {
            "dataIn": dict(io="in"),
            "dataOut": dict(io="out"),
        }
        # TODO
        self.buffer_size = 32
        self._buffer = np.array([])
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        # TODO
        self._buffer = np.append(self._buffer, kwds["dataIn"])[-self.buffer_size:]

        return {"dataOut": self._buffer}


fclib.registerNodeType(NormalVectorNode, [(FlowchartType.normal_vector.value,)])


class LogNode(Node):
    nodeName = FlowchartType.log.value

    def __init__(self, name):
        terminals = {
            "accelX": dict(io="in"),
            "accelY": dict(io="in"),
            "accelZ": dict(io="in"),
            "dataOut": dict(io="out")
        }

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwdargs):
        log = {
            "accelX": kwdargs["accelX"][0],
            "accelY": kwdargs["accelY"][0],
            "accelZ": kwdargs["accelZ"][0]
        }

        print(log, flush=True)

        return log


fclib.registerNodeType(LogNode, [(FlowchartType.log.value,)])
