import sys
import os.path
import logging
from time import sleep
from PyQt5.QtCore import pyqtSlot, QSettings, Qt, QCoreApplication, QTimer
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QPushButton, QAction
from random import randint
from pickle import dump,load

class TCubeGame(QMainWindow):
    def __init__(self, parent= None):
        super().__init__(parent)
        logging.basicConfig(filename='TCubed.log',level=logging.DEBUG, format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s')
        self.appSettings = QSettings('JD', 'TCubedSettings')
        uic.loadUi("TicTacToe.ui",self)
        self.buttonText=[["one","",0,0],["two","",1,0],["three","",2,0],["four","",3,0],["five","",4,0],["six","",5,0],["seven","",6,0],["eight","",7,0],["nine","",8,0]]
        self.pushButtonList=[self.one, self.two, self.three, self.four, self.five, self.six, self.seven, self.eight, self.nine]
        self.topRow = self.buttonText[0:3]
        self.middleRow = self.buttonText[3:6]
        self.bottomRow = self.buttonText[6:9]
        self.player = "X"
        self.cpu="O"
        self.cpuMoveFirst=False
        self.results="Tic Tac Toe"
        self.difficulty="Normal"
        self.wins=0
        self.losses=0
        self.draws=0
        self.one.clicked.connect(lambda :self.buttonClickedHandler(self.one,'one'))
        self.two.clicked.connect(lambda :self.buttonClickedHandler(self.two, 'two'))
        self.three.clicked.connect(lambda :self.buttonClickedHandler(self.three, 'three'))
        self.four.clicked.connect(lambda :self.buttonClickedHandler(self.four,'four'))
        self.five.clicked.connect(lambda :self.buttonClickedHandler(self.five, 'five'))
        self.six.clicked.connect(lambda :self.buttonClickedHandler(self.six, 'six'))
        self.seven.clicked.connect(lambda :self.buttonClickedHandler(self.seven, 'seven'))
        self.eight.clicked.connect(lambda :self.buttonClickedHandler(self.eight, 'eight'))
        self.nine.clicked.connect(lambda :self.buttonClickedHandler(self.nine, 'nine'))
        self.actionRestart.triggered.connect(self.restartGame)
        self.actionPreferences.triggered.connect(self.preferencesAction)
        self.restartTimer=QTimer()

    def closeEvent(self, event):
        self.saveGame()

    def loadUI(self):
        try:
            with open("tCubedPickle.pl", 'rb') as inputFile:
                self.buttonText,self.wins,self.losses,self.draws=load(inputFile)
                logging.debug("Loaded Pickle File")
        except:
            logging.debug("Pickle File Does not Exist.")
        for item in self.buttonText:
            thisButton=self.pushButtonList[item[2]]
            if item[1] is not "":
                thisButton.setEnabled(False)
                thisButton.setText(item[1])
            else:
                thisButton.setText("")
        self.resultsLabel.setText(str(self.results))
        self.firstScoreLabel.setText(str(self.wins))
        self.secondScoreLabel.setText(str(self.losses))
        self.drawScoreLabel.setText(str(self.draws))
        self.loadSettings()
        logging.debug("Loaded UI")

    def preferencesAction(self):
        preferencesWindow.show()

    def saveGame(self):
        with open("tCubedPickle.pl", 'wb') as tCubedPickle:
            dump((self.buttonText,self.wins,self.losses,self.draws), tCubedPickle)
        logging.debug("Saved Game")

    def loadSettings(self):
        if self.appSettings.contains('playerMark'):
            self.player = self.appSettings.value('playerMark', type=str)
        else:
            self.player = "X"
        if self.player == "O":
            self.cpu="X"
        else:
            self.cpu="O"
        if self.appSettings.contains('cpuMoveFirst'):
            self.cpuMoveFirst = self.appSettings.value('cpuMoveFirst', type=bool)
        else:
            self.cpuMoveFirst = False
        if self.appSettings.contains('difficulty'):
            self.difficulty = self.appSettings.value('difficulty', type=str)
        else:
            self.difficulty = "Normal"

    def restartGame(self):
        self.loadSettings()
        self.buttonText = [["one", "", 0, 0], ["two", "", 1, 0], ["three", "", 2, 0],
                           ["four", "", 3, 0], ["five", "", 4, 0], ["six", "", 5, 0],
                           ["seven", "", 6, 0], ["eight", "", 7, 0], ["nine", "",8, 0]]
        self.results = "Tic Tac Toe"
        for item in self.buttonText:
            thisButton=self.pushButtonList[item[2]]
            thisButton.setEnabled(True)
            thisButton.setText("")
        self.resultsLabel.setText(str(self.results))
        if self.cpuMoveFirst is True:
            cpuSelectedNum = self.cpuWinCheck(self.topRow, self.middleRow, self.bottomRow)
            cpuSelectedButton = self.pushButtonList[cpuSelectedNum]
            if cpuSelectedButton is not None:
                for item in self.buttonText:
                    if self.pushButtonList[item[2]] is cpuSelectedButton:
                        item[1] = self.cpu
                        item[3] = 3
                cpuSelectedButton.setEnabled(False)
                cpuSelectedButton.setText(self.cpu)
        logging.info("Restarted Game")

    def winCheck(self, topRow, middleRow, bottomRow, player):
        self.movesAvailable=False
        threeInARow=player+player+player
        rowList =[topRow, middleRow, bottomRow]
        for number in range(0,3):
            if topRow[number][1] + middleRow[number][1] + bottomRow[number][1] == threeInARow:
                self.updateWinLosses(player)
        for row in rowList:
            if row[0][1] + row[1][1] + row[2][1] == threeInARow:
                self.updateWinLosses(player)
        if topRow[0][1] is player:
            if middleRow[1][1] is player:
                if bottomRow[2][1] is player:
                    self.updateWinLosses(player)
        if topRow[2][1] is player:
            if middleRow[1][1] is player:
                if bottomRow[0][1] is player:
                    self.updateWinLosses(player)
        for button in self.buttonText:
            if button[3] == 0:
                self.movesAvailable=True
        if self.movesAvailable is False and self.results == "Tic Tac Toe":
            self.results="Draw"
            self.draws+=1
            self.drawScoreLabel.setText(str(self.draws))
            self.resultsLabel.setText(self.results)
            self.restartTimer.singleShot(3000, self.restartGame)

    def updateWinLosses(self, player):
        for buttons in self.pushButtonList:
            buttons.setEnabled(False)
        self.results = "%s Wins" % (player)
        logging.info("%s Wins" % (player))
        self.resultsLabel.setText(self.results)
        if player is self.player:
            self.wins += 1
        elif player is self.cpu:
            self.losses += 1
        self.firstScoreLabel.setText(str(self.wins))
        self.secondScoreLabel.setText(str(self.losses))
        self.restartTimer.singleShot(3000, self.restartGame)

    def cpuWinCheck(self,topRow, middleRow, bottomRow):
        moveMade = 0
        self.movesAvailable=False
        winMovesList=[]
        blockMovesList=[]
        rowList = [topRow, middleRow, bottomRow]
        winOrBlockList=[]
        for possibleMoves in self.buttonText:
            if possibleMoves[3] is 0:
                self.movesAvailable = True
        if self.movesAvailable is True:
            for number in range(0, 3):
                if (topRow[number][3] + middleRow[number][3] + bottomRow[number][3]) is 6:
                    if topRow[number] not in winMovesList:
                        winMovesList.append(topRow[number])
                    if middleRow[number] not in winMovesList:
                        winMovesList.append(middleRow[number])
                    if bottomRow[number] not in winMovesList:
                        winMovesList.append(bottomRow[number])
            for row in rowList:
                if row[0][3] + row[1][3] + row[2][3] is 6:
                    if row[0] not in winMovesList:
                        winMovesList.append(row[0])
                    if row[1] not in winMovesList:
                        winMovesList.append(row[1])
                    if row[2] not in winMovesList:
                        winMovesList.append(row[2])
            if topRow[0][3]+ middleRow[1][3] + bottomRow[2][3] is 6:
                if topRow[0] not in winMovesList:
                    winMovesList.append(topRow[0])
                if middleRow[1] not in winMovesList:
                    winMovesList.append(middleRow[1])
                if bottomRow[2] not in winMovesList:
                    winMovesList.append(bottomRow[2])
            if topRow[2][3] + middleRow[1][3] + bottomRow[0][3] is 6:
                if topRow[2] not in winMovesList:
                    winMovesList.append(topRow[2])
                if middleRow[1] not in winMovesList:
                    winMovesList.append(middleRow[1])
                if bottomRow[0] not in winMovesList:
                    winMovesList.append(bottomRow[0])
            for number in range(0, 3):
                if topRow[number][3] + middleRow[number][3] + bottomRow[number][3] is 2:
                    if topRow[number] not in blockMovesList:
                        blockMovesList.append(topRow[number])
                    if middleRow[number] not in blockMovesList:
                        blockMovesList.append(middleRow[number])
                    if bottomRow[number] not in blockMovesList:
                        blockMovesList.append(bottomRow[number])
            for row in rowList:
                if row[0][3] + row[1][3] + row[2][3] is 2:
                    if row[0] not in blockMovesList:
                        blockMovesList.append(row[0])
                    if row[1] not in blockMovesList:
                        blockMovesList.append(row[1])
                    if row[2] not in blockMovesList:
                        blockMovesList.append(row[2])
            if topRow[0][3]+ middleRow[1][3] + bottomRow[2][3] is 2:
                if topRow[0] not in blockMovesList:
                    blockMovesList.append(topRow[0])
                if middleRow[1] not in blockMovesList:
                    blockMovesList.append(middleRow[1])
                if bottomRow[2] not in blockMovesList:
                    blockMovesList.append(bottomRow[2])
            if topRow[2][3] + middleRow[1][3] + bottomRow[0][3] is 2:
                if topRow[2] not in blockMovesList:
                    blockMovesList.append(topRow[2])
                if middleRow[1] not in blockMovesList:
                    blockMovesList.append(middleRow[1])
                if bottomRow[0] not in blockMovesList:
                    blockMovesList.append(bottomRow[0])
            for moves in winMovesList:
                if moves[3] is 0:
                    winOrBlockList.append(moves)
            for moves in blockMovesList:
                if moves[3] is 0:
                    winOrBlockList.append(moves)
            if self.difficulty == "Easy":
                winOrBlockList=[]
            if len(winOrBlockList) is 0:
                logging.info("CPU has chosen Random Move")
                while(moveMade is 0):
                    randomNumber=randint(0,8)
                    if self.buttonText[randomNumber][3] is 0:
                        moveMade += 1
                        return self.buttonText[randomNumber][2]
            else:
                logging.info("CPU has chosen a Win Or Block Move")
                return winOrBlockList[0][2]
        else:
            return None

    @pyqtSlot()
    def buttonClickedHandler(self,button, num):
        logging.info("Player Has Selected A Button.")
        for item in self.buttonText:
            if item[0] == num:
                item[1]= self.player
                item[3]=1
        button.setEnabled(False)
        button.setText(self.player)
        self.topRow = self.buttonText[0:3]
        self.middleRow = self.buttonText[3:6]
        self.bottomRow = self.buttonText[6:9]
        self.winCheck(self.topRow,self.middleRow,self.bottomRow,self.player)
        if self.results == "Tic Tac Toe":
            cpuSelectedNum=self.cpuWinCheck(self.topRow,self.middleRow,self.bottomRow)
            cpuSelectedButton=self.pushButtonList[cpuSelectedNum]
            if cpuSelectedButton is not None:
                for item in self.buttonText:
                    if self.pushButtonList[item[2]] is cpuSelectedButton:
                        item[1] = self.cpu
                        item[3] = 3
                cpuSelectedButton.setEnabled(False)
                cpuSelectedButton.setText(self.cpu)
            self.winCheck(self.topRow,self.middleRow,self.bottomRow,self.cpu)

class preferencesDialog(QDialog):
    def __init__(self, parent=TCubeGame):
        super(preferencesDialog, self).__init__()
        uic.loadUi('TCubedPreferences.ui',self)
        self.appSettings = QSettings('JD', 'TCubedSettings')
        if self.appSettings.contains('playerMark'):
            self.player = self.appSettings.value('playerMark', type=str)
            if self.player == "O":
                self.boxState=True
            else:
                self.boxState=False
        else:
            self.player = "X"
            self.boxState=False
            self.appSettings.setValue('playerMark', self.player)

        if self.appSettings.contains('cpuMoveFirst'):
            self.cpuMoveFirst = self.appSettings.value('cpuMoveFirst', type=bool)
        else:
            self.cpuMoveFirst = False
            self.appSettings.setValue('cpuMoveFirst', self.cpuMoveFirst)

        if self.appSettings.contains('difficulty'):
            self.difficulty = self.appSettings.value('difficulty', type=str)
            if self.difficulty == "Easy":
                self.easyButton.setChecked(True)
                self.hardButton.setChecked(False)
        else:
            self.difficulty = "Hard"
            self.easyButton.setChecked(False)
            self.hardButton.setChecked(True)

        self.easyButton.toggled.connect(self.difficultyHandler)
        self.playerMarkBox.setChecked(self.boxState)
        self.moveFirst.setChecked(self.cpuMoveFirst)
        self.playerMarkBox.stateChanged.connect(self.playerBoxChecked)
        self.moveFirst.stateChanged.connect(self.moveBoxChecked)
        self.buttonBox.rejected.connect(self.cancelClickedHandler)
        self.buttonBox.accepted.connect(self.okayClickedHandler)


    @pyqtSlot()
    def playerBoxChecked(self):
        if self.playerMarkBox.isChecked() is True:
            self.player="O"
        else:
            self.player="X"

    @pyqtSlot()
    def moveBoxChecked(self):
        if self.moveFirst.isChecked() is True:
            self.cpuMoveFirst=True
        else:
            self.cpuMoveFirst=False

    @pyqtSlot()
    def difficultyHandler(self):
        if self.hardButton.isChecked() is False:
            self.difficulty="Easy"
        else:
            self.difficulty="Hard"

    @pyqtSlot()
    def cancelClickedHandler(self):
        self.close()

    @pyqtSlot()
    def okayClickedHandler(self):
        self.appSettings.setValue('playerMark', self.player)
        self.appSettings.setValue('cpuMoveFirst', self.cpuMoveFirst)
        self.appSettings.setValue('difficulty', self.difficulty)
        self.close()
        TCubeApp.restartGame()

if __name__ == "__main__":
    appSettings= QSettings('JD', 'TCubedSettings')
    app = QApplication(sys.argv)
    TCubeApp= TCubeGame()
    TCubeApp.show()
    TCubeApp.loadUI()
    preferencesWindow=preferencesDialog()
    sys.exit(app.exec_())












