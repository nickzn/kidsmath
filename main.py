#!/usr/bin/env python3


import sys
import platform
import re
from pathlib import Path
import kidsmath
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (QLabel, QLineEdit, QPushButton, QApplication,
                               QSpinBox, QFileDialog, QGridLayout, QWidget,
                               QCheckBox, QGroupBox, QHBoxLayout, QMessageBox,
                               QErrorMessage, QMainWindow, QAction)


class Widget(QWidget):

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        # Create widgets
        self.lower_label = QLabel(self.tr('Min'))
        self.lower_spin = QSpinBox(self)
        self.lower_spin.setMinimum(1)
        self.upper_label = QLabel(self.tr('Max'))
        self.upper_default = 10
        self.upper_spin = QSpinBox(self)
        self.upper_spin.setMinimum(1)
        self.upper_spin.setValue(self.upper_default)
        self.n_label = QLabel(self.tr('Number per formula'))
        self.n_spin = QSpinBox(self)
        self.n_spin.setMinimum(2)
        self.n_spin.setMaximum(4)
        self.total_label = QLabel(self.tr('Total tests'))
        self.total = QSpinBox(self)
        self.total.setMinimum(10)
        self.total.setMaximum(1000)
        self.total_default = 100
        self.total.setValue(self.total_default)
        self.total.setSingleStep(10)

        self.plus_cb = QCheckBox('+')
        self.minus_cb = QCheckBox('-')
        self.multi_cb = QCheckBox('×')
        self.divide_cb = QCheckBox('÷')
        self.plus_cb.setChecked(True)
        self.minus_cb.setChecked(True)

        self.file_name = self.tr('%s/kidsmath.xlsx' % str(Path.home()))
        self.file_label = QLabel(self.tr('Save File:'))
        self.file = QLineEdit(self.tr(self.file_name))
        self.browse_btn = QPushButton(self.tr('Browse'))
        self.save_btn = QPushButton(self.tr('Save'))
        # Create layout and add widgets
        hbox = QHBoxLayout()
        hbox.addWidget(self.plus_cb)
        hbox.addWidget(self.minus_cb)
        hbox.addWidget(self.multi_cb)
        hbox.addWidget(self.divide_cb)
        self.group_box = QGroupBox(self.tr('Operators:'))
        self.group_box.setLayout(hbox)

        layout = QGridLayout()
        row = 0
        layout.addWidget(QLabel(self.tr('Setting:')), row, 0)
        layout.addWidget(self.lower_label, row, 1)
        layout.addWidget(self.lower_spin, row, 2)
        layout.addWidget(self.upper_label, row, 3)
        layout.addWidget(self.upper_spin, row, 4)
        layout.addWidget(self.n_label, row, 5)
        layout.addWidget(self.n_spin, row, 6)
        layout.addWidget(self.total_label, row, 7)
        layout.addWidget(self.total, row, 8)
        layout.addWidget(self.group_box, row, 9, 1, 2)
        row += 1
        layout.addWidget(self.file_label, row, 0)
        layout.addWidget(self.file, row, 1, 1, 8)
        layout.addWidget(self.browse_btn, row, 9)
        layout.addWidget(self.save_btn, row, 10)
        layout.setColumnStretch(8, 1)
        self.setLayout(layout)

        self.browse_btn.clicked.connect(self.set_file)
        self.save_btn.clicked.connect(self.save_file)

    @Slot()
    def set_file(self):
        self.file_name, f = QFileDialog.getOpenFileName(
            self, self.tr('Save Ffile'),
            filter=self.tr('Spreadsheets (*.xlsx)'))
        if self.file_name:
            self.file.setText(self.file_name)

    @Slot()
    def save_file(self):
        err_msg = ''
        filename = self.file.text()
        upper_limit = self.upper_spin.value()
        lower_limit = self.lower_spin.value()
        n_number = self.n_spin.value()
        total_tests = self.total.value()
        if not filename:
            err_msg += 'missing file name\n'
        if upper_limit < lower_limit:
            err_msg += 'wrong setting, min number is larger than max number\n'
        operators = self.collect_operators()
        if len(operators) == 0:
            err_msg += 'at least one operator must be checked\n'

        if err_msg:
            self.err_dialog(err_msg)
        else:
            split_num = kidsmath.gen_split(n_number)
            tests, results = kidsmath.gen_test(
                operators, upper_limit, lower_limit, n_number, total_tests)
            kidsmath.gen_xlsx(filename, tests, results, n_number, split_num)
            msg = '%s generated!\n' % filename
            self.info_dialog(msg)

    def info_dialog(self, msg):
        dial = QMessageBox()
        dial.setText(msg)
        dial.exec_()

    def err_dialog(self, msg):
        err = QErrorMessage()
        err.showMessage(msg)
        err.exec_()

    @Slot()
    def collect_operators(self):
        operators = []
        if self.plus_cb.isChecked():
            operators.append('+')
        if self.minus_cb.isChecked():
            operators.append('-')
        if self.multi_cb.isChecked():
            operators.append('*')
        if self.divide_cb.isChecked():
            operators.append('/')
        return operators


class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle('Kidsmath')

        # Menu
        self.menu = self.menuBar()
        if re.match(r'Darwin', platform.platform()):
            self.menu.setNativeMenuBar(False)
        self.file_menu = self.menu.addMenu('File')

        # Exit QAction
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.exit_app)

        self.file_menu.addAction(exit_action)
        self.setCentralWidget(widget)

    @Slot()
    def exit_app(self, checked):
        QApplication.quit()


if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    # QWidget
    widget = Widget()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    # window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec_())
