# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time

import os
import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 600)
        self.MakingUi(Dialog)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.FuncionalidadUi()

    def FuncionalidadUi(self):
        self.workerThread = Worker_Thread()
        self.progressBar.setVisible(False)
        self.workerThread.signal.connect(self.imprimir)
        self.pushButton.clicked.connect(self.ClickButton)

    def ClickButton(self):        
        self.workerThread.setUrl(self.textEdit.toPlainText())
        # self.textEdit.setAlignment(QtCore.Qt.AlignHCenter)
        self.textEdit.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.workerThread.start()
        self.progressBar.setVisible(True)
        print("YA PASO EL WORKER")

    def imprimir(self):
        print("CALLBACK CALLED")
    
    def MakingUi(self,Dialog):
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(250, 330, 300, 50))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(325, 175, 150, 80))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.logoIm = QtWidgets.QLabel(Dialog)
        self.logoIm.setGeometry(QtCore.QRect(250, 25, 300, 100))
        self.logoIm.setFrameShape(QtWidgets.QFrame.Box)
        self.logoIm.setFrameShadow(QtWidgets.QFrame.Plain)
        self.logoIm.setLineWidth(1)
        self.logoIm.setText("")
        self.logoIm.setObjectName("logoIm")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(40, 470, 750, 40))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(100, 250, 600, 50))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")    

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "4chanDownloader"))
        self.pushButton.setText(_translate("Dialog", "DESCARGAR"))
        self.label.setText(_translate("Dialog", "URL"))
        self.textEdit.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n""<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n""p, li { white-space: pre-wrap; }\n""</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:14pt; font-weight:400; font-style:normal;\">\n""<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))

class Worker_Thread(QtCore.QThread):
    signal = QtCore.pyqtSignal()
    pathChrome =  os.path.dirname(os.path.realpath(__file__)) + " /webdrivers/chromedriver"
    pathJS = os.path.dirname(os.path.realpath(__file__)) +"/webdrivers/phantomjs"
    # signal = QtCore.pyqtSignal('PyQt_PyObject')
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.chunk_size = 1024
        self.url = ""
    
    def setUrl(self,url):
        self.url = url

    def DownloadAFile(self,img_url,nameIdx):
        try:
            url_DIR = img_url.split('.')
            nameFile = nameIdx + '.'+url_DIR[len(url_DIR)-1]
            r = requests.get(img_url, stream=True)
            if(r.status_code == 404):
                raise ValueError('La imagen no se encuentra disponible')
            elif(r.status_code == 200):
                total_size = int(r.headers['content-length'])
                with open(nameFile,'wb')as f:
                    for data in tqdm(iterable=r.iter_content(chunk_size=self.chunk_size),total=total_size/self.chunk_size, unit='KB'):
                        f.write(data)
                print("FIN")
            else:
                raise ValueError('Error BD')
        except Exception as error:
            print("ERROR!: " + repr(error))

    def GetFileLinks(self):
        try:
            print("stuff")
            driver = webdriver.PhantomJS(self.pathJS)
            driver.get(self.url)
            posts = driver.find_elements_by_class_name("fileThumb")
            idx=1
            for post in posts:
                url_image = post.get_attribute('href')
                self.DownloadAFile(url_image,"File"+str(idx))
                idx+=1
            driver.close()
        except:
            print("ERROR")

    def run(self):
        # self.downloadAFile(self.url,'Imagen1')
        self.GetFileLinks()
        self.signal.emit()


def runApp():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

