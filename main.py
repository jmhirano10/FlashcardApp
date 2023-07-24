'''
Roadmap:
- (completed) Load txt file and ask question in console 
- (completed) Check question correctness and determine score
- Re-ask incorrect questions mode
- (completed) question set (txt file) selector
- (completed) List of all available question sets
- Store highscores
- All question sets mode
- (completed) Counter for answered, correct, incorrect, remaining
- (completed) GUI
- (completed) Set editor
- All questions mode
- randomized question mode

Blueprint:
main
- Receives input and print output
questions
- Loads required question set
'''

import csv
import tkinter as tk
from pathlib import Path

class Questions:
    def __init__(self):
        self.data = []
        self.index = 0
        self.correct = 0
        self.incorrect = 0
        self.remaining = 0
        self.path = Path('Questions/')

    def loadSet(self,setName):
        with open(self.path / setName,'r',encoding='utf8',newline='') as file:
            self.data = list(csv.reader(file,delimiter=','))
    
    def reset(self):
        self.index = 0
        self.correct = 0
        self.incorrect = 0 
        self.remaining = len(self.data)
    
    def getCurrentQ(self):
        return self.data[self.index][0]
    
    def checkAnswer(self,answer):
        if answer == self.data[self.index][1]:
            self.correct += 1
        else:
            self.incorrect += 1

        self.remaining -= 1
        self.index += 1
    
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
        self.availableSets = ['L6.txt']
        #self.geometry('400x300')
        self.title('Japanese Quiz')
        self.columnconfigure(0,weight=3)
        self.columnconfigure(1,weight=1)
        container = tk.Frame(self)
        container.pack(fill='both',expand=True)
        self.frames = {}
        pages = [MainMenu,SetUp,InGame,Results,Edit]
        
        for F in pages:
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky='nsew')

        self.showFrame(MainMenu)
    
    def showFrame(self,container):
        frame = self.frames[container]
        frame.tkraise()
    
    def startGame(self):
        self.questions.reset()
        self.frames[InGame].updateStats()
        self.showFrame(InGame)

class MainMenu(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        self.control = control
        scrollBar = tk.Scrollbar(self)
        questionSets = tk.Listbox(self,yscrollcommand=scrollBar.set)
        
        for set in control.availableSets:
            questionSets.insert('end',set)

        playBtn = tk.Button(self,text='Play',command=lambda:self.next(questionSets.curselection(),SetUp))
        editBtn = tk.Button(self,text='Edit',command=lambda:self.next(questionSets.curselection(),Edit))
        exitBtn = tk.Button(self,text='Exit')

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
        self.control = control

        learnBtn        = tk.Checkbutton(self,text="Learn Mode")
        randomizeBtn    = tk.Checkbutton(self,text="Randomize Set")
        timedBtn        = tk.Checkbutton(self,text="Timed")
        setLabel        = tk.Label(self,textvariable=control.currentSet)
        startBtn        = tk.Button(self,text='Start',command=lambda:control.startGame())
        backBtn         = tk.Button(self,text='Back',command=lambda:control.showFrame(MainMenu))

        learnBtn.grid(column=0,row=0,padx=10,pady=10)
        randomizeBtn.grid(column=0,row=1,padx=10,pady=10)
        timedBtn.grid(column=0,row=2,padx=10,pady=10)
        setLabel.grid(column=1,row=0,padx=10,pady=10)
        startBtn.grid(column=1,row=1,padx=10,pady=10)
        backBtn.grid(column=1,row=2,padx=10,pady=10)

class InGame(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        self.control    = control
        self.correct    = tk.IntVar(value=0)
        self.incorrect  = tk.IntVar(value=0)
        self.remaining  = tk.IntVar(value=0)
        self.question   = tk.StringVar()

        correctLabel    = tk.Label(self,textvariable=self.correct)
        incorrectLabel  = tk.Label(self,textvariable=self.incorrect)
        remainingLabel  = tk.Label(self,textvariable=self.remaining)
        questionLabel   = tk.Label(self,textvariable=self.question)
        answerEntry     = tk.Entry(self)
        enterButton     = tk.Button(self,text='Enter',command=lambda:self.enter(answerEntry.get()))
        backButton      = tk.Button(self,text='Back',command=lambda:control.showFrame(SetUp))

        correctLabel.grid(column=0,row=0,padx=10,pady=10)
        incorrectLabel.grid(column=2,row=0,padx=10,pady=10)
        remainingLabel.grid(column=1,row=0,padx=10,pady=10)
        questionLabel.grid(column=1,row=1,padx=10,pady=10)
        answerEntry.grid(column=1,row=2,padx=10,pady=10)
        enterButton.grid(column=2,row=2,padx=10,pady=10)
        backButton.grid(column=0,row=2,padx=10,pady=10)

    def enter(self,answer):
        self.control.questions.checkAnswer(answer)
        self.updateStats()
        if self.control.questions.remaining <= 0:
            self.control.showFrame(Results)
    
    def updateStats(self):
        self.correct.set(self.control.questions.correct)
        self.incorrect.set(self.control.questions.incorrect)
        self.remaining.set(self.control.questions.remaining)
        if self.control.questions.remaining > 0:
            self.question.set(self.control.questions.getCurrentQ())

class Results(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        correctLabel    = tk.Label(self,textvariable=control.frames[InGame].correct)
        incorrectLabel  = tk.Label(self,textvariable=control.frames[InGame].incorrect)
        startButton     = tk.Button(self,text='Start',command=lambda:control.startGame())
        backButton      = tk.Button(self,text='Back',command=lambda:control.showFrame(SetUp))

        correctLabel.grid(column=0,row=1,padx=10,pady=10)
        incorrectLabel.grid(column=0,row=2,padx=10,pady=10)
        startButton.grid(column=1,row=1,padx=10,pady=10)
        backButton.grid(column=1,row=2,padx=10,pady=10)

class Edit(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        self.control = control

        scrollBar = tk.Scrollbar(self)
        self.set = tk.Listbox(self,yscrollcommand=scrollBar)
        
        deleteButton    = tk.Button(self,text='Delete',command=lambda:self.delete(self.set.curselection()))
        addButton       = tk.Button(self,text='Add',command=lambda:self.add([questionEntry.get(),answerEntry.get()]))
        saveButton      = tk.Button(self,text='Save',command=lambda:self.save())
        backButton      = tk.Button(self,text='Back',command=lambda:self.back())
        answerEntry     = tk.Entry(self)
        questionEntry   = tk.Entry(self)

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
    app = QuizApp()
    app.mainloop()
