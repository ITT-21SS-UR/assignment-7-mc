import sys
from enum import Enum

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.flowchart import Flowchart, Node
from DIPPID_pyqtnode import BufferNode, DIPPIDNode

# Author: Claudia
# Reviewer: Martina
class FlowchartType(Enum):
    dippid = "DIPPID"
    buffer = "Buffer"
    plot_widget = "PlotWidget"
    normal_vector = "NormalVector"
    log = "Log"


# TODO is it allowed to move it to DIPPID_pyqtnode and modify this file? else move to separate class
class NormalVectorNode(Node):
    nodeName = FlowchartType.normal_vector.value

    def __init__(self, name):
        # TODO what is needed for normal vector
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }
        # TODO
        self.buffer_size = 32
        self._buffer = np.array([])
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        # TODO
        self._buffer = np.append(self._buffer, kwds['dataIn'])[-self.buffer_size:]

        return {'dataOut': self._buffer}


# fclib.registerNodeType(NormalVectorNode, [("NormalVector",)])


# TODO is it allowed to move it to DIPPID_pyqtnode? else move to separate class
class LogNode(Node):
    nodeName = FlowchartType.log.value

    # TODO a LogNode that reads values (e.g., accelerometer data) from its input terminal and writes them to stdout.
    def __init__(self, name):
        # TODO what is needed for log
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }
        # TODO
        self.buffer_size = 32
        self._buffer = np.array([])
        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        # TODO
        self._buffer = np.append(self._buffer, kwds['dataIn'])[-self.buffer_size:]

        return {'dataOut': self._buffer}


# fclib.registerNodeType(LogNode, [("Log",)])


class MainWindow(QtWidgets.QWidget):

    def __init__(self, port_number=None):
        super(MainWindow, self).__init__()

        self.__port_number = port_number

        self.__setup_main_window()
        self.__setup_flowchart()

    def __setup_main_window(self):
        self.setWindowTitle("Analyze")
        self.move(QtWidgets.qApp.desktop().availableGeometry(
            self).center() - self.rect().center())

    def __setup_flowchart(self):
        self.__flow_chart = Flowchart(terminals={})
        self.__layout = QtGui.QGridLayout()
        self.__layout.addWidget(self.__flow_chart.widget(), 0, 0, 2, 1)

        self.__setup_dippid()

        # TODO change all position values for flowchart
        self.__setup_accelerometer_x()
        self.__setup_accelerometer_y()
        self.__setup_accelerometer_z()
        self.__setup_normal_vector()

        self.setLayout(self.__layout)

    def __setup_dippid(self):
        self.__dippid_node = self.__flow_chart.createNode("DIPPID", pos=(0, 0))
        self.__dippid_node.set_port(self.__port_number)

    def __setup_accelerometer_x(self):
        plot_widget = pg.PlotWidget()
        self.__layout.addWidget(plot_widget, 0, 1)
        plot_widget.setTitle("accelerometer x")
        plot_widget.setYRange(0, 1)  # TODO valid range

        plot_widget_node = self.__flow_chart.createNode(FlowchartType.plot_widget.value, pos=(0, -150))
        plot_widget_node.setPlot(plot_widget)

        buffer_node = self.__flow_chart.createNode(FlowchartType.buffer.value, pos=(150, 0))
        self.__flow_chart.connectTerminals(self.__dippid_node["accelX"], buffer_node["dataIn"])
        self.__flow_chart.connectTerminals(buffer_node["dataOut"], plot_widget_node["In"])

    def __setup_accelerometer_y(self):
        plot_widget = pg.PlotWidget()
        self.__layout.addWidget(plot_widget, 0, 2)
        plot_widget.setTitle("accelerometer y")
        plot_widget.setYRange(0, 1)  # TODO valid range

        plot_widget_node = self.__flow_chart.createNode(FlowchartType.plot_widget.value, pos=(0, -150))
        plot_widget_node.setPlot(plot_widget)

        buffer_node = self.__flow_chart.createNode(FlowchartType.buffer.value, pos=(150, 0))
        self.__flow_chart.connectTerminals(self.__dippid_node["accelY"], buffer_node["dataIn"])
        self.__flow_chart.connectTerminals(buffer_node["dataOut"], plot_widget_node["In"])

    def __setup_accelerometer_z(self):
        plot_widget = pg.PlotWidget()
        self.__layout.addWidget(plot_widget, 1, 1)
        plot_widget.setTitle("accelerometer z")
        plot_widget.setYRange(0, 1)  # TODO valid range

        plot_widget_node = self.__flow_chart.createNode(FlowchartType.plot_widget.value, pos=(0, -150))
        plot_widget_node.setPlot(plot_widget)

        buffer_node = self.__flow_chart.createNode(FlowchartType.buffer.value, pos=(150, 0))
        self.__flow_chart.connectTerminals(self.__dippid_node["accelZ"], buffer_node["dataIn"])
        self.__flow_chart.connectTerminals(buffer_node["dataOut"], plot_widget_node["In"])

    def __setup_normal_vector(self):
        # TODO setup normal vector
        plot_widget = pg.PlotWidget()
        self.__layout.addWidget(plot_widget, 1, 2)
        plot_widget.setTitle("normal vector")
        plot_widget.setYRange(0, 1)  # TODO valid range

        plot_widget_node = self.__flow_chart.createNode(FlowchartType.plot_widget.value, pos=(0, -150))
        plot_widget_node.setPlot(plot_widget)


def start_program():
    # TODO what should be done with the port number -> set port of MainWindow Text in DIPPID
    # port_number = read_port_number()  # TODO use that
    port_number = 5700  # TODO remove after debugging / finished

    app = QtGui.QApplication([])
    main_window = MainWindow(port_number)
    main_window.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        sys.exit(QtGui.QApplication.instance().exec_())

    sys.exit(app.exec_())


def read_port_number():
    if len(sys.argv) < 2:
        sys.stderr.write("Please give a port number as argument (-_-)\n")
        sys.exit(1)

    return sys.argv[1]


if __name__ == '__main__':
    start_program()
