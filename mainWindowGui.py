# -*- coding: utf-8 -*-
import os
import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from tqdm import tqdm
from bs4 import BeautifulSoup

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setFixedSize(800,600)
        self.__CreateUi(MainWindow)
        self.__RetranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.__AssignFunctionality()

    def __CreateUi(self,MainWindow):
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(100, 500, 675, 30))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(25, 60, 750, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit.setFont(font)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(25, 180, 750, 300))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.plainTextEdit.setFont(font)
        self.plainTextEdit.setPlainText("")
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(25, 110, 750, 50))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 10, 700, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(25, 500, 100, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(24, 550, 761, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
    
    def __RetranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "4chanDownloader"))
        self.pushButton.setText(_translate("MainWindow", "DOWNLOAD"))
        self.label.setText(_translate("MainWindow", "Enter URL:"))
        self.label_2.setText(_translate("MainWindow", "Progress:"))
        self.label_3.setText(_translate("MainWindow", "-Chelosky-"))
    
    def __AssignFunctionality(self):
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        self.plainTextEdit.setEnabled(False)
        self.label_2.setVisible(False)
        self.plainTextEdit.setPlainText("\t\t\t\tConsole:")
        self.workerThread = Worker_Thread()
        self.workerThread.signalUpdateConsole.connect(self.UpdateConsole)
        self.workerThread.signalSetUpPB.connect(self.SetUpPB)
        self.workerThread.signalUpdatePB.connect(self.UpdatePB)
        self.workerThread.signalEndApp.connect(self.ResetApp)
        self.pushButton.clicked.connect(self.__ButtonClicked)
    
    def UpdateConsole(self,text):
        self.__AddTextToConsole(text)
    
    def SetUpPB(self,numero):
        self.__SetUpPB(numero)

    def UpdatePB(self):
        self.__UpdateProgressBar()
    
    def ResetApp(self):
        self.__ResetApp()
        self.label_2.setVisible(False)
    
    def __ResetApp(self):
        self.progressBar.setVisible(False)
    
    def __SetUpPB(self,numero):
        self.progressBar.setMaximum(numero)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(True)
        self.label_2.setVisible(True)
    
    def __UpdateProgressBar(self):
        self.progressBar.setValue(self.progressBar.value()+1)

    def __AddTextToConsole(self,text):
        # self.plainTextEdit.setEnabled(True)
        self.plainTextEdit.setPlainText(self.plainTextEdit.toPlainText()+'\n'+text)
        self.plainTextEdit.verticalScrollBar().setValue(self.plainTextEdit.verticalScrollBar().maximum())

    def __ButtonClicked(self):
        self.workerThread.SetUrl(self.lineEdit.text())
        self.workerThread.start()
    
class Worker_Thread(QtCore.QThread):
    signalSetUpPB = QtCore.pyqtSignal(int)
    signalUpdateConsole = QtCore.pyqtSignal(str)
    signalUpdatePB = QtCore.pyqtSignal()
    signalEndApp = QtCore.pyqtSignal()
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.__chunk_size = 1024
        self.__url = ""
    
    def SetUrl(self,url):
        self.__url = url
    
    def __SendMessageConsole(self,text):
        self.signalUpdateConsole.emit(text)

    def __GetFileLinks(self):
        try:
            self.__SendMessageConsole("Accessing Site...")
            r = requests.get(self.__url)
            if(r.status_code == 404):
                raise ValueError("Error: The URL isn't available")
            elif(r.status_code == 200):
                self.__SendMessageConsole("Access Successful...")
                html_content = r.text
                soup = BeautifulSoup(html_content,"html.parser")
                posts = soup.findAll('a',{"class":"fileThumb"})
                self.__SendMessageConsole("Obtaining Information...")
                self.signalSetUpPB.emit(len(posts))
                self.__SendMessageConsole("Total Posts: "+str(len(posts)))
                indexFile=1
                self.__SendMessageConsole("Creating new Directory...")
                actual_path = self.__MakeNewDir('\Downloads')
                self.__SendMessageConsole("Downloading Files...")
                for post in posts:
                    url_File = "https:"+str(post['href'])
                    self.__DownloadFile(url_File,"File"+str(indexFile),actual_path)
                    indexFile+=1
                self.__SendMessageConsole("App Finished!")
                self.signalEndApp.emit()
            else:
                raise ValueError("Error: Unknown Problem")
        except Exception as error:
            self.__SendMessageConsole(str(error))
            print(repr(error))

    def __MakeNewDir(self,dirName):
        temp_path = os.path.dirname(os.path.realpath(__file__))+dirName
        if not os.path.exists(temp_path):
            temp_path += '\\'
            os.makedirs(temp_path)
        else:
            idx = 1
            while(os.path.exists(temp_path + str(idx))):
                idx+=1
            temp_path += str(idx)+'\\'
            os.makedirs(temp_path)
        return temp_path

    def __DownloadFile(self,urlFile,nameFile,actual_path):
        try:
            self.__SendMessageConsole("\t"+nameFile+"\t Url:("+ urlFile +")")
            r = requests.get(urlFile,stream=True)
            if(r.status_code == 404):
                raise ValueError("Error: The URL file isn't available")
            elif(r.status_code==200):
                urlStuff = urlFile.split('.')
                _nameFile = nameFile + '.' + str(urlStuff[len(urlStuff)-1])
                total_size = int(r.headers['content-length'])
                with open(actual_path+_nameFile,'wb') as f:
                    for data in tqdm(iterable=r.iter_content(chunk_size=self.__chunk_size),total=total_size/self.__chunk_size, unit='KB'):
                        f.write(data)
                self.__SendMessageConsole("\t\t"+nameFile+" Downloaded.")
                self.signalUpdatePB.emit()
            else:
                raise ValueError("Error: Unknown Problem")
        except Exception as error:
            self.__SendMessageConsole(str(error))
            print(repr(error))
    
    def run(self):
        self.__GetFileLinks()
        


def RunApp():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

