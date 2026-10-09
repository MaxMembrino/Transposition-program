#Max Membrino computer science project NEA 15/01/25
import cv2, numpy, mido, time, os
from tkinter import *
from tkinter import filedialog, font
from PIL import Image, ImageTk

def removeStave(sheet,UBsheet):
    delete =[]
    lines, space = staveHeight(sheet,UBsheet)
    height, width = sheet.shape[:2]
    
    #iterate along each pixel for each line
    for x in range(0,5):
        for p in range(-4,4): #incase lines lines are thicker than 1 pixel
            h = int(lines[x])
            h = h+p
            for w in range(0, width):
                #print(w,h)
                #print(sheet[h,w, 0])
                if sheet[h,w, 0] ==0:
                    #pixel is on a stave line
                    h1 = h+1 
                    h2 = h-1
                    if sheet[h1,w,0] or sheet[h2,w,0] == 255: #checks for white above/below
                        delete.append((h,w)) #add pixels to be deleted onto an array
    
    for g in range(0,len(delete)): # delete pixels in array
        h = delete[g][0]
        w = delete[g][1]
        sheet[h,w] =[255,255,255]
    
    return sheet, lines, space

def convertToMIDI(notes, lines, space, heights):
    pitches = list()
    for x in range(0,len(lines)): #makes the lines values integers
        lines[x] = int(lines[x])
    print("Convert the pitches to midi format")
    for x in range(0,len(notes)):
        height = heights[x]
        #checks for notes on lines
        if int(lines[0] + space - 3) <= height <= int(lines[0] + space + 3):
            print("C")
            pitch = "60"
        elif lines[0]-3 <= height <= lines[0]+3 :
            print("E")
            pitch = "64"
        elif lines[1]-3 <= height <= lines[1]+3:
            print("G")
            pitch = "67"
        elif lines[2]-3 <= height <= lines[2]+3:
            print("B")
            pitch = "71"
        elif lines[3]-3 <= height <= lines[3]+3:
            print("D")
            pitch = "74"
        elif lines[4]-3 <= height <= lines[4]+3:
            print("F")
            pitch = "77"
        else:
            #checks for notes in between lines
            if height > lines[0]:
                print("D")
                pitch = "62"
            elif height > lines[1]:
                print("F")  
                pitch = "65"
            elif height > lines[2]:
                print("A") 
                pitch = "69"
            elif height > lines[3]:
                print("C")
                pitch = "72"
            elif height > lines[4]:
                print("E")
                pitch = "76"
            else:
                pitch = "79"
                
                
        pitches.append(pitch)
    return pitches

def convert(note):
    #Convert letter notes to MIDI and other way round
    midi = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77,78,79]
    letter = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B","C", "C#", "D", "D#", "E", "F", "F#", "G"]
    try:
        int(note)
        print("MIDI to letter")
        note = letter[midi.index(note)] #converts value in one array to value in other array
    except:
        print("letter to MIDI")
        note = midi[letter.index(note)]
    return note

def transpose(notes,key,lines,space):
    
    heights =list()
    #puts everything into new format so that it can be converted to MIDI
    trnotes=list()
    print("Put the notes into trnotes list")
    notes = sorted(notes)
    print(notes)
    
    for x in range(0,len(notes)):
        if notes[x][2][0] == "up": 
            #notes have to be split as the head is in different places on the different templates
            #note stems going up
            heights.append(int(notes[x][1][1] - 9))
        else:
            #note stems going down
            heights.append(int(notes[x][1][1] - 37))
        #format of each note is (x1,y1),(x2,y2), (pitch, duration)
        
    pitches = convertToMIDI(notes, lines, space, heights)
    print(pitches)
    #transposes MIDI pitches up by amount user has selected with drop down boxes
    for x in range(0,len(notes)):
        pitches[x] = int(pitches[x]) + int(key)
        trnotes.append(((notes[x][0]),(notes[x][1][0],heights[x]), (pitches[x], "duration")))
    
    print(pitches)
    print(trnotes)
    return trnotes

def staveHeight(sheet,UBsheet):
    global lines, space, timesig
    print("Get stave height")
    clef = cv2.imread("assets/trebleclef.png")
    h,w = clef.shape[:2]
    #finds the maximum value for where the treble clef could be
    matches = cv2.matchTemplate(UBsheet,clef,cv2.TM_CCOEFF_NORMED)
    minv, maxv, minl, topLeft = cv2.minMaxLoc(matches)
    bottomRight = (topLeft[0]+w, topLeft[1]+h)
    
    threshold=0.7
    #checks for 4/4
    template=cv2.imread("assets/timesig4.png")
    template = binarise(template)
    matches = cv2.matchTemplate(UBsheet, template, cv2.TM_CCOEFF_NORMED) #template match
    (y,x) = numpy.where(matches >= threshold)
    print(y,x)
    print(y.size)
    if y.size < 1: #temporary values to test program replace with [] []
            
        #repeats for 3/4
        template=cv2.imread("assets/timesig3.png")
        template = binarise(template)
        matches = cv2.matchTemplate(UBsheet, template, cv2.TM_CCOEFF_NORMED) #template match
        (y,x) = numpy.where(matches >= threshold)
        print(y,x)
        timesig=3 #for 3/4
    else:
        print("ABBC")
        timesig=4 #for 4/4
    print(timesig)
    
    

    
    
    #temporary code to show clef detection
    #cv2.rectangle(sheet,topLeft, bottomRight, 255, 2)
    
    
    
    #calculates the height of the stave, and the spaces inbetween each line
    line1 = bottomRight[1]
    
    line5 = topLeft[1]
    height = line1-line5
    space = height / 4
    print(line1, line5, height, space)
    lines=[]
    for x in range(0,5):
        lines.append(line1 - space*x)
        
    """
    #temporary code to verify line height
    for x in range(0,5):
        cv2.rectangle(sheet, (0,int(lines[x])),(170,int(lines[x])), 255,1)
    """
    return lines, space 

def binarise(image): #converts images to only black and white to make reading easier
    (T, image) = cv2.threshold(image, 180, 255, cv2.THRESH_BINARY)
    return image

def readMusic(sheet,notes, template, stem):
    print("Read sheet music")
    threshold = 0.7 #threshold is how close matches have to be to the template
    h,w = template.shape[:2] #get width and height of template
    
    sheet = binarise(sheet)
    template = binarise(template)
    matches = cv2.matchTemplate(sheet, template, cv2.TM_CCOEFF_NORMED) #template match
    (y3,x3) = numpy.where(matches >= threshold) #compares match to threshold
    
    while y3.size !=0: #if there are some notes in the image
    
        matches = cv2.matchTemplate(sheet, template, cv2.TM_CCOEFF_NORMED) #template match
        minv, maxv, btmR, topL = cv2.minMaxLoc(matches) #splits the values into the minimum and maximum matches
        btmR = (topL[0]+w, topL[1]+h) #calculates value for bottom right corner with template shape and top left corner
        cv2.rectangle(sheet, topL, btmR, 0, -1)
        notes.append((topL, btmR, (stem,0)))   
        matches = cv2.matchTemplate(sheet, template, cv2.TM_CCOEFF_NORMED) #template match
        (y3,x3) = numpy.where(matches >= threshold)
    return sheet, notes


def fileopen():
    global win,filepath,box1,img1display, y, toolTip
    #gives the user the option to open a file from their device
    filepath = filedialog.askopenfilename(title="Select a file to transpose")
    
    img1 = Image.open(filepath) #opens image selected by the user
    img1 = ImageTk.PhotoImage(img1)   
    img1display = Label(box1,image=img1)
    
    img1display.image = img1
    img1display.pack(expand=True) #places image inside the canvas
    toolTip.config(text="Use next page button to go to enter keys and transpose. Use re-upload to select a new piece of music")
    print(filepath)
    if y == False:#only triggers once to avoid repeat buttons stacking
        nextpageB = Button(command=lambda:[forget(nextpageB),forget(reuploadB),transposePage()],text="Next page",bg="green",font=font1)
        nextpageB.grid(row=2,column=3,rowspan=2,columnspan=5,sticky="news",padx=15,pady=15)
        y = True
        
        reuploadB = Button(command=lambda:[reUpload(reuploadB)],text="Re-upload",bg="green",font=font1)
        reuploadB.grid(row=4,column=3,rowspan=2,columnspan=5,sticky="news",padx=15,pady=15)
    toolTip.lift()

def reUpload(reuploadB): #gives the user an option to select a different image
    img1display.destroy() #deletes the first uploaded image
    fileopen()
    
def keyEntered(keyEnter, transposeB):
    global c
    if keyEnter.cget("bg") =="red": 
        c+=1
    keyEnter.config(bg="green") #turns dropdown box green once a key is entered into it
    if c == 2:
        arrowG = ImageTk.PhotoImage(Image.open("assets/arrowG.png")) #turns transpose button green once both keys entered
        transposeB.config(image=arrowG)
        arrowG.image = arrowG 


def transposeBclicked():
    global warnC, warn,c1,initialKey,newKey, keyEnter1, keyEnter2, transposeB
    global lines, space, keyLabel1, keyLabel2, trnotes
    print("transpose button clicked")
    if c!=2 and c1==0: #if transpose button is pressed before keys are entered
        warn = Label(text="Enter keys first and then click transpose", fg="red",font=font1)
        warn.grid(row=2,column=4,columnspan=3) 
        warnC=1
        c1=1
    elif c==2: #only trigger warning once
        if warnC != 0:
            forget(warn)
        
        #get entered keys from dropdown boxes
        key1 = initialKey.get()
        key2 = newKey.get()
        key1 = convert(key1)
        key2 = convert(key2)
        print(key1,key2)
        key3 = abs(key1-key2)
        print(key3)
        
        sheet = cv2.imread(filepath)
        UBsheet=cv2.imread(filepath)#unbinarised sheet
        template1 = cv2.imread("assets/template1.png")
        template2 = cv2.imread("assets/template2.png")

        sheet = binarise(sheet)
        template1 = binarise(template1)
        template2 = binarise(template2)

        notes = list()
        sheet, lines, space = removeStave(sheet,UBsheet)
        stem = "up" #notes with stems going up
        sheet, notes = readMusic(sheet,notes, template1,stem) #stem is going down for template 1
        stem = "down" #notes with stems going down
        sheet, notes = readMusic(sheet,notes, template2,stem) #stem is going up for template 2
        print("A")
        trnotes = transpose(notes,key3,lines,space)
        print("ABC")
        
        createSheetMusic(trnotes)#creates final sheet music
        #deletes all widgets so they are not still visible on final page
        widgets = [transposeB,keyEnter1,keyEnter2,keyLabel2,keyLabel1]
        for x in range(0,5):
            forget(widgets[x])

    
def createSheetMusic(trnotes):
    global timesig
    count = 0 
    print("Use the notes array")
    print(trnotes) # pitch is stored at[x][2][0]
    
    #C also needs to be made into its own image
    pitches = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79]
    heights = ['33', '33', '28', '28', '24', '21', '21', '17', '17', '12', '12', '31', '27', '27', '23', '23', '18', '13', '13', '10']
    #templates for template matching (must be RGBA format)
    blanksheet = Image.open("assets/blanksheet.png").convert("RGBA")
    noteupnat = Image.open("assets/transparentnoteup.png").convert("RGBA")
    notedownnat = Image.open("assets/transparentnotedown.png").convert("RGBA")
    noteupsharp = Image.open("assets/transparentnoteupsharp.png").convert("RGBA")
    notedownsharp = Image.open("assets/transparentnotedownsharp.png")
    notec = Image.open("assets/transparentnotec.png").convert("RGBA")
    barline = Image.open("assets/barline.png").convert("RGBA")
    #3/4 or 4/4 time signature depending on input from user sheet music
    timesigimg = Image.open("assets/timesig"+str(timesig)+".png").convert("RGBA")
    timesigshape = cv2.imread("assets/timesig"+str(timesig)+".png")
    h5, w5, c5 = timesigshape.shape
    h5, w5 = int(h5) * 0.8, int(w5)*0.8
    h5, w5 = int(h5), int(w5)
    timesigimg = timesigimg.resize((w5, h5))
    
    
    #adds time signature to sheet music
    blanksheet.paste(timesigimg,(50, 25))
    
    for x in range (0,len(trnotes)):
        
        pitch = trnotes[x][2][0]
        height = heights[pitches.index(pitch)]
        print(height)
        
        #if the note is sharp it has a different template
        if pitch in [61, 63, 66, 68, 70, 73, 75, 78]: 
            noteup = noteupsharp
            height = int(height) -1
            notedown = notedownsharp
        else: #if note is natural it has the normal template
            noteup = noteupnat
            notedown = notedownnat

        xcoord = int(x*30 +62) #decides the spacing between notes
        
        if int(pitch) > 70:
            blanksheet.paste(notedown, (xcoord,int(height)), notedown)
        else:
            if height == "33": #middle C has a different template
                blanksheet.paste(notec, (xcoord,int(height)), notec)
            else:
                blanksheet.paste(noteup, (xcoord,int(height)), noteup)
        count+=1
        #add a barline every 3 or 4 notes depending on the time signature
        if count == int(timesig):
            print("Add barline", timesig) 
            blanksheet.paste(barline,((xcoord + 22),22),barline)
            count = 0 #resets count to zero so that the next barline is placed after the next set of 3 or 4 notes
    
    toolTip.config(text="You can view your sheet music on the right. Use the restart button at the top to transpose a new piece of music.")
    
    transposedsheet = ImageTk.PhotoImage(blanksheet)
    img2display = Label(box2,image=transposedsheet)
    a=0
    img2display.image = transposedsheet
    img2display.pack(expand=True) #places image inside the canvas
    restartB = Button(win,text="Restart",bg="green",font=font1, command=lambda:restart())
    restartB.grid(row=1,column=3,columnspan=5,rowspan=3,sticky="ewsn")
    playMusicB = Button(win,text="Play music",bg="green",font=font1, command=lambda:play())
    playMusicB.grid(row=4,pady=5,column=3,columnspan=5,rowspan=2,sticky="ewsn")


def play(): #play the transposed music out loud
    global trnotes
    output_port = mido.open_output()
    for x in range (0,len(trnotes)):
        midiCode = trnotes[x][2][0]
        msg_on = mido.Message('note_on', note=midiCode, velocity=64)
        output_port.send(msg_on)
        time.sleep(0.5) #duration of note to play
        msg_off = mido.Message('note_off', note=midiCode, velocity=64)
        output_port.send(msg_off)
    output_port.close()

    
    
    
    

def restart(): #initialises all variables, destroy window, open new window
    global c,warnC, c
    print("restart")
    c=0
    c1=0
    warnC=0
    notes = list()
    win.destroy()
    createWindow()
    

def transposePage():   
    global title, keyEnter1, initialKey, font1, newKey, keyEnter2, transposeB, keyLabel1, keyLabel2, toolTip
    print("Transpose page")
    toolTip.config(text="Click the red buttons above to select the keys to transpose between. When they are both green, press the green transpose button above to transpose the music.")
    title.config(text="Tranpose a piece of music")
    arrowR = ImageTk.PhotoImage(Image.open(r"assets/arrowR.jpg"))
    transposeB = Button(win, image=arrowR, command=transposeBclicked)
    transposeB.grid(column=4, row=1, columnspan=3, rowspan=2, sticky="news")
    transposeB.image = arrowR
    initialKey = StringVar()
    initialKey.set("Add a key")
    newKey = StringVar()
    newKey.set("Add a key")
    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    keyEnter1 = OptionMenu(win, initialKey, *keys, command=lambda x: keyEntered(keyEnter1, transposeB))
    keyEnter1.grid(column=6, row=4, sticky="news")
    keyEnter2 = OptionMenu(win, newKey, *keys, command=lambda x: keyEntered(keyEnter2, transposeB))
    keyEnter2.grid(column=6, row=6, sticky="news")
    keyEnter1.config(font=font1, bg="red")
    keyEnter2.config(font=font1, bg="red")
    keyLabel1 = Label(font=font1, text="Initial key:", bg="blue")
    keyLabel2 = Label(font=font1, text="New key:", bg="blue")
    keyLabel1.grid(column=4, row=4, sticky="news", columnspan=2, padx=15)
    keyLabel2.grid(column=4, row=6, sticky="news", columnspan=2, padx=15)
    
    toolTip.lift()
    
def forget(widget): #to delete widgets
#    widget.grid_forget()
    widget.destroy()   
    
def changeFont(size):
    global font1
    print(size)
    font1=font.Font(family="arial",size=size)  #changes font as slider changes
    
    for widget in win.winfo_children(): #applies changes to widgets with the same font
        widget.config(font=font1)
    
    
    
    
def toggleTT(widget):
    global toggle, toolTip
    if toggle == 0: #tool tips on
        widget.config(bg="green",text="Enabled")
        toggle=1
        toolTip.grid_propagate(False)
        toolTip.grid(row=7,column=3,columnspan=5,padx=5,pady=5,rowspan=3,sticky="ewsn")
        
        
    elif toggle ==1: #tool tips off
        widget.config(bg="red",text="Disabled")
        toggle = 0
        toolTip.grid_forget()
    
    
    
def initSettings():
    global settingsPage, fontControl, themeColour, ttToggle, font1
    settingsPage = Frame(win, borderwidth=5, relief="solid", bg="orange")
    settingsPage.columnconfigure((0, 1), weight=1, uniform='column1')
    settingsPage.rowconfigure(tuple(range(10)), weight=1, uniform='row1')
    settingsTitle = Label(settingsPage, font=font1, text="Settings", bg="blue")
    settingsTitle.grid(column=0, row=0, columnspan=2, sticky="ew")
    theme = StringVar(value="Light blue")
    themes = ["Light blue", "Red", "Green", "Orange", "Yellow", "Blue", "Purple", "Pink", "Black"]
    themeColour = OptionMenu(settingsPage, theme, *themes, command=lambda x: [win.config(bg=theme.get()), themeColour.config(bg=theme.get()), fontControl.config(bg=theme.get())])
    themeColour.config(font=font1, bg="light blue")
    themeColour.grid(column=1, padx=5, pady=5, row=2, columnspan=2, sticky="news")
    option1 = Label(settingsPage, text="Theme colour", font=font1, bg="green")
    option1.grid(column=0, row=2, padx=5, pady=5, sticky="news")
    fontControl = Scale(settingsPage, from_=15, to=50, orient="horizontal", bg=theme.get(), command=changeFont)
    fontControl.grid(column=1, padx=5, pady=5, row=3, columnspan=2, sticky="news")
    option2 = Label(settingsPage, text="Font size", font=font1, bg="green")
    option2.grid(column=0, row=3, padx=5, pady=5, sticky="news")
    option3 = Label(settingsPage, text="Tooltips", font=font1, bg="green")
    option3.grid(column=0, row=4, padx=5, pady=5, sticky="news")
    ttToggle = Button(settingsPage, bg="red", text="Disabled", font=font1, command=lambda: [toggleTT(ttToggle)])
    ttToggle.grid(column=1, row=4, padx=5, pady=5, sticky="news")
    settingsExit = Button(settingsPage, text="Close settings", font=font1, bg="green", command=closeSettings)
    settingsExit.grid(row=6, column=0, columnspan=2, pady=15)

def openSettings():
    settingsB.grid_remove()  # hides the button temporarily without losing its grid settings
    settingsPage.place(relx=0.5, rely=0.5, relwidth=0.7, relheight=0.75, anchor="center")
    settingsPage.lift()      # ensures it sits on top of all widgets on any screen

def closeSettings():
    settingsPage.place_forget()
    settingsB.grid()         # restores the button to its exact previous grid position
    
    

def createWindow():
    global win, box1, box2, title, uploadB, y, settingsCount, font1, toolTip, toggle, settingsPage, settingsB
    win = Tk()
    toggle = 0
    font1 = font.Font(family="arial", size=25)
    y = False
    settingsCount = 0
    win.columnconfigure((0,1,2,3,4,5,6,7,8,9,10), weight=1, uniform='column')
    win.rowconfigure((0,1,2,3,4,5,6,7,8,9,10), weight=1, uniform='row')
    win.config(bg="light blue")
    win.title("Music transposition program")
    win.state("zoomed")
    title = Label(win, text="Upload a piece of music", bg="blue", fg="white", font=font1)
    title.grid(row=0, column=0, columnspan=12, sticky="news", padx=30)
    uploadB = Button(win, text="Upload", bg="green", font=font1, command=lambda: [fileopen(), forget(uploadB)])
    uploadB.grid(row=1, column=3, columnspan=5, rowspan=3, sticky="ewsn")
    box1 = Canvas(win, bg="grey")
    box1.grid(row=2, column=0, rowspan=9, columnspan=3, sticky="ewsn", padx=10, pady=5)
    box2 = Canvas(win, bg="grey")
    box2.grid(row=2, column=8, rowspan=9, columnspan=3, sticky="ewsn", padx=10, pady=5)
    
    settingsB = Button(win, text="Settings", bg="orange", font=font1, command=openSettings)
    settingsB.grid(column=4, row=10, columnspan=3, rowspan=1, sticky="news")
    toolTip = Label(win, text="Click the button above to select a piece of music to upload from your device", wraplength=350, font=font1, bg="light green")
    initSettings()
    
    win.mainloop()
    


global c,warnC
#initialises variables
c=0
c1=0
warnC=0
notes = list()

createWindow()

