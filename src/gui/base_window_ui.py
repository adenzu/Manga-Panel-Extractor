# Form implementation generated from reading ui file 'res\designer\base_window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(374, 251)
        MainWindow.setIconSize(QtCore.QSize(24, 24))
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.input_directory_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.input_directory_label.setObjectName("input_directory_label")
        self.verticalLayout_2.addWidget(self.input_directory_label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.input_directory_line_edit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.input_directory_line_edit.setObjectName("input_directory_line_edit")
        self.horizontalLayout_2.addWidget(self.input_directory_line_edit)
        self.input_directory_browse_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.input_directory_browse_button.setObjectName("input_directory_browse_button")
        self.horizontalLayout_2.addWidget(self.input_directory_browse_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.output_directory_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.output_directory_label.setObjectName("output_directory_label")
        self.verticalLayout_2.addWidget(self.output_directory_label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.output_directory_line_edit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.output_directory_line_edit.setObjectName("output_directory_line_edit")
        self.horizontalLayout_3.addWidget(self.output_directory_line_edit)
        self.output_directory_browse_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.output_directory_browse_button.setObjectName("output_directory_browse_button")
        self.horizontalLayout_3.addWidget(self.output_directory_browse_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.output_separate_folders_check_box = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.output_separate_folders_check_box.setObjectName("output_separate_folders_check_box")
        self.horizontalLayout.addWidget(self.output_separate_folders_check_box)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.merge_mode_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.merge_mode_label.setObjectName("merge_mode_label")
        self.horizontalLayout_6.addWidget(self.merge_mode_label)
        self.merge_mode_combo_box = QtWidgets.QComboBox(parent=self.centralwidget)
        self.merge_mode_combo_box.setObjectName("merge_mode_combo_box")
        self.merge_mode_combo_box.addItem("")
        self.merge_mode_combo_box.addItem("")
        self.merge_mode_combo_box.addItem("")
        self.horizontalLayout_6.addWidget(self.merge_mode_combo_box)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.progress_bar = QtWidgets.QProgressBar(parent=self.centralwidget)
        self.progress_bar.setEnabled(False)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setInvertedAppearance(False)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout_2.addWidget(self.progress_bar)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.start_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.start_button.setObjectName("start_button")
        self.horizontalLayout_5.addWidget(self.start_button)
        self.cancel_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setObjectName("cancel_button")
        self.horizontalLayout_5.addWidget(self.cancel_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Manga Panel Extractor"))
        self.input_directory_label.setText(_translate("MainWindow", "Input Directory"))
        self.input_directory_browse_button.setText(_translate("MainWindow", "Browse"))
        self.output_directory_label.setText(_translate("MainWindow", "Output Directory"))
        self.output_directory_browse_button.setText(_translate("MainWindow", "Browse"))
        self.output_separate_folders_check_box.setToolTip(_translate("MainWindow", "<html><head/><body><p>Create folders for every input manga page and extract their respective panels into them.</p></body></html>"))
        self.output_separate_folders_check_box.setText(_translate("MainWindow", "Output To Separate Folders"))
        self.merge_mode_label.setToolTip(_translate("MainWindow", "<html><head/><body><p>None - Extract all panels separately</p><p>Vertically - Merge panels of vertical stripes</p><p>Horizontally - Merge panels of horizontal stripes</p></body></html>"))
        self.merge_mode_label.setText(_translate("MainWindow", "Merge Mode"))
        self.merge_mode_combo_box.setToolTip(_translate("MainWindow", "<html><head/><body><p>None - Extract all panels separately</p><p>Vertical - Merge panels of vertical stripes</p><p>Horizontal - Merge panels of horizontal stripes</p></body></html>"))
        self.merge_mode_combo_box.setItemText(0, _translate("MainWindow", "None"))
        self.merge_mode_combo_box.setItemText(1, _translate("MainWindow", "Vertical"))
        self.merge_mode_combo_box.setItemText(2, _translate("MainWindow", "Horizontal"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.cancel_button.setText(_translate("MainWindow", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
