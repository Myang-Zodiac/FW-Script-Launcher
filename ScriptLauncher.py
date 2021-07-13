#import PyQt5
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QDesktopWidget, QLabel, QListWidget, QPushButton, QTextEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon, QFont#, QFontDatabase
from PyQt5.QtCore import Qt, QSize
import sys
import os
from distutils.dir_util import copy_tree
import shutil
import subprocess

class Window(QWidget):
    def __init__(self):
        super().__init__()
        # Set window layout

        self.setInitUI()

        # Create dummy layout (temp solution)
        topLayout = QVBoxLayout()
        self.setLayout(topLayout)
        self.optionsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Tests')
        # Create tab switcher widget
        self.tabWrapper = QTabWidget()
        self.tabWrapper.setFont(QFont('Calibri', 11))
        self.tabWrapper.move(5,5)
        self.tabWrapper.resize(self.width()-10,self.height()-10)
        # Set up pages
        self.makeStartPage()
        self.makeResultsPage()
        # Add tab switcher widget to dummy layout
        topLayout.addChildWidget(self.tabWrapper)

        # Show Window
        self.show()



    '''MAIN FUNCTIONS'''
    def setInitUI(self): # Called by __init__
        '''Set up window layout'''
        self.setFixedWidth(750)
        self.setFixedHeight(500)
        self.setWindowTitle("Script Launcher")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')))
        self._center()

    def makeStartPage(self): # Called by __init__ 
        '''Set up Main Page'''
        self.startPage = QWidget()

        # Create list view
        self._makeScriptList()
        # Create add and subtract buttons to manipulate tests folder
        self._makeAddSubButtons()
        # Create snippet view
        self._makeSnippetView()

        self.tabWrapper.addTab(self.startPage, 'Script Selection')

    def makeResultsPage(self): # Called by __init__ 
        ''' Set up Results Page'''
        self.resultsPage = QWidget()

        self.tabWrapper.addTab(self.resultsPage, 'Results')
    
    '''SUB-FUNCTIONS'''
    def _switchPage(self, targetPage): # General purpose tool function 
        '''Switches to target page'''
        self.tabWrapper.setCurrentWidget(targetPage)
    def _center(self): # Called by setInitUI 
        '''Centers window'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    def _makeScriptList(self): # Called by makeStartPage 
        '''Creates and displays list of available scripts and two methods to launch'''
        # Explain how to launch
        self.intro = QLabel('Select desired test and launch', self.startPage)
        self.intro.resize(350,20)
        self.intro.move(10,15)
        self.intro.setAlignment(Qt.AlignCenter)
        # Setup list of tests
        self.listWidget = QListWidget(self.startPage)
        self.listWidget.setStyleSheet("border: 1px solid gray;")
        self.listWidget.resize(350,365) #330
        self.listWidget.move(10,50)
        self.__getOptions()
        self.listWidget.addItems(self.options.keys())
        # Enable launch mechanisms
        self.submitTest = QPushButton('Launch', self.startPage)
        self.submitTest.setFont(QFont('Calibri', 9))
        self.submitTest.move(125, 420)
        self.submitTest.clicked.connect(self.__launchScriptHandler)
        self.listWidget.itemDoubleClicked.connect(self.__launchScriptHandler)
    def _makeSnippetView(self): # Called by makeStartPage 
        self.snippetInstructions = QLabel('Select a script to see its description', self.startPage)
        self.snippetInstructions.resize(350,20)
        self.snippetInstructions.move(375,15)
        self.snippetInstructions.setAlignment(Qt.AlignCenter)

        self.scriptSnippet = QTextEdit(self.startPage)
        self.scriptSnippet.setReadOnly(True)
        self.scriptSnippet.setStyleSheet("border: 1px solid gray;")
        self.scriptSnippet.resize(350,365)
        self.scriptSnippet.move(375,50)
        
        self.listWidget.itemClicked.connect(self.__updateSnippet)
    def _makeAddSubButtons(self):
        self.folderView = QPushButton(self.startPage)
        self.folderView.resize(35,35)
        self.folderView.move(262, 381)
        self.folderView.setIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'foldericon.png')))
        self.folderView.setIconSize(QtCore.QSize(25,25))
        self.subScript = QPushButton('-', self.startPage)
        self.subScript.resize(35,35)
        self.subScript.move(294,381)
        self.addScript = QPushButton('+', self.startPage)
        self.addScript.resize(35,35)
        self.addScript.move(326,381)
        self.refresh = QPushButton(self.startPage)
        self.refresh.resize(27,27)
        self.refresh.move(333,23) #332 51
        self.refresh.setStyleSheet("QPushButton"
                                   "{"
                                   "background-color : white;"
                                   "border : 0px"
                                   "}"
                                   "QPushButton::hover"
                                   "{"
                                   "background-color : rgb(229,243,255);"
                                   "border : 1px"
                                   "}"
                                   "QPushButton::pressed"
                                   "{"
                                   "background-color : rgb(229,243,255);"
                                   "border : 0px"
                                   "}")
        self.refresh.setIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'refreshicon.png')))


        self.folderView.clicked.connect(self.__folderView)
        self.subScript.clicked.connect(self.__subFile)
        self.addScript.clicked.connect(self.__addFile)
        self.refresh.clicked.connect(self.__refresh)

    '''SUB-SUB-FUNCTIONS'''
    def __getOptions(self): # Called by _makeScriptList 
        '''Retrieves available tests and creates a dictionary with name:path pairs'''
        #appPath = os.path.dirname(os.path.abspath(__file__))
        self.options = {}
        folder = os.listdir(self.optionsPath)
        for test in folder:
            #self.optionPaths.append(os.path.join(optionsPath, test))
            self.options[test] = os.path.join(self.optionsPath, test)
        #for optionPath in self.optionPaths:
            #self.options.append(optionPath.split('\\')[-1])

    def __updateSnippet(self, item): # Called by _makeSnippetView on event 
        '''Verifies whether info.txt exists and displays info/error accordingly'''
        try:
            f = open(os.path.join(self.options[item.text()], 'info.txt'), "r")
            info = f.read()
            self.scriptSnippet.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.scriptSnippet.setPlainText(info)
            self.scriptSnippet.setWordWrapMode(False)
        except:
            self.scriptSnippet.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            self.scriptSnippet.setPlainText('Error: no info file found')
    
    def __launchScriptHandler(self, item): # Called by _makeScriptList on events 
        '''Verifies whether selected script exists and launches or displays error accordingly'''
        self._switchPage(self.resultsPage)
        if not item:
            test = self.options[self.listWidget.selectedItems()[0].text()]
        else:
            test = self.options[item.text()]
        try: # to launch script
            pass
        except: # display error
            pass
        else: # display success message
            pass
    
    #'''
    def __folderView(self):
        #os.system(f'explorer {self.optionsPath}')
        subprocess.Popen(f'explorer {self.optionsPath}', shell=True)
    #'''

    def __addFile(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder == '':
            return
        try:
            os.mkdir(os.path.join(self.optionsPath, folder.split('/')[-1]))
        except FileExistsError as e:
            print(e)
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("The directory already exists")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.exec()
        else:
            copy_tree(folder, os.path.join(self.optionsPath, folder.split('/')[-1]))
            self.listWidget.addItem(folder.split('/')[-1])
            self.__getOptions()
    
    def __subFile(self):
        if len(self.listWidget.selectedItems()) == 1:
            path = self.options[self.listWidget.selectedItems()[0].text()]
            shutil.rmtree(path)
            self.listWidget.takeItem(self.listWidget.row(self.listWidget.selectedItems()[0]))
            self.__getOptions()
            self.scriptSnippet.setPlainText('')
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("No directory was selected")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.exec()
    
    def __refresh(self):
        optionsTemp = self.options.keys()
        self.__getOptions()
        for opt in self.options:
            if opt not in optionsTemp:
                self.listWidget.addItem(opt)
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    #window.show()
    sys.exit(app.exec_())