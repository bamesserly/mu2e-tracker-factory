# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wire_tensioner_window.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 500)
        self.label_4 = QLabel(Dialog)
        self.label_4.setGeometry(QRect(10, 455, 55, 21))
        font = QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setFrameShape(QFrame.NoFrame)
        self.label_4.setObjectName("label_4")
        self.statuslabel = QLabel(Dialog)
        self.statuslabel.setGeometry(QRect(80, 455, 421, 21))
        self.statuslabel.setFont(font)
        self.statuslabel.setFrameShape(QFrame.NoFrame)
        self.statuslabel.setObjectName("statuslabel")
        self.stackedWidget = QStackedWidget(Dialog)
        self.stackedWidget.setGeometry(QRect(20, 90, 471, 281))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QWidget()
        self.page.setObjectName("page")
        self.tension_harden = QPushButton(self.page)
        self.tension_harden.setGeometry(QRect(1, 102, 151, 51))
        self.tension_harden.setFont(font)
        self.tension_harden.setCheckable(True)
        self.tension_harden.setObjectName("tension_harden")
        self.tensionlabel = QLabel(self.page)
        self.tensionlabel.setGeometry(QRect(170, 40, 101, 31))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tensionlabel.sizePolicy().hasHeightForWidth())
        self.tensionlabel.setSizePolicy(sizePolicy)
        palette = QPalette()
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush)
        self.tensionlabel.setPalette(palette)
        self.tensionlabel.setFont(font)
        self.tensionlabel.setAutoFillBackground(True)
        self.tensionlabel.setFrameShape(QFrame.Box)
        self.tensionlabel.setObjectName("tensionlabel")
        self.label = QLabel(self.page)
        self.label.setGeometry(QRect(175, 15, 97, 21))
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.strawtimelabel = QLabel(self.page)
        self.strawtimelabel.setGeometry(QRect(310, 40, 91, 31))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.strawtimelabel.sizePolicy().hasHeightForWidth()
        )
        self.strawtimelabel.setSizePolicy(sizePolicy)
        palette = QPalette()
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush)
        self.strawtimelabel.setPalette(palette)
        self.strawtimelabel.setFont(font)
        self.strawtimelabel.setAutoFillBackground(True)
        self.strawtimelabel.setFrameShape(QFrame.Box)
        self.strawtimelabel.setObjectName("strawtimelabel")
        self.label_9 = QLabel(self.page)
        self.label_9.setGeometry(QRect(310, 12, 91, 21))
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.recordtension = QPushButton(self.page)
        self.recordtension.setGeometry(QRect(0, 160, 151, 41))
        self.recordtension.setFont(font)
        self.recordtension.setCheckable(True)
        self.recordtension.setObjectName("recordtension")
        self.next_straw = QPushButton(self.page)
        self.next_straw.setGeometry(QRect(1, 210, 151, 41))
        self.next_straw.setFont(font)
        self.next_straw.setCheckable(True)
        self.next_straw.setObjectName("next_straw")
        self.topcheck = QCheckBox(self.page)
        self.topcheck.setGeometry(QRect(10, 23, 121, 20))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.topcheck.sizePolicy().hasHeightForWidth())
        self.topcheck.setSizePolicy(sizePolicy)
        self.topcheck.setFont(font)
        self.topcheck.setObjectName("topcheck")
        self.bottomcheck = QCheckBox(self.page)
        self.bottomcheck.setGeometry(QRect(10, 50, 121, 20))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bottomcheck.sizePolicy().hasHeightForWidth())
        self.bottomcheck.setSizePolicy(sizePolicy)
        self.bottomcheck.setFont(font)
        self.bottomcheck.setObjectName("bottomcheck")
        self.resetmotor = QPushButton(self.page)
        self.resetmotor.setGeometry(QRect(160, 210, 121, 41))
        self.resetmotor.setFont(font)
        self.resetmotor.setCheckable(True)
        self.resetmotor.setObjectName("resetmotor")
        self.tension_only = QPushButton(self.page)
        self.tension_only.setGeometry(QRect(160, 160, 121, 41))
        self.tension_only.setFont(font)
        self.tension_only.setCheckable(True)
        self.tension_only.setObjectName("tension_only")
        self.tarebutton = QPushButton(self.page)
        self.tarebutton.setGeometry(QRect(290, 160, 171, 41))
        self.tarebutton.setFont(font)
        self.tarebutton.setCheckable(True)
        self.tarebutton.setObjectName("tarebutton")
        self.setcalbutton = QPushButton(self.page)
        self.setcalbutton.setGeometry(QRect(290, 210, 171, 41))
        self.setcalbutton.setFont(font)
        self.setcalbutton.setCheckable(True)
        self.setcalbutton.setObjectName("setcalbutton")
        self.recordlabel = QLabel(self.page)
        self.recordlabel.setGeometry(QRect(0, 260, 251, 21))
        self.recordlabel.setFont(font)
        self.recordlabel.setText("")
        self.recordlabel.setObjectName("recordlabel")
        self.tarebutton2 = QPushButton(self.page)
        self.tarebutton2.setGeometry(QRect(290, 110, 171, 41))
        self.tarebutton2.setFont(font)
        self.tarebutton2.setCheckable(True)
        self.tarebutton2.setObjectName("tarebutton2")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName("page_2")
        self.layoutWidget_2 = QWidget(self.page_2)
        self.layoutWidget_2.setGeometry(QRect(10, 10, 143, 61))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.verticalLayout_6 = QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_6.setSizeConstraint(QLayout.SetFixedSize)
        self.verticalLayout_6.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.caliblabel = QLabel(self.layoutWidget_2)
        self.caliblabel.setFont(font)
        self.caliblabel.setObjectName("caliblabel")
        self.verticalLayout_6.addWidget(self.caliblabel)
        self.calibmode = QLabel(self.layoutWidget_2)
        palette = QPalette()
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush)
        self.calibmode.setPalette(palette)
        self.calibmode.setFont(font)
        self.calibmode.setAutoFillBackground(True)
        self.calibmode.setFrameShape(QFrame.Box)
        self.calibmode.setObjectName("calibmode")
        self.verticalLayout_6.addWidget(self.calibmode)
        self.tare = QPushButton(self.page_2)
        self.tare.setGeometry(QRect(10, 90, 131, 31))
        self.tare.setFont(font)
        self.tare.setCheckable(True)
        self.tare.setObjectName("tare")
        self.setbutton = QPushButton(self.page_2)
        self.setbutton.setGeometry(QRect(10, 130, 131, 31))
        self.setbutton.setFont(font)
        self.setbutton.setCheckable(True)
        self.setbutton.setObjectName("setbutton")
        self.layoutWidget_4 = QWidget(self.page_2)
        self.layoutWidget_4.setGeometry(QRect(170, 90, 139, 61))
        self.layoutWidget_4.setObjectName("layoutWidget_4")
        self.verticalLayout_8 = QVBoxLayout(self.layoutWidget_4)
        self.verticalLayout_8.setSizeConstraint(QLayout.SetFixedSize)
        self.verticalLayout_8.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_8.setSpacing(6)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.caliblabel_3 = QLabel(self.layoutWidget_4)
        self.caliblabel_3.setFont(font)
        self.caliblabel_3.setObjectName("caliblabel_3")
        self.verticalLayout_8.addWidget(self.caliblabel_3)
        self.loadcellreading = QLabel(self.layoutWidget_4)
        palette = QPalette()
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush)
        self.loadcellreading.setPalette(palette)
        self.loadcellreading.setFont(font)
        self.loadcellreading.setAutoFillBackground(True)
        self.loadcellreading.setFrameShape(QFrame.Box)
        self.loadcellreading.setObjectName("loadcellreading")
        self.verticalLayout_8.addWidget(self.loadcellreading)
        self.tension_mode = QPushButton(self.page_2)
        self.tension_mode.setGeometry(QRect(310, 160, 131, 41))
        self.tension_mode.setFont(font)
        self.tension_mode.setCheckable(True)
        self.tension_mode.setObjectName("tension_mode")
        self.stackedWidget.addWidget(self.page_2)
        self.label_2 = QLabel(Dialog)
        self.label_2.setGeometry(QRect(30, 20, 104, 31))
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.strawnumbox = QSpinBox(Dialog)
        self.strawnumbox.setGeometry(QRect(28, 50, 71, 31))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.strawnumbox.sizePolicy().hasHeightForWidth())
        self.strawnumbox.setSizePolicy(sizePolicy)
        self.strawnumbox.setFont(font)
        self.strawnumbox.setObjectName("strawnumbox")
        self.caliblabel_2 = QLabel(Dialog)
        self.caliblabel_2.setGeometry(QRect(135, 20, 137, 27))
        self.caliblabel_2.setFont(font)
        self.caliblabel_2.setObjectName("caliblabel_2")
        self.calibfactor = QLabel(Dialog)
        self.calibfactor.setGeometry(QRect(135, 50, 131, 31))
        palette = QPalette()
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush)
        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        brush = QBrush(QColor(122, 0, 25))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush)
        self.calibfactor.setPalette(palette)
        self.calibfactor.setFont(font)
        self.calibfactor.setAutoFillBackground(True)
        self.calibfactor.setFrameShape(QFrame.Box)
        self.calibfactor.setObjectName("calibfactor")

        ## Continuity

        # Label
        self.continuityLabel = QLabel(Dialog)
        self.continuityLabel.setFont(font)
        self.continuityLabel.setGeometry(QRect(20, 360, 180, 30))
        self.continuityLabel.setText("Continuity")

        # Select Continuity
        self.selectContinuity = QComboBox(Dialog)
        self.selectContinuity.addItems(
            [
                "Pass: No Continuity",
                "Fail: Right Continuity",
                "Fail: Left Continuity",
                "Fail: Both Continuity",
            ]
        )
        self.selectContinuity.setCurrentIndex(0)
        self.selectContinuity.setGeometry(QRect(20, 400, 200, 30))
        self.selectContinuity.setFont(font)

        # Select Wire Position
        self.selectWirePosition = QComboBox(Dialog)
        self.selectWirePosition.addItems(["Top 1/3", "Middle 1/3", "Lower 1/3"])
        self.selectWirePosition.setCurrentIndex(1)
        self.selectWirePosition.setGeometry(QRect(250, 400, 200, 30))
        self.selectWirePosition.setFont(font)

        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_4.setText(_translate("Dialog", "Status:"))
        self.statuslabel.setText(_translate("Dialog", "TextLabel"))
        self.tension_harden.setText(
            _translate("Dialog", "Work Harden and \nTension Wire")
        )
        self.tensionlabel.setText(_translate("Dialog", "zero"))
        self.label.setText(_translate("Dialog", "Wire Tension"))
        self.strawtimelabel.setText(_translate("Dialog", "0"))
        self.label_9.setText(_translate("Dialog", "Wire Timer"))
        self.recordtension.setText(_translate("Dialog", "Save"))
        self.next_straw.setText(_translate("Dialog", "Next Straw"))
        self.topcheck.setText(_translate("Dialog", "Top Row"))
        self.bottomcheck.setText(_translate("Dialog", "Bottom Row"))
        self.resetmotor.setText(_translate("Dialog", "Reset Motor"))
        self.tension_only.setText(_translate("Dialog", "Tension Wire"))
        self.tarebutton.setText(_translate("Dialog", "Tare Load Cell (50g)"))
        self.setcalbutton.setText(_translate("Dialog", "Set Calibration (100g)"))
        self.tarebutton2.setText(_translate("Dialog", "Tare Load Cell (0g)"))
        self.caliblabel.setText(_translate("Dialog", "Calibration mode"))
        self.calibmode.setText(_translate("Dialog", "standby"))
        self.tare.setText(_translate("Dialog", "Tare: Hang 50g"))
        self.setbutton.setText(_translate("Dialog", "Set: Hang 100g"))
        self.caliblabel_3.setText(_translate("Dialog", "Load Cell reading"))
        self.loadcellreading.setText(_translate("Dialog", "0"))
        self.tension_mode.setText(_translate("Dialog", "Tension Mode"))
        self.label_2.setText(_translate("Dialog", "Wire Number"))
        self.caliblabel_2.setText(_translate("Dialog", "Calibration Factor"))
        self.calibfactor.setText(_translate("Dialog", "0"))


