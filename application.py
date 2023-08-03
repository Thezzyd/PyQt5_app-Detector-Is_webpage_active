
from __future__ import annotations
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMainWindow
#from PyQt5.uic import loadUi
import requests
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from pushbullet import PushBullet
from pushbullet import errors

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    

    def __init__(self, page_name, time_break, is_active, logs, feedback_widget, access_token, parentObj):
        super().__init__()
        self.parentObj = parentObj
        self.page_name = page_name
        self.time_break = time_break
        self.is_active = is_active
        self.feedback_widget = feedback_widget
        self.logs = logs
        self.access_token = access_token
        self.timer_for_message = 0
        self.errorFormat = '<span style="color:red;">{}</span>'
        self.warningFormat = '<span style="color:orange;">{}</span>'
        self.validFormat = '<span style="color:green;">{}</span>'
        self.message_content = "Checked website is now available!"
        self.message_title = 'Hey!'
        self.startTime = time.time()

    def showPopup(self):
        msg = QDialog()
        msg.setWindowTitle('Webpage is active!!!')
        #msg.setText('Podana strona internetowa jest już aktywna!')
        msg.setWindowModality(QtCore.Qt.NonModal)
        msg.exec()


    def run(self):
        i=0
        is_popup_shown = False
        while(self.is_active):
            try:
                response_target = requests.get(self.page_name, allow_redirects=False)
            except requests.exceptions.MissingSchema:
                self.logs.append(self.errorFormat.format('Given link to the page contains an error...'+'  |  '+current_time))
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if response_target.status_code == 200:
                self.logs.append(self.validFormat.format('Webpage is active: ' + str(response_target.status_code) +'  |  '+ current_time))
                self.feedback_widget.setStyleSheet("background-color: green;")
                self.parentObj.activateWindow()
                if(self.access_token != '' and self.access_token != None):
                    if((time.time() - self.startTime) >= self.timer_for_message):
                        self.timer_for_message = 1800
                        self.startTime = time.time()
                        try:
                            pb = PushBullet(self.access_token)   
                            push = pb.push_note(self.message_title, self.message_content)
                            self.logs.append(self.warningFormat.format('Successful transmission of the notification to the specified token...'+'  |  '+current_time))
                            #print('weszlo... wyslano')
                        except errors.InvalidKeyError:
                            self.logs.append(self.errorFormat.format('Incorrect token specified, message transmission failed...'+'  |  '+current_time))
               #print('Strona aktywna: ', response_target.status_code)
            else:
                self.logs.append(self.errorFormat.format('Webpage inactive: ' + str(response_target.status_code) +'  |  '+ current_time))
                self.feedback_widget.setStyleSheet("background-color: red;")
                #print('Strona nieaktywna: ', response_target.status_code) 
            x = self.logs.verticalScrollBar().maximum()
            self.logs.verticalScrollBar().setValue(x + 1)
            time.sleep(int(self.time_break))
            i = i + 1 
            if(i==4):
                self.parentObj.activateWindow()


class Ui_MainWindow(object):
    access_token = ""
    time_break = 110
    is_active = False
    page_name = ''
    errorFormat = '<span style="color:red;">{}</span>'
    warningFormat = '<span style="color:orange;">{}</span>'
    validFormat = '<span style="color:green;">{}</span>'
    worker = None

    def Start(self):
        self.time_break = self.input_time_break.text()
        self.page_name = self.input_page_link.text()
        self.access_token = self.input_access_token.text()

        if(self.time_break == '' or not self.time_break or self.page_name == '' or not self.time_break or not self.time_break.isnumeric()):
            self.logs.append('Fields are blank or contain an error...')
        else:
            self.is_active = True
            self.button_start.setEnabled(False)
            self.button_stop.setEnabled(True)
            self.logs.append(self.warningFormat.format('Detection has begun for the site: '+ self.page_name))
            self.CheckIfExists()

    def CheckIfExists(self):
        if(self.worker):
            self.worker.page_name = self.page_name
            self.worker.time_break = self.time_break
            self.worker.is_active = self.is_active
            self.worker.access_token = self.access_token
            self.worker.timer_for_message = 0
            self.thread = QThread(parent=MainWindow)
            self.thread.started.connect(self.worker.run)
            self.thread.start()
        else:    
            self.thread = QThread(parent=MainWindow)
            self.worker = Worker(self.page_name, self.time_break, self.is_active, self.logs, self.feedback_widget, self.access_token, MainWindow)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.thread.start()
        
    def showPopup(self):
        msg = QMessageBox()
        msg.setWindowTitle('Webpage is active!!!')
        msg.setText('The specified website is now active!')
        x = msg.exec_()

    def Stop(self):
        self.is_active = False
        self.worker.is_active = self.is_active
        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)
        self.logs.append(self.warningFormat.format('Stopped...'))


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(735, 300)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 30, 481, 221))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_6 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_6.setMinimumSize(QtCore.QSize(150, 0))
        self.label_6.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_5.addWidget(self.label_6)
        self.input_page_link = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.input_page_link.setObjectName("input_page_link")
        self.horizontalLayout_5.addWidget(self.input_page_link)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setMinimumSize(QtCore.QSize(150, 0))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.input_time_break = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.input_time_break.setObjectName("input_time_break")
        self.horizontalLayout.addWidget(self.input_time_break)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setMinimumSize(QtCore.QSize(150, 0))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.input_access_token = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.input_access_token.setObjectName("input_access_token")
        self.horizontalLayout_2.addWidget(self.input_access_token)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.logs = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.logs.setEnabled(True)
        self.logs.setMaximumSize(QtCore.QSize(16777215, 100))
        self.logs.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.logs.setReadOnly(True)
        self.logs.setObjectName("logs")
        self.verticalLayout.addWidget(self.logs)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.button_start = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_start.setObjectName("button_start")
        self.horizontalLayout_6.addWidget(self.button_start)
        self.button_stop = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_stop.setObjectName("button_stop")
        self.horizontalLayout_6.addWidget(self.button_stop)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.feedback_widget = QtWidgets.QWidget(self.centralwidget)
        self.feedback_widget.setGeometry(QtCore.QRect(500, 30, 221, 221))
        self.feedback_widget.setStyleSheet("background-color: gray")
        self.feedback_widget.setObjectName("feedback_widget")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(8, 0, 721, 24))
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 735, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PyQt5 App | Is webpage active detector"))
        self.label_6.setText(_translate("MainWindow", "Provide a link to the site:"))
        self.input_page_link.setPlaceholderText(_translate("MainWindow", "Enter the link to the site: \'http://...\'"))
        self.label.setText(_translate("MainWindow", "Refreshing interval:"))
        self.input_time_break.setPlaceholderText(_translate("MainWindow", "Enter the refreshing interval (in seconds)"))
        self.label_3.setText(_translate("MainWindow", "Access token (pushbullet):"))
        self.input_access_token.setPlaceholderText(_translate("MainWindow", "Optional -> Enter access token from pushbullet app"))
        self.logs.setPlaceholderText(_translate("MainWindow", "Logs..."))
        self.button_start.setText(_translate("MainWindow", "Start"))
        self.button_stop.setText(_translate("MainWindow", "Stop"))
        self.label_2.setText(_translate("MainWindow", "Does the website exist / is active?"))
        self.button_start.clicked.connect(self.Start)
        self.button_stop.clicked.connect(self.Stop)
        self.button_stop.setEnabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindow.setFixedWidth(735)
    MainWindow.setFixedHeight(280)
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
