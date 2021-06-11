import sys

import pyqtgraph as pg
from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.flowchart import Flowchart

from DIPPID_pyqtnode import BufferNode, DIPPIDNode
from custom_nodes import LogNode, NormalVectorNode, FlowchartType


# Author: Claudia
# Reviewer: Martina
class MainWindow(QtWidgets.QWidget):

    def __init__(self, port_number=None):
        super(MainWindow, self).__init__()

        self.__port_number = port_number

        self.__setup_flowchart()
        self.__setup_main_window()

    def __setup_main_window(self):
        self.setWindowTitle("Analyze")
        self.move(QtWidgets.qApp.desktop().availableGeometry(
            self).center() - self.rect().center())

    def __setup_flowchart(self):
        self.__flow_chart = Flowchart(terminals={})
        self.__layout = QtGui.QGridLayout()
        self.__layout.addWidget(self.__flow_chart.widget(), 0, 0, 2, 1)

        self.__setup_dippid()

        self.__setup_accelerometer_x()
        self.__setup_accelerometer_y()
        self.__setup_accelerometer_z()
        self.__setup_normal_vector()

        self.__setup_log()

        self.setLayout(self.__layout)

    def __setup_dippid(self):
        self.__dippid_node = self.__flow_chart.createNode(FlowchartType.dippid.value, pos=(0, 0))
        self.__dippid_node.set_port(self.__port_number)

    def __setup_accelerometer_x(self):
        plot_widget = pg.PlotWidget()
        plot_widget.setTitle("accelerometer x")
        plot_widget.setYRange(-2, 2)
        self.__layout.addWidget(plot_widget, 0, 1)

        plot_widget_node = self.__flow_chart.createNode(FlowchartType.plot_widget.value, pos=(300, -100))
        plot_widget_node.setPlot(plot_widget)

        buffer_node = self.__flow_chart.createNode(FlowchartType.buffer.value, pos=(150, -100))

        self.__flow_chart.connectTerminals(self.__dippid_node["accelX"], buffer_node["dataIn"])
        self.__flow_chart.connectTerminals(buffer_node["dataOut"], plot_widget_node["In"])

    def __setup_accelerometer_y(self):
        plot_widget = pg.PlotWidget()
        plot_widget.setTitle("accelerometer y")
        plot_widget.setYRange(-2, 2)
        self.__layout.addWidget(plot_widget, 0, 2)

        plot_widget_node = self.__flow_chart.createNode(FlowchartType.plot_widget.value, pos=(300, -50))
        plot_widget_node.setPlot(plot_widget)

        buffer_node = self.__flow_chart.createNode(FlowchartType.buffer.value, pos=(150, -50))

        self.__flow_chart.connectTerminals(self.__dippid_node["accelY"], buffer_node["dataIn"])
        self.__flow_chart.connectTerminals(buffer_node["dataOut"], plot_widget_node["In"])

    def __setup_accelerometer_z(self):
        plot_widget = pg.PlotWidget()
        plot_widget.setTitle("accelerometer z")
        plot_widget.setYRange(-2, 2)
        self.__layout.addWidget(plot_widget, 1, 1)

        plot_widget_node = self.__flow_chart.createNode(FlowchartType.plot_widget.value, pos=(300, 80))
        plot_widget_node.setPlot(plot_widget)

        buffer_node = self.__flow_chart.createNode(FlowchartType.buffer.value, pos=(150, 80))

        self.__flow_chart.connectTerminals(self.__dippid_node["accelZ"], buffer_node["dataIn"])
        self.__flow_chart.connectTerminals(buffer_node["dataOut"], plot_widget_node["In"])

    def __setup_normal_vector(self):
        plot_widget = pg.PlotWidget()
        plot_widget.setTitle("normal vector")
        # TODO better range?
        plot_widget.setYRange(-2, 2)
        plot_widget.setXRange(-2, 2)
        self.__layout.addWidget(plot_widget, 1, 2)

        plot_widget_node = self.__flow_chart.createNode(FlowchartType.plot_widget.value, pos=(300, 130))
        plot_widget_node.setPlot(plot_widget)

        self.__normal_vector_node = self.__flow_chart.createNode(FlowchartType.normal_vector.value, pos=(150, 130))

        self.__flow_chart.connectTerminals(self.__dippid_node["accelX"], self.__normal_vector_node["accelX"])
        self.__flow_chart.connectTerminals(self.__dippid_node["accelZ"], self.__normal_vector_node["accelZ"])
        self.__flow_chart.connectTerminals(self.__normal_vector_node["rotation"], plot_widget_node["In"])

    def __setup_log(self):
        log_node = self.__flow_chart.createNode(FlowchartType.log.value, pos=(150, 0))

        self.__flow_chart.connectTerminals(self.__dippid_node["accelX"], log_node["accelX"])
        self.__flow_chart.connectTerminals(self.__dippid_node["accelY"], log_node["accelY"])
        self.__flow_chart.connectTerminals(self.__dippid_node["accelZ"], log_node["accelZ"])
        self.__flow_chart.connectTerminals(self.__normal_vector_node["rotation"], log_node["rotation"])


def start_program():
    port_number = read_port_number()

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
