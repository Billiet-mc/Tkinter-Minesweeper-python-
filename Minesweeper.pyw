from tkinter import *
from tkinter import ttk
from random import choice


#this class is basically just a regular button class but it adds a few attributes + a reveal function and a onRightClick function
class gridButton(Button):


    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        #id is calculated using the widgets internal name which includes its number
        self.id = ''.join(i for i in self.winfo_name() if i.isdigit())
        self.id = int(self.id)-1 if not self.id == '' else 0
        self.isFlagged = 0
        self.isRevealed = 0
        self.isMine = 0
        self.mineNumber = 0

    #game logic that happend when a button is revealed (changes from hidden to revealed)
    def revealButton(self):
        global GAME_OVER
        global freeze

        #if statement checks if the game is still ongoing and if the button is not flagged
        if not GAME_OVER and not self.isFlagged:
            
            #first case: the button you revealed is a mine
            if self.isMine == 1:
                self.config(image = mineImage)
                GAME_OVER = True
                #freezes the timer
                freeze = True

                #reveals all mines and sets the state of all other buttons to 'disabled'
                for i in buttons:
                    if i.isMine:
                        i.config(image = mineImage)
                    else:
                        i.config(state='disabled')
                resetButton.config(text='You Lose... Back to Home Screen?', command=lambda: reLoadHomeScreen())
            #else case: the button you revealed is NOT a mine
            else:
                #make the button display the appropriate number and set the relief to groove to make it disctinct from hidden buttons
                self.config(relief='groove', background='gray75', activebackground='gray75', image=mineNumberImages[self.mineNumber-1])
                self.isRevealed = 1

                #add up the total amount of revealed buttons and mines
                revealedCount = 0
                mineCount = 0 
                for i in buttons:
                    if i.isRevealed:
                        revealedCount = revealedCount + 1
                    elif i.isMine:
                        mineCount = mineCount + 1

                
                #check if game is won (if all non mine buttons are revealed)
                if revealedCount == len(buttons) - mineCount:
                    GAME_OVER = True
                    freeze = True
                    #reveals all mines (does not set any buttons to 'disabled' like it would if the player lost)
                    for i in buttons:
                        if i.isMine:
                            i.config(image = mineImage)
                        else:
                            i.config()
                    resetButton.config(text='You Win! Back to Home Screen?', command=lambda: reLoadHomeScreen())

                    
        #this is to prevent the button appearing to be pressed after losing/winning the game or being pressed while flagged
        else:
            self.config(relief='raised') if not self.isRevealed else self.config(relief='groove')




    #set a flag on a hidden button or remove a flag on a hidden button
    def onRightClick(self):
        if not GAME_OVER and not self.isRevealed:
            self.config(image = hiddenImage if self.isFlagged else flagImage)
            self.isFlagged = not self.isFlagged


#global variables
GAME_OVER = False
freeze = False

#setting up root window
root = Tk()
root.title("Minesweeper")
root.rowconfigure(0, weight=1)
root.columnconfigure(0,weight=1)



debugStyle = ttk.Style()
debugStyle.configure('red.TFrame', background = 'red')


#overarching all encompassing containing super frame

mainFrame = ttk.Frame(root)
mainFrame.grid(row=0, column=0, sticky=N + E + S + W)
mainFrame.rowconfigure(0, weight=1)
mainFrame.columnconfigure(0,weight=1)


#gameSreen is the frame that contains everything the player sees when not in the home screen (the minefield, timer, and reset button, and title above the minefield)
gameScreen = ttk.Frame(mainFrame)
gameScreen.grid(row=0, column=0, sticky=N + S + W + E)

#ten rows are needed to make the minefeild frame take up a much larger portion (9/10) of the screen than the top ribbon display
for i in range(1,10):
    gameScreen.rowconfigure(i, weight=1)
gameScreen.columnconfigure(0, weight=1)


#style used to make the background gray in the gamescreen
botStyle = ttk.Style()
botStyle.configure('gray.TFrame', background='gray75')
botStyle.configure('reset.TButton', font=('Arial'), highlightthickness = 0)

#defining Images used
hiddenImage = PhotoImage(file='images/hidden.gif')
mineImage = PhotoImage(file = 'images/mine.gif')
nullImage = PhotoImage(file = 'images/null.gif')
flagImage = PhotoImage(file = 'images/flag.gif')
mineNumberImages = []
for i in range(8):
    mineNumberImages.append(PhotoImage(file=f"images/{i+1}.gif"))
#this is because the gridButton class assigns a number image based on minenumber-1 (because of index stuff) and 0-1 wraps around to the end
mineNumberImages.append(nullImage)

#setting the stringvar to be used by the label
#everything defined here is defined here so it can be accessed by reLoadGameScreen() and updateLabels()
time = StringVar()
time.set('Time: 0')
width = StringVar()
height = StringVar()
topFrame = ttk.Frame(gameScreen)
resetButton = ttk.Button(topFrame, style = 'reset.TButton', text='Reset', command= lambda: reLoadGameScreen((width.get(), height.get()), 1, gameScreen))
startScreen = ttk.Frame(mainFrame, style='gray.TFrame')
error = StringVar()
errorLabel = ttk.Label(startScreen, style='gray.TLabel', textvariable=error, font=('Arial 10'))



buttons = []
#dimensions of the grid (w,h)
buttonDim = (20,20)
#you can adjust difficulty by taking a slice of this list to include less 0s.  
# doing random.choice() on this list unsliced will return a mine (AKA a 1) about 20% of the time
difficulty = [1,1,0,0,0,0,0,0,0,0]




#returns a list containing the 3x3 grid of buttons that has centerButton at the center
#if the button is an edge button it returns all existing surrounding buttons 
def getSurroundingButtons(centerButton):
    surroundingButtons = []
    centerButtonRow = int(centerButton.id/buttonDim[0])
    centerButtonColumn = centerButton.id%buttonDim[0]
    for i in buttons:
        irow = int(i.id/buttonDim[0])
        icolumn = i.id%buttonDim[0]
        if (centerButtonColumn-1 == icolumn or centerButtonColumn+1 == icolumn or centerButtonColumn == icolumn) and (centerButtonRow-1 == irow or centerButtonRow+1 == irow or centerButtonRow == irow):
            surroundingButtons.append(i)
    return surroundingButtons



#if you clicked a blank button it clicks all neighboring buttons that arent mines (if one of the neighboring buttons is another blank button it recursively clicks that one too)
#if you clicked anything else it just reveals that one button
def buttonClicked(centerButton):
    if not GAME_OVER:
        surroundingButtons = getSurroundingButtons(centerButton)
        if centerButton.mineNumber == 0:
            #prevents a user clicked button from changing releif when being pressed 
            centerButton.config(relief='groove')
            for i in surroundingButtons:
                if i.mineNumber > 0 and not i.isRevealed and not i.isMine:
                    i.revealButton()
                elif i.mineNumber == 0 and not i.isRevealed:
                    i.revealButton()
                    buttonClicked(i)

        elif centerButton.mineNumber > 0:
            centerButton.revealButton()

    #prevents a user clicked button from changing releif when being pressed when the game is over  
    elif GAME_OVER:
        if centerButton.isMine:
            centerButton.config(relief = 'raised')
        elif not centerButton.isRevealed:
            centerButton.config(relief = 'raised')
        else:
            centerButton.config(relief = 'groove')
 
    


#schedules a call to itself which updates the timer every second (after method does not use recursion)
#should only be called once throughought the entire program
def updateLabels():
    if not freeze:
        gameScreen.after(1000, lambda: (time.set(f'Time: {int(time.get()[5:])+1}'), updateLabels()))







def reLoadHomeScreen():

    global freeze
    freeze = True
    

    #################################
    #          start screen         #
    #################################



    startScreen.grid(row=0, column=0, sticky=N + E + S + W)
    startScreen.rowconfigure(0, weight=1)
    startScreen.rowconfigure(1, weight=1)
    startScreen.rowconfigure(3, weight=1)
    startScreen.rowconfigure(4, weight=1)
    startScreen.columnconfigure(0,weight=1)
    startScreen.columnconfigure(2, weight=1)


    #Setting up widgets for the home screen

    #setting up labels
    grayLabelStyle = ttk.Style()
    grayLabelStyle.configure('gray.TLabel', background = 'gray75')

    ttk.Label(startScreen, style='gray.TLabel', text='''
███╗░░░███╗██╗███╗░░██╗███████╗░██████╗░██╗░░░░░░░██╗███████╗███████╗██████╗░███████╗██████╗░
████╗░████║██║████╗░██║██╔════╝██╔════╝░██║░░██╗░░██║██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗
██╔████╔██║██║██╔██╗██║█████╗░░╚█████╗░░╚██╗████╗██╔╝█████╗░░█████╗░░██████╔╝█████╗░░██████╔╝
██║╚██╔╝██║██║██║╚████║██╔══╝░░░╚═══██╗░░████╔═████║░██╔══╝░░██╔══╝░░██╔═══╝░██╔══╝░░██╔══██╗
██║░╚═╝░██║██║██║░╚███║███████╗██████╔╝░░╚██╔╝░╚██╔╝░███████╗███████╗██║░░░░░███████╗██║░░██║
╚═╝░░░░░╚═╝╚═╝╚═╝░░╚══╝╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚══════╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝''', font=('Arial',8)).grid(row=0, column=0, sticky=S, columnspan=3)
    ttk.Label(startScreen, style='gray.TLabel', text='Grid Dimensions:', font=('Arial 12')).grid(row=1, column=1, sticky=W+S)


    #setting up Entries

    width.set(10)
    height.set(10)


    widthEntry = ttk.Entry(startScreen, textvariable=width, width=4)
    widthEntry.grid(row=1, column=1, sticky=E+S, padx=45)

    ttk.Label(startScreen, style='gray.TLabel', text='x', font=('Arial 12')).grid(row=1, column=1, sticky=E+S, padx=32)

    heightEntry = ttk.Entry(startScreen, textvariable=height, width=4)
    heightEntry.grid(row=1, column=1, sticky=E+S)


    error.set('')
    errorLabel.grid(row=2, column=1)


    ttk.Label(startScreen, style='gray.TLabel', font='Arial 12', text='Controls:\n\nLeft-Click: Reveal Square\nRight-Click: Flag Square\nEscape: Return to Home Screen', justify='center').grid(row=3, column=1)


    #start button
    Button(startScreen, text='Start Game', command= lambda: (reLoadGameScreen((width.get(), height.get()))), font=('Arial 13')).grid(row=4, column=0, sticky=N, columnspan=3)
    root.minsize(850,450)









def reLoadGameScreen(userButtonDim, resetTimer = 0, fromScreen = startScreen):
    global freeze
    global GAME_OVER
    global buttonDim


    #logic to check if the input dimensions are valid
    try:

        if int(userButtonDim[0]) > 0 and int(userButtonDim[1]) > 0:
            print(userButtonDim[0])
            buttonDim = (int(userButtonDim[0]), int(userButtonDim[1]))
        else:
            error.set('Invalid Dimensions!')
            errorLabel.update()
            return ''
        
    except ValueError:
        error.set('Invalid Dimensions!')
        errorLabel.update()
        return ''
    

    #if user is coming from the homescreen (pressed the start game button instead of the reset button) remove the start screen and unfreeze timer
    if fromScreen == startScreen:
        startScreen.grid_forget()
        gameScreen.grid()
        freeze = False
        time.set('Time: 0')

    
    GAME_OVER = False
    resetButton.config(text='Reset', command=lambda: reLoadGameScreen(userButtonDim, 1, gameScreen))
    gameScreen.focus()

    ############################
    #         top frame        #
    ############################

    #nothing special just configuring the labels

    topFrame.grid(row=0, column=0, sticky=N + E + W + S)
    topFrame.rowconfigure(0, weight=1)
    topFrame.columnconfigure(0, weight=1, uniform='fred')
    topFrame.columnconfigure(1, weight=1, uniform='fred')
    topFrame.columnconfigure(2, weight=1, uniform='fred')

    resetButton.grid(row=0, column=0)

    ttk.Label(topFrame, text='''
███╗░░░███╗██╗███╗░░██╗███████╗░██████╗░██╗░░░░░░░██╗███████╗███████╗██████╗░███████╗██████╗░
████╗░████║██║████╗░██║██╔════╝██╔════╝░██║░░██╗░░██║██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗
██╔████╔██║██║██╔██╗██║█████╗░░╚█████╗░░╚██╗████╗██╔╝█████╗░░█████╗░░██████╔╝█████╗░░██████╔╝
██║╚██╔╝██║██║██║╚████║██╔══╝░░░╚═══██╗░░████╔═████║░██╔══╝░░██╔══╝░░██╔═══╝░██╔══╝░░██╔══██╗
██║░╚═╝░██║██║██║░╚███║███████╗██████╔╝░░╚██╔╝░╚██╔╝░███████╗███████╗██║░░░░░███████╗██║░░██║
╚═╝░░░░░╚═╝╚═╝╚═╝░░╚══╝╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚══════╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝''', font='Arial 3').grid(row=0, column=0, columnspan=3)

    timeLabel = ttk.Label(topFrame, textvariable=time, font='Arial')
    timeLabel.grid(row=0, column=2)
    updateLabels() if not resetTimer else  time.set('Time: 0')

    


    ############################
    #       bottom frame       #
    ############################

    #destroys all existing buttons and set buttons to a blank list
    global buttons
    if len(buttons) > 0:
        for i in buttons:
            i.destroy()
        buttons = []




    #setting up overarching containing frame of the minefield
    botFrame = Frame(gameScreen, background='gray50')
    botFrame.grid(row=1, column=0, sticky=N + E + W + S, rowspan=9)
    botFrame.columnconfigure(0, weight=1)
    # botFrame.rowconfigure(0, weight=1) #uncomment to make the button grid centered vertically


    #setting up the secondary frame containing the button grid
    buttonFrame = ttk.Frame(botFrame)
    buttonFrame.grid(row=0,column=0)

    # START OF BUTTON GRID CODE #

    #generating all the buttons
    for i in range((buttonDim[0]*buttonDim[1])):
        buttons.append(gridButton(buttonFrame, image = hiddenImage))
        buttons[i].grid(row = int(i/buttonDim[0]), column = i%buttonDim[0])
        buttons[i].isMine = choice(difficulty)


    #calculating the number of mines surrounding each button
    for i in buttons:
        i.mineNumber = [ j.isMine for j in getSurroundingButtons(i) ].count(1)



    #generates a list of all buttons with no surrounding mines aka blank buttons
    blankButtons = [ i for i in buttons if i.mineNumber == 0 ]
    if len(blankButtons) == 0:
        try:
            blankButtons.append( [i for i in buttons if not i.isMine][0] )
        except IndexError:
            buttons[0].isMine = 0
            buttons[0].mineNumber = buttons[0].mineNumber - 1
            blankButtons.append(buttons[0])

    #sorts the blank buttons by the amount of adjacent blank buttons it has
    # sorted default clicks is a list of lists formatted like [number of adjacent blank buttons(including the center one), the actual button object the number corresponds to]
    sortedDefaultClicks = [ [[j.mineNumber for j in getSurroundingButtons(i) ].count(0), i] for i in blankButtons ]
    sortedDefaultClicks = sorted(sortedDefaultClicks, key= lambda x: x[0], reverse=True)

    #auto clicks the button with the highest amount of adjacent blank buttons and if there's a tie just pick the first occuring one
    buttonClicked(sortedDefaultClicks[0][1])


    #set the width and height of the window and the minsize
    buttons[0].update()
    gridwidth = (int(buttons[0].winfo_width()) * int(userButtonDim[0]))
    gridheight = (int(buttons[0].winfo_height()) * int(userButtonDim[1]))
    
    gameScreen.config(width=gridwidth)
    gameScreen.config(height=gridheight)
    gameScreen.update()


    if root.winfo_width() < gridwidth:
        root.geometry(f"{gridwidth}x{root.winfo_height()}")
    
    if root.winfo_height() - topFrame.winfo_height() < gridheight:
        topFrame.update()
        root.geometry(f"{root.winfo_width()}x{gridheight + topFrame.winfo_height()}")

    root.update()

    #   END OF BUTTON GRID CODE   #




    





#################################
#         binding inputs        #
#################################

root.bind('<Button-1>', lambda event: (buttonClicked(event.widget) if (event.widget in buttons) else None))
root.bind('<Button-3>', lambda event: ((event.widget.onRightClick()) if (event.widget in buttons) else None))
root.bind('<Escape>', lambda event: reLoadHomeScreen())



reLoadHomeScreen()

root.minsize(850,450)

root.mainloop()
