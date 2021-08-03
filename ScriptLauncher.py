#import PyQt5
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QButtonGroup, QRadioButton, QWidget, QVBoxLayout, QTabWidget, QDesktopWidget, QLabel, QListWidget, QPushButton, QTextEdit, QFileDialog, QMessageBox, QLineEdit
from PyQt5.QtGui import QIcon, QFont
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
        self.DLPath = ''

        # Create dummy layout (temp solution)
        topLayout = QVBoxLayout()
        self.setLayout(topLayout)
        self.optionsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
        # Create tab switcher widget
        self.tabWrapper = QTabWidget()
        self.tabWrapper.setFont(QFont('Calibri', 11))
        self.tabWrapper.move(5,5)
        self.tabWrapper.resize(self.width()-10,self.height()-10)
        # Set up pages
        self.makeStartPage()
        self.makeResultsPage()
        self.makeSettingsPage()
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
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/icon.png')))
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
        '''Set up Results Page'''
        self.resultsPage = QWidget()

        self.tabWrapper.addTab(self.resultsPage, 'Results')

    def makeSettingsPage(self):
        '''Set up Settings Page'''
        self.settingsPage = QWidget()

        self._makePathInput()
        self._makeRunSettings()

        self.tabWrapper.addTab(self.settingsPage, 'Settings')
    
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
        '''Creates small sub-window to view info files for tests'''
        # Explain how to show info snippet
        self.snippetInstructions = QLabel('Select a script to see its description', self.startPage)
        self.snippetInstructions.resize(350,20)
        self.snippetInstructions.move(375,15)
        self.snippetInstructions.setAlignment(Qt.AlignCenter)
        # Set up window to view snippet
        self.scriptSnippet = QTextEdit(self.startPage)
        self.scriptSnippet.setReadOnly(True)
        self.scriptSnippet.setStyleSheet("border: 1px solid gray;")
        self.scriptSnippet.resize(350,365)
        self.scriptSnippet.move(375,50)
        # Update snippet shown on single-click
        self.listWidget.itemClicked.connect(self.__updateSnippet)
    def _makeAddSubButtons(self): # Called by makeStartPage
        '''Creates add, subtract, folder, and refresh buttons'''
        # Create folder button
        self.folderView = QPushButton(self.startPage)
        self.folderView.resize(35,35)
        self.folderView.move(262, 381)
        self.folderView.setIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/foldericon.png')))
        self.folderView.setIconSize(QtCore.QSize(25,25))
        # Create subtract button
        self.subScript = QPushButton('-', self.startPage)
        self.subScript.resize(35,35)
        self.subScript.move(294,381)
        # Create add button
        self.addScript = QPushButton('+', self.startPage)
        self.addScript.resize(35,35)
        self.addScript.move(326,381)
        # Create refresh button
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
        self.refresh.setIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/refreshicon.png')))
        # Enable actions on single-click
        self.folderView.clicked.connect(self.__folderView)
        self.subScript.clicked.connect(self.__subFile)
        self.addScript.clicked.connect(self.__addFile)
        self.refresh.clicked.connect(self.__refresh)
    def _makePathInput(self): # Called by makeSettingsPage
        '''Creates input box to get Docklight path if not already saved'''
        # Create input box
        self.pathInput = QLineEdit(self.settingsPage)
        self.pathInput.resize(600,25)
        self.pathInput.move(15,15)
        # Create save button
        self.pathInputButton = QPushButton('Save', self.settingsPage)
        self.pathInputButton.setFont(QFont('Calibri', 9))
        self.pathInputButton.resize(100,25)
        self.pathInputButton.move(620, 15)
        # Ready storage file for reading
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/dlpath.txt'), "r+") as f:
            txt = f.read().rstrip()
            if not os.path.isfile(txt) or not txt.endswith("Docklight_Scripting.exe"):
                self.pathInput.setPlaceholderText('Input DockLight Scripting path')
            else:
                self.pathInput.setPlaceholderText('Valid path entered')
                self.DLPath = txt
                self.pathInput.setText(txt)
                self.pathInputButton.setText('Replace')
        # Call function to save data
        self.pathInputButton.clicked.connect(self.__handlePath)
    def _makeRunSettings(self):
        '''Creates selection dropdown to determine how to run script'''
        self.runTypeLabel = QLabel('Select run type:', self.settingsPage)
        self.runTypeLabel.resize(500,20)
        self.runTypeLabel.move(15,50)

        self.runTypeSelect = QButtonGroup()
        self.manualRadio = QRadioButton('Manual', self.settingsPage)
        self.manualRadio.move(15,75)
        self.autoRadio = QRadioButton('Auto', self.settingsPage)
        self.autoRadio.move(15,100)
        self.hideRadio = QRadioButton('Hide Window', self.settingsPage)
        self.hideRadio.move(15,125)
        self.runTypeSelect.addButton(self.manualRadio)
        self.runTypeSelect.addButton(self.autoRadio)
        self.runTypeSelect.addButton(self.hideRadio)
        self.manualRadio.setChecked(True)



    '''SUB-SUB-FUNCTIONS'''
    def __getOptions(self): # Called by _makeScriptList 
        '''Retrieves available tests and creates a dictionary with name:path pairs'''
        self.options = {}
        folder = os.listdir(self.optionsPath)
        for test in folder:
            self.options[test] = os.path.join(self.optionsPath, test)
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
        script = ''
        proj = ''
        if not item:
            testDir = self.options[self.listWidget.selectedItems()[0].text()]
        else:
            testDir = self.options[item.text()]
        testDir = list(os.walk(testDir))[0]
        for file in testDir[2]:
            if file.endswith('.pts'):
                script = os.path.join(testDir[0], file)
            if file.endswith('.ptp'):
                proj = os.path.join(testDir[0], file)
            if script != '' and proj != '':
                break
        
        runSettings = ''
        if self.autoRadio.isChecked():
            runSettings += '-r'
        elif self.hideRadio.isChecked():
            runSettings += '-r -i'

        subprocess.Popen(f'"{self.DLPath}" {runSettings} "{proj}" "{script}"', shell=True) # add -m -i to launch/run with no footprint
        
    def __folderView(self): # Called by _makeAddSubButtons
        '''Opens file explorer in options path'''
        subprocess.Popen(f'explorer "{self.optionsPath}"', shell=True)
    def __addFile(self): # Called by _makeAddSubButtons
        '''Adds selected folder to directory'''
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder == '':
            return
        try:
            os.mkdir(os.path.join(self.optionsPath, folder.split('/')[-1]))
        except FileExistsError as e:
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
    def __subFile(self): # Called by _makeAddSubButtons
        '''Removes selected folder from directory'''
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
    def __refresh(self): # Called by _makeAddSubButtons
        '''Refreshes script list'''
        optionsTemp = self.options.keys()
        self.__getOptions()
        for opt in self.options:
            if opt not in optionsTemp:
                self.listWidget.addItem(opt)
    def __handlePath(self): # Called by _makePathInput
        '''Verifies Docklight path when adding new path'''
        if self.DLPath == '':
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/dlpath.txt'), "r+") as f:
                if os.path.isfile(self.pathInput.text()) and self.pathInput.text().endswith("Docklight_Scripting.exe"):
                    f.truncate(0)
                    f.write(self.pathInput.text())
                    self.pathInput.setPlaceholderText('Valid path saved')
                    self.DLPath = self.pathInput.text()
                    self.pathInputButton.setText('Replace')
                else:
                    self.pathInput.setPlaceholderText('Invalid path. Please enter the correct path.')
                    self.pathInput.clear()
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())