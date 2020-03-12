#!/usr/bin/env python3


import sys
import platform
import re
from pathlib import Path
import formula
from PySide2.QtCore import Slot
from PySide2.QtGui import QIntValidator, QPixmap
from PySide2.QtWidgets import (QLabel, QLineEdit, QPushButton, QApplication,
                               QSpinBox, QFileDialog, QGridLayout, QWidget,
                               QCheckBox, QGroupBox, QHBoxLayout, QMessageBox,
                               QErrorMessage, QMainWindow, QTabWidget, QAction)


class Tab(QTabWidget):
    def __init__(self, parent=None):
        super(Tab, self).__init__(parent)
        self.save_widget = SaveWidget()
        self.test_widget = TestWidget(options=self.save_widget)
        self.addTab(self.test_widget, 'Math Test')
        self.addTab(self.save_widget, 'Options')


class TestWidget(QWidget):
    def __init__(self, parent=None, options=None):
        super(TestWidget, self).__init__(parent)
        self.options = options
        self.results = []
        self.tests = []
        self.index = 0
        self.n_number = 1
        self.total_try = 0
        self.index_label = QLabel(self.tr('Test #'))
        self.start = QPushButton(self.tr('Start'))
        self.stop = QPushButton(self.tr('Stop'))
        self.next = QPushButton(self.tr('Next'))
        self.correct = QLabel()
        self.smile_face = QPixmap('./images/smile.png')
        self.sad_face = QPixmap('./images/sad.png')
        self.correct.setPixmap(self.smile_face)
        self.start.setDefault(True)
        self.next.setEnabled(False)
        self.stop.setEnabled(False)

        self.formula = QLineEdit()
        self.formula.setReadOnly(True)
        min_height = 50
        self.formula.setMinimumHeight(min_height)
        self.answer = QLineEdit()
        self.answer.setMinimumHeight(min_height)
        self.answer.setValidator(QIntValidator())

        layout = QGridLayout()
        row = 0
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(self.tr('Total tests')))
        hbox.addWidget(self.options.total)
        layout.addWidget(self.index_label, row, 0)
        layout.addLayout(hbox, row, 2)
        layout.addWidget(self.start, row, 3)
        layout.addWidget(self.stop, row, 4)
        row += 1
        layout.addWidget(self.formula, row, 0)
        layout.addWidget(self.answer, row, 2)
        layout.addWidget(self.next, row, 3)
        layout.addWidget(self.correct, row, 4)
        layout.setColumnStretch(0, 1)
        self.setLayout(layout)

        self.start.clicked.connect(self.start_test)
        self.stop.clicked.connect(self.stop_test)
        self.next.clicked.connect(self.next_test)

    @Slot()
    def next_test(self):
        answer = self.answer.text()
        if not answer:
            self.options.err_dialog('must answer before click next')
            return None
        correct = int(answer) == formula.eval_expr(self.tests[self.index])
        if correct:
            self.correct.setPixmap(self.smile_face)
            self.answer.clear()
            self.index += 1
            if self.index < self.n_number:
                self.set_test(self.index)
                self.index_label.setText(self.tr('Rule %d' % (self.index + 1)))
        else:
            self.correct.setPixmap(self.sad_face)
        self.total_try += 1
        if self.index == len(self.tests):
            self.show_summary()
            self.stop_test()
            return

    def correct_rate(self):
        return self.index / self.total_try

    def show_summary(self):
        msg = 'Total attempt: %s Correct: %s Rate: %s' % (
            self.total_try, self.index, '{0:.0%}'.format(self.correct_rate()))
        self.options.info_dialog(msg)

    @Slot()
    def start_test(self):
        (filename, upper_limit, lower_limit,
         self.n_number, total_tests, operators) = self.options.collect_input()
        # skip filename check in test mode
        filename = True
        err_msg = self.options.check_input(filename,
                                           upper_limit, lower_limit, operators)
        if err_msg:
            self.options.err_dialog(err_msg)
        else:
            self.tests, self.results = formula.gen_test(
                operators, upper_limit, lower_limit, self.n_number, total_tests)
            for w in (self.next, self.start, self.stop):
                self.toggle_enable(w)
            self.set_test(self.index)
            self.index_label.setText(self.tr('Rule %d' % (self.index + 1)))
            self.next.setDefault(True)

    def set_test(self, index):
        self.formula.setText(self.tests[index])

    def toggle_enable(self, w):
        if w.isEnabled():
            w.setEnabled(False)
        else:
            w.setEnabled(True)

    @Slot()
    def stop_test(self):
        for w in (self.next, self.start, self.stop):
            self.toggle_enable(w)
        self.formula.clear()
        self.answer.clear()
        self.index = 0
        self.correct_try = 0
        self.total_try = 0
        self.index_label.setText(self.tr('Rule #'))


class SaveWidget(QWidget):

    def __init__(self, parent=None):
        super(SaveWidget, self).__init__(parent)
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
        (filename, upper_limit, lower_limit,
         n_number, total_tests, operators) = self.collect_input()
        err_msg = self.check_input(filename,
                                   upper_limit, lower_limit, operators)
        if err_msg:
            self.err_dialog(err_msg)
        else:
            split_num = formula.gen_split(n_number)
            tests, results = formula.gen_test(
                operators, upper_limit, lower_limit, n_number, total_tests)
            formula.gen_xlsx(filename, tests, results, n_number, split_num)
            msg = '%s generated!\n' % filename
            self.info_dialog(msg)

    def check_input(self, filename, upper_limit, lower_limit, operators):
        err_msg = ''
        if not filename:
            err_msg += 'missing file name\n'
        if upper_limit < lower_limit:
            err_msg += 'wrong setting, min number is larger than max number\n'
        if len(operators) == 0:
            err_msg += 'at least one operator must be checked\n'
        return err_msg

    def collect_input(self):
        filename = self.file.text()
        upper_limit = self.upper_spin.value()
        lower_limit = self.lower_spin.value()
        n_number = self.n_spin.value()
        total_tests = self.total.value()
        operators = self.collect_operators()
        return (filename, upper_limit, lower_limit,
                n_number, total_tests, operators)

    def info_dialog(self, msg):
        dial = QMessageBox()
        dial.setText(msg)
        dial.exec_()

    def err_dialog(self, msg):
        err = QErrorMessage()
        err.showMessage(msg)
        err.exec_()

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
        self.setWindowTitle('KidsMath')

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
    widget = Tab()
    # QMainWindow using QWidget as central widget
    window = MainWindow(widget)
    # window.resize(800, 600)
    window.show()

    # Execute application
    sys.exit(app.exec_())
