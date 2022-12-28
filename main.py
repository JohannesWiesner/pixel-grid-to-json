import tkinter as tk
from tkinter import messagebox
import json
import os
import re

class App(tk.Tk):
    def __init__(self,savingpath,*args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        ## -- App Settings ------------------------------------------------------------------------------------------------
        
        self.savingpath = savingpath

        self.title("Draw LED")

        # set app to zoomed state
        self.wm_state('normal')

        # Function: Allow esc-button to close main window
        def close(event):
            self.destroy()

        # bind close-function to app
        self.bind('<Escape>', close)

        # set root background color 
        self.configure(bg="white")

        ## -- Canvas Settings ----------------------------------------------------------------------------------------------

        # LED matrix settings
        self.rows = 16  
        self.columns = 24
        self.cellwidth = 20
        self.cellheight = 20
        self.pitch = 3
        self.canvaswidth = self.columns * self.cellwidth
        self.canvasheight = self.rows * self.cellheight

        # create canvas
        self.canvas = tk.Canvas(self, width=self.canvaswidth, height=self.canvasheight,highlightthickness=0, bg='white')
        self.canvas.grid(row=0,column=0,sticky="NSEW")

        # create dictionary for later storage of led objects
        self.oval = {}

        ## -- Functions ----------------------------------------------------------------------------------------------------

        # create list object that stores all coordinates of current active leds
        self.locations = []

        # change led color when clicked
        def changeColor(event):
            
            item = self.canvas.find_closest(event.x, event.y)
            current_color = self.canvas.itemcget(item, 'fill')

            if current_color == 'red':
                self.canvas.itemconfig(item, fill='white')
                self.canvas.dtag('current','active')
            else:
                self.canvas.itemconfig(item, fill='red')
                self.canvas.addtag_withtag('active','current')

        # get coordinates of current clicked led and show them on label
        def identifyLed(event):

            led = self.canvas.find_closest(event.x, event.y)
            current_tags = self.canvas.gettags(led)
            location = current_tags[2]

            self.coord_label.configure(text=location)

        # clear led matrix
        # 1.) change color back to white 
        # 2.) remove 'active'-tag if set
        # 3.) reset locations-list
        def clearMatrix():

            led_idfs = self.canvas.find_withtag('active')

            for idf in led_idfs:
                self.canvas.itemconfig(idf, fill='white')
                self.canvas.dtag(idf,'active')

            self.locations = []

            print(self.locations)

        # load json file and correspondingly change led matrix
        def loadTemplate(selection):

            index = selection[0]
            filename = self.template_list.get(index)

            # get filepath for selected item in list
            for file in os.listdir(self.savingpath):
                if file.startswith(filename):

                    # open file and save coordinates
                    with open(self.savingpath + filename,'r') as fileobject:
                        temp = json.load(fileobject)
                        self.locations = temp[filename]

            # activate all leds corresponding to coordinates (fill = red + add 'active'-tag)
            for coordinates in self.locations:
            
                current_led = self.canvas.find_withtag(coordinates)

                self.canvas.itemconfig(current_led, fill='red')
                self.canvas.addtag_withtag('active',current_led)

            print(self.locations)
        
        # delete selected template
        def delTemplate(selection):

            index = selection[0]
            filename = self.template_list.get(index)
            locations = None

            # get filepath for selected item in list
            for file in os.listdir(self.savingpath):
                if file.startswith(filename):

                    # open file and save coordinates
                    with open(self.savingpath + filename,'r') as file:
                        temp = json.load(file)
                        locations = temp[filename]

            for coordinates in locations:

                current_led = self.canvas.find_withtag(coordinates)

                self.canvas.itemconfig(current_led, fill='white')
                self.canvas.dtag('active',current_led)

            # reset locations
            self.locations = []

            print("Locations:",self.locations)

        def switchLayout(switchvar):

            if switchvar == True:

                all_leds = self.canvas.find_all()

                for idf in all_leds:
                    
                    tags = self.canvas.itemcget(idf,'tags')
                    
                    if not 'active' in tags:
                        self.canvas.itemconfig(idf, state='hidden')

                self.switch.configure(text='Show grid')

            elif switchvar == False:

                all_leds = self.canvas.find_all()

                for idf in all_leds:
                    
                    tags = self.canvas.itemcget(idf,'tags')
                    
                    if not 'active' in tags:
                        self.canvas.itemconfig(idf, state='normal')

                self.switch.configure(text='Remove grid')

        ## -- Toplevel window for saving files  ----------------------------------------------------------------------------------------------------

        # create and open save toplevel window where user can name file he wants to save
        # FIXME: include save-as-txt-file option
        def callSaveBox():

            # variable is manipulated by validateEntry-function and later checked in saveTemplate-fucntion
            # If value is false, user typed in non-valid filename
            gate = None

            twipadx = 10
            twpadx = 10
            twpady = 10 

            # check if filename is valid
            def validateEntry(*args):

                global gate

                # only allow letters, numbers, dashes and underscores as file name
                regexp = re.compile(r"^[A-Za-z0-9_-]*$")
                
                if regexp.search(entry_input.get()):
                    gate = True
                elif not regexp.search(entry_input.get()):
                    gate = False

                print('Here it goes:', gate)

            # save current led matrix coordinates in json file
            def saveTemplate(filename):

                global gate

                led_idfs = self.canvas.find_withtag('active')

                for idf in led_idfs:
                    current_led_tags = self.canvas.gettags(idf)
                    current_led_coords = current_led_tags[2]

                    self.locations.append(current_led_coords)

                if gate == True:
                    
                    # create .json conform dictionary
                    dump_dict = {filename:self.locations}

                    # dump data with given filename
                    with open(self.savingpath + filename, 'w') as file:
                        json.dump(dump_dict,file,indent=2)

                    # insert name of new file to listbox but only if filename does not already exist
                    items = self.template_list.get('0','end')

                    if not filename in items:

                        self.template_list.insert('end',filename)
                    
                    # close toplevel window
                    closeSaveBox()

                    # show info
                    infobox = messagebox.showinfo('Draw LED','Saved file as: {}.json'.format(filename))
                
                elif gate == False:
                    errorbox = messagebox.showerror('Draw LED','Please provide a valid filename',parent=saveBox)
                
                elif gate == None:
                    errorbox = messagebox.showerror('Draw LED','Please provide a valid filename',parent=saveBox)

            def closeSaveBox():
                saveBox.destroy()

            saveBox = tk.Toplevel()

            saveBox_label = tk.Label(saveBox,text='Filename:')
            saveBox_label.grid(row=0,column=0,padx=twpadx,pady=twpady)

            entry_input = tk.StringVar()

            saveBox_entry = tk.Entry(saveBox)
            saveBox_entry.grid(row=0,column=1,columnspan=2,padx=twpadx,pady=twpady)
            saveBox_entry.configure(textvariable=entry_input)

            # bind validateEntry-function to entry_input-variable
            entry_input.trace("w",validateEntry)

            saveBox_ok = tk.Button(saveBox,text='Save')
            saveBox_ok.grid(row=1,column=1,sticky="W",padx=twpadx,pady=twpady,ipadx=twipadx)
            saveBox_ok.configure(command=lambda: saveTemplate(saveBox_entry.get()))

            saveBox_cancel = tk.Button(saveBox,text='Cancel')
            saveBox_cancel.grid(row=1,column=2,sticky="W",padx=twpadx,pady=twpady,ipadx=twipadx)
            saveBox_cancel.configure(command=closeSaveBox)

        ## -- LED-Grid  ----------------------------------------------------------------------------------------------------

        # create leds on canvas
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column*self.cellwidth
                y1 = row * self.cellheight
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.oval[row,column] = self.canvas.create_oval(x1+self.pitch,y1+self.pitch,x2-self.pitch,y2-self.pitch,tags=("clickable","color",[row,column]),fill="white")

        # bind functions to leds
        self.canvas.tag_bind("color","<ButtonPress-1>", changeColor)
        self.canvas.tag_bind("clickable","<ButtonPress-1>",identifyLed)

        ## -- Controll field ----------------------------------------------------------------------------------------------------

        self.pady = 10
        self.padx = 10
        self.width = 20

        self.controll_frame = tk.Frame(relief="sunken",bd=1)
        self.controll_frame.grid(row=0,column=1,sticky="NESW",padx=self.padx)

        self.led_label = tk.Label(self.controll_frame,text="Current selected LED:")
        self.led_label.grid(row=0,column=1,sticky="NW",padx=10,pady=self.pady)

        self.coord_label = tk.Label(self.controll_frame,text="No LEDs selected")
        self.coord_label.grid(row=0,column=3,sticky="NW",padx=10,pady=self.pady)

        self.template_list = tk.Listbox(self.controll_frame)
        self.template_list.grid(row=1,column=1,sticky="W",padx=10,rowspan=5,pady=self.pady)
        
        # load json-files to listbox
        for file in os.listdir(self.savingpath):
            self.template_list.insert('end',file)

        self.template_scrollbar = tk.Scrollbar(self.controll_frame)
        self.template_scrollbar.grid(row=1,column=2,rowspan=5,pady=self.pady,sticky="NS")
        
        # connect listbox and scrollbar
        self.template_scrollbar.config(command=self.template_list.yview)
        self.template_list.config(yscrollcommand=self.template_scrollbar.set)

        self.template_button = tk.Button(self.controll_frame,text="Load template",width=self.width)
        self.template_button.grid(row=1,column=3,sticky="NW",padx=self.padx,pady=self.pady)
        self.template_button.configure(command= lambda: loadTemplate(self.template_list.curselection()))

        self.delete_button = tk.Button(self.controll_frame,text="Clear selected template",width=self.width)
        self.delete_button.grid(row=2,column=3,sticky="NW",padx=self.padx,pady=self.pady)
        self.delete_button.configure(command= lambda: delTemplate(self.template_list.curselection()))

        self.clear_button = tk.Button(self.controll_frame,text="Clear Configuration",width=self.width)
        self.clear_button.grid(row=3,column=3,sticky="NW",padx=self.padx,pady=self.pady)
        self.clear_button.configure(command=clearMatrix)

        self.save_button = tk.Button(self.controll_frame,text="Save Configuration",width=self.width)
        self.save_button.grid(row=4,column=3,sticky="NW",padx=self.padx,pady=self.pady)
        self.save_button.configure(command=callSaveBox)

        self.switch_button = tk.Checkbutton(self.controll_frame,text='Remove grid',width=self.width,indicatoron=0)
        self.switch_button.grid(row=5,column=3,sticky="NW",padx=self.padx,pady=self.pady)
        self.switch_var = tk.BooleanVar()
        self.switch_button.configure(variable=self.switch_var,command=lambda: switchLayout(self.switch_var.get()))

if __name__ == "__main__":

    # Customize: define saving directory here
    savingpath = 'savings/'

    # create folder where json-data is stored
    if not os.path.exists(savingpath):
        os.makedirs(savingpath)

    # start program
    app = App(savingpath=savingpath)
    app.mainloop()
