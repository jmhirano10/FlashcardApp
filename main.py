'''
Roadmap:
- (completed) Load txt file and ask question in console 
- (completed) Check question correctness and determine score
- (completed) Re-ask incorrect questions mode
- (completed) question set (txt file) selector
- (completed) List of all available question sets
- Store highscores
- All question sets mode
- (completed) Counter for answered, correct, incorrect, remaining
- (completed) GUI
- (completed) Set editor
- (completed) randomized question mode
- (completed) When wrong insta restart
- Show answer on incorrect entry for (n seconds)

Blueprint:
main
- Receives input and print output
questions
- Loads required question set
'''

import csv
import random
import time
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path

class Questions:
    def __init__(self):
        self.data       = []
        self.dataCurr   = []
        self.index      = []
        self.correct    = []
        self.incorrect  = []
        self.remaining  = 0
        self.startTime  = 0
        self.path       = Path('Questions/')

    def loadSet(self,setName):
        with open(self.path / setName,'r',encoding='utf8',newline='') as file:
            self.data = list(csv.reader(file,delimiter=','))
        self.dataCurr = self.data
    
    def reset(self):
        self.index      = list(range(0,len(self.data)))
        self.correct    = []
        self.incorrect  = []
        self.remaining  = len(self.data)

    def randomizeSet(self):
        order = []
        for i in range(0,len(self.data)):
            randint = random.randint(0,len(self.index)-1)
            order.append(self.index[randint])
            self.index.pop(randint)
        self.index = order
    
    def getCurrentQ(self):
        return self.data[self.index[0]][0]
    
    def checkAnswer(self,answer):
        corAnswer = None
        if answer == self.data[self.index[0]][1]:
            self.correct.append(self.data[self.index[0]])
        else:
            self.incorrect.append(self.data[self.index[0]])
            corAnswer = self.data[self.index[0]][1]

        self.remaining -= 1
        self.index.pop(0)
        return corAnswer
    
    def writeData(self,setName):
        with open(self.path / setName,'w',encoding='utf8',newline='') as file:
            setWriter = csv.writer(file,delimiter=',')
            setWriter.writerows(self.data)
    
    def deleteQuestion(self,index):
        self.data.pop(index)
    
    def addQuestion(self,question):
        self.data.append(question)
    
class QuizApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.questions = Questions()
        self.currentSet = tk.StringVar()
        self.availableSets = ['L5.txt','L6.txt','L7.txt','L8.txt','L9.txt','K.txt','K1.txt','K2.txt','K3.txt','K4.txt','K5.txt','K6.txt','K7.txt','K8.txt','K9.txt','KNew.txt','Phone.txt','PhoneVerb.txt','NewWords.txt','Phrases.txt']
        self.geometry('600x400')
        self.title('Japanese Quiz')
        container = tk.Frame(self)
        container.pack(fill='both',expand=True)
        self.frames = {}
        self.pages = [MainMenu,SetUp,InGame,Results,Edit,Answer]
        
        for F in self.pages:
            frame = F(container,self)
            self.frames[F] = frame
            frame.pack(expand=True)

        self.showFrame(MainMenu)
    
    def showFrame(self,container):
        for page in self.pages:
            self.frames[page].pack_forget()
        self.frames[container].pack(expand=True)
        
    
    def startGame(self,newGame=True):
        if newGame:
            self.questions.data = self.questions.dataCurr
            self.frames[Results].timeResult.set('')
            if self.frames[SetUp].timed.get():
                self.questions.startTime = time.time()
        self.questions.reset()
        if self.frames[SetUp].randomize.get():
            self.questions.randomizeSet()
        self.frames[InGame].noFail = self.frames[SetUp].noFail.get()
        self.frames[InGame].updateStats()
        self.showFrame(InGame)
    
    def endGame(self):
        if self.frames[SetUp].learnmode.get() and len(self.questions.incorrect):
            self.questions.data = self.questions.incorrect
            self.startGame(False)
        else:
            self.questions.data = self.questions.dataCurr
            if self.frames[SetUp].timed.get():
                self.frames[Results].timeResult.set(str(time.time()-self.questions.startTime))
            self.showFrame(Results)
    
    def showAnswer(self,answer):
        self.frames[Answer].corAnswer.set(answer)
        self.showFrame(Answer)
    
    def resumeGame(self):
        self.frames[InGame].updateStats()
        if self.frames[InGame].noFail:
            if len(self.questions.incorrect) > 0:
                self.startGame()
        if self.questions.remaining <= 0:
            self.endGame()
        else:
            self.showFrame(InGame)

class MainMenu(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        self.control = control
        scrollBar = ttk.Scrollbar(self)
        questionSets = tk.Listbox(self,yscrollcommand=scrollBar.set)
        
        for set in control.availableSets:
            questionSets.insert('end',set)

        playBtn = ttk.Button(self,text='Play',command=lambda:self.next(questionSets.curselection(),SetUp))
        editBtn = ttk.Button(self,text='Edit',command=lambda:self.next(questionSets.curselection(),Edit))
        exitBtn = ttk.Button(self,text='Exit',command=lambda:exit())

        questionSets.grid(column=0,row=0,rowspan=3,padx=10,pady=10)
        playBtn.grid(column=1,row=0,padx=10,pady=10)
        editBtn.grid(column=1,row=1,padx=10,pady=10)
        exitBtn.grid(column=1,row=2,padx=10,pady=10)
    
    def next(self,set,frame):
        self.control.currentSet.set(self.control.availableSets[set[0]])
        self.control.questions.loadSet(self.control.currentSet.get())
        self.control.showFrame(frame)

        if frame == Edit:
            for q in self.control.questions.data:
                question = q[0] + ', ' + q[1]
                self.control.frames[Edit].set.insert('end',question)
        
class SetUp(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        self.control    = control
        self.noFail     = tk.BooleanVar()
        self.randomize  = tk.BooleanVar()
        self.learnmode  = tk.BooleanVar()
        self.timed      = tk.BooleanVar()

        noFailBtn       = ttk.Checkbutton(self,text='No Incorrect Answers',variable=self.noFail)
        learnBtn        = ttk.Checkbutton(self,text="Learn Mode",variable=self.learnmode)
        randomizeBtn    = ttk.Checkbutton(self,text="Randomize Set",variable=self.randomize)
        timedBtn        = ttk.Checkbutton(self,text="Timed",variable=self.timed)
        setLabel        = ttk.Label(self,textvariable=control.currentSet)
        startBtn        = ttk.Button(self,text='Start',command=lambda:control.startGame())
        backBtn         = ttk.Button(self,text='Back',command=lambda:control.showFrame(MainMenu))

        noFailBtn.grid(column=0,row=0,columnspan=2,padx=10,pady=10)
        learnBtn.grid(column=0,row=1,padx=10,pady=10)
        randomizeBtn.grid(column=0,row=2,padx=10,pady=10)
        timedBtn.grid(column=0,row=3,padx=10,pady=10)
        setLabel.grid(column=1,row=1,padx=10,pady=10)
        startBtn.grid(column=1,row=2,padx=10,pady=10)
        backBtn.grid(column=1,row=3,padx=10,pady=10)

class InGame(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        self.control    = control
        self.noFail     = False
        self.correct    = tk.IntVar(value=0)
        self.incorrect  = tk.IntVar(value=0)
        self.remaining  = tk.IntVar(value=0)
        self.question   = tk.StringVar()

        correctLabel    = ttk.Label(self,textvariable=self.correct)
        incorrectLabel  = ttk.Label(self,textvariable=self.incorrect)
        remainingLabel  = ttk.Label(self,textvariable=self.remaining)
        questionLabel   = ttk.Label(self,textvariable=self.question,font=('Arial', 30))
        answerEntry     = ttk.Entry(self)
        enterButton     = ttk.Button(self,text='Enter',command=lambda:self.enter(answerEntry))
        backButton      = ttk.Button(self,text='Back',command=lambda:control.showFrame(SetUp))

        correctLabel.grid(column=0,row=0,padx=10,pady=10)
        incorrectLabel.grid(column=2,row=0,padx=10,pady=10)
        remainingLabel.grid(column=1,row=0,padx=10,pady=10)
        questionLabel.grid(column=1,row=1,padx=10,pady=10)
        answerEntry.grid(column=1,row=2,padx=10,pady=10)
        enterButton.grid(column=2,row=2,padx=10,pady=10)
        backButton.grid(column=0,row=2,padx=10,pady=10)

        control.bind('<Return>',lambda event:self.enter(answerEntry))

    def enter(self,answerEntry):
        answer = answerEntry.get()
        answerEntry.delete(0,'end')
        isCorrect = self.control.questions.checkAnswer(answer)
        if isCorrect:
            self.control.showAnswer(isCorrect)
        else:
            self.control.resumeGame()
    
    def updateStats(self):
        self.correct.set(len(self.control.questions.correct))
        self.incorrect.set(len(self.control.questions.incorrect))
        self.remaining.set(self.control.questions.remaining)
        if self.control.questions.remaining > 0:
            self.question.set(self.control.questions.getCurrentQ())

class Answer(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        self.corAnswer  = tk.StringVar()

        corAnsLabel     = ttk.Label(self,textvariable=self.corAnswer)

        corAnsLabel.grid(column=0,row=0)

        control.bind('<Control_L>',lambda event:control.resumeGame())

class Results(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        self.timeResult = tk.StringVar()

        correctText     = ttk.Label(self,text='Correct')
        incorrectText   = ttk.Label(self,text='Incorrect')
        correctLabel    = ttk.Label(self,textvariable=control.frames[InGame].correct)
        incorrectLabel  = ttk.Label(self,textvariable=control.frames[InGame].incorrect)
        timerLabel      = ttk.Label(self,textvariable=self.timeResult)
        startButton     = ttk.Button(self,text='Start',command=lambda:control.startGame())
        backButton      = ttk.Button(self,text='Back',command=lambda:control.showFrame(SetUp))

        correctText.grid(column=0,row=1,padx=10,pady=10)
        incorrectText.grid(column=2,row=1,padx=10,pady=10)
        correctLabel.grid(column=1,row=1,padx=10,pady=10)
        incorrectLabel.grid(column=3,row=1,padx=10,pady=10)
        timerLabel.grid(column=1,row=0,columnspan=2,padx=10,pady=10)
        startButton.grid(column=0,row=2,columnspan=2,padx=10,pady=10)
        backButton.grid(column=2,row=2,columnspan=2,padx=10,pady=10)

class Edit(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        self.control = control

        scrollBar       = ttk.Scrollbar(self)
        self.set        = tk.Listbox(self,yscrollcommand=scrollBar)
        deleteButton    = ttk.Button(self,text='Delete',command=lambda:self.delete(self.set.curselection()))
        addButton       = ttk.Button(self,text='Add',command=lambda:self.add([questionEntry.get(),answerEntry.get()]))
        saveButton      = ttk.Button(self,text='Save',command=lambda:self.save())
        backButton      = ttk.Button(self,text='Back',command=lambda:self.back())
        answerEntry     = ttk.Entry(self)
        questionEntry   = ttk.Entry(self)

        self.set.grid(column=0,row=0,rowspan=4,padx=10,pady=10)
        answerEntry.grid(column=1,row=0,padx=10,pady=10)
        questionEntry.grid(column=1,row=1,padx=10,pady=10)
        addButton.grid(column=1,row=2,padx=10,pady=10)
        deleteButton.grid(column=1,row=3,padx=10,pady=10)
        saveButton.grid(column=1,row=4,padx=10,pady=10)
        backButton.grid(column=0,row=4,padx=10,pady=10)

    
    def delete(self,question):
        self.control.questions.deleteQuestion(question[0])
        self.set.delete(question[0])
    
    def add(self,question):
        self.control.questions.addQuestion(question)
        question = question[0] + ', ' + question[1]
        self.set.insert('end',question)
    
    def save(self):
        self.control.questions.writeData(self.control.currentSet.get())

    def back(self):
        self.control.showFrame(MainMenu)
        self.set.delete(0,'end')

if __name__ == '__main__':
    #ctypes.windll.shcore.SetProcessDpiAwareness(1)
    app = QuizApp()
    app.mainloop()
