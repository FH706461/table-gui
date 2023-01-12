# https://www.w3schools.com/sql/sql_autoincrement.asp
# GUI Table Base: https://www.youtube.com/watch?v=ETHtvd-_FJg
# Need to fix: Search needs overhaul
# Need to fix: Add can put in blanks?


import PySimpleGUI as sg
import sqlite3

# SQL stuff
sqliteConnection = sqlite3.connect('musicList.db')
cursor = sqliteConnection.cursor()

cursor.execute('''select count(name)
                  from sqlite_master
                  where type = 'table'
                  and name = 'SongList';''')

# Updates table
def GetSongInfo():
  sqlite_select_query = """SELECT * from SongList"""
  
  cursor.execute(sqlite_select_query)
  global records
  records = cursor.fetchall()

# Creates database if it doesn't exist
if not cursor.fetchone()[0]==1:
  sqlite_create_table_query = '''CREATE TABLE SongList (
                             identity TEXT PRIMARY KEY,
                             songName TEXT NOT NULL,
                             artist TEXT NOT NULL,
                             length TEXT NOT NULL);'''
  
  cursor.execute(sqlite_create_table_query)
  sqliteConnection.commit()
  print("SQLite table created")
  
  sqlite_insert_query = """REPLACE INTO SongList
                       (identity, songName, artist, length)
                       VALUES (?, ?, ?, ?);"""
  
  recordsToInsert = [('000001', 'Six Shooter', 'Coyote Kisses', '3:38'),
                    ('000002', 'Lone Digger', 'Caravan Palace', '3:51'),
                    ('000003','Delta','C2C','3:44'),
                    ('000004', 'Rock It For Me', 'Caravan Palace', '3:11')]
  
  cursor.executemany(sqlite_insert_query, recordsToInsert)
  sqliteConnection.commit()

GetSongInfo()

# Add Song Code
def AddSong():
  # The stuff inside the window. sg.Text() is basically the gui version of print()
  addLayout = [
    
    # Layout of Add Song Window
    [sg.Text("Please enter a valid ID.")],
    [sg.InputText(key = 'inputAddID')],
    [sg.Text("Please enter the song name.")],
    [sg.InputText(key = 'inputSongName')],
    [sg.Text("Please enter the artist.")],
    [sg.InputText(key = 'inputArtist')],
    [sg.Text("Please enter the length of the song.")],
    [sg.InputText(key = 'inputTimeLength')],
    [sg.Text("", key = 'state')],

    # Continue and close buttons
    [sg.Button('Continue'), sg.Button('Quit')]
          ]
  
    # Creates the window
  window = sg.Window('  Add Song', addLayout)

  # Event Loop to process "events" and get the "values" of the inputs
  while True:

    event, values = window.read()

    # Defining info given
    addID = values['inputAddID']
    addSongName = values['inputSongName']
    addArtist = values['inputArtist']
    addTimeLength = values['inputTimeLength']

    # Error checking triggers
    existID = False
    blankInput = False
    
    # For when the user closes the window or clicks cancel
    if event == sg.WIN_CLOSED or event == 'Quit':
      break  

    # Finds whether ID is unique
    for i in range(len(records)):
      if addID == records[i][0]:
        window["state"].update("Song ID already in use.")
        existID = True
        break
    if existID:
      continue

    # Finds if input is blank. Technically works?
    if addID.strip() == '' or addSongName.strip() == '' or addArtist.strip() == '' or addTimeLength.strip() == '':
      window["state"].update("No Input")
      blankInput = True
      break
    if blankInput:
      continue

    # SQL input stuff
    sqlite_insert_query = """insert INTO SongList
                           (identity, songName, artist, length)
                           VALUES (?, ?, ?, ?);"""
    recordsToInsert = [(addID, addSongName, addArtist, addTimeLength)]      
    cursor.executemany(sqlite_insert_query, recordsToInsert)
    sqliteConnection.commit()
    break

  window.close()

# Delete Command
def DelSong():
  # Delete window layout
  delLayout = [
    
    # Input for deletion
    [sg.Text("Please enter an ID to delete a song.")],
    [sg.InputText("", key = 'inputDelID')],
    [sg.Text("", key = 'state')],
      
    # Continue and close buttons
    [sg.Button('Continue'), sg.Button('Quit')]
          ]

  window = sg.Window('  Delete Song', delLayout)

  while True:

    event, values = window.read()

    delID = values['inputDelID']
    
    # For when the user closes the window or clicks cancel
    if event == sg.WIN_CLOSED or event == 'Quit':
      break

    sqlite_delete_query = "delete from SongList where identity = '" + str(delID) +"';"
    cursor.execute(sqlite_delete_query)
    sqliteConnection.commit()

    # Error checking
    if int(cursor.rowcount) > 0:
      window["state"].update("No songs found. Try again. (" + str(cursor.rowcount) + " rows successfully deleted).")
    else:
      window["state"].update("Input invalid. Try again.")
      
    break
    
  window.close()
  

# Currently being redone
def SearchSong():
  # Layout of Search window
  findLayout = [

    [sg.Text("Search for:")],
    [sg.Radio('Song Name', "RADIO1"), sg.Radio('Artist', "RADIO1")],

    [sg.InputText("", key = 'inputSearch')],
   
    # Continue and close buttons
    [sg.Button('Continue'), sg.Button('Quit')]
          ]

  window = sg.Window('  Find Song', findLayout)

  while True:

    event, values = window.read()

    find = values['inputFind']

    # For when the user closes the window or clicks cancel
    if event == sg.WIN_CLOSED or event == 'Quit':
      break
    
    contain = False
  
    # Checks row in table
    for song in records:
      # Checks column in row
      for info in song:
        # if input is present, prints all possible students
        if find.lower() in info.lower():
          window["state"].update(", ".join(song))
          contain = True
          break
  
    # If input doesn't exist in table
    if not contain:
      window["state"].update("Song does not exist.")

    break

  window.close()
  
# Defines heading and converts records into data
def MakeTableData():
    headings = ['ID', 'Song Name', 'Artist', 'Time']
    data = records

    return headings, data

# TKinter function to display and edit value in cell. Currently Unused
def EditCell(window, key, row, col, justify='left'):

    global textvariable, edit

    def Callback(event, row, col, text, key):
        global edit
        # event.widget gives you the same entry widget we created earlier
        widget = event.widget
        if key == 'Focus_Out':
            # Get new text that has been typed into widget
            text = widget.get()
            # Print to terminal
            print(text)
        # Destroy the entry widget
        widget.destroy()
        # Destroy all widgets
        widget.master.destroy()
        # Get the row from the table that was edited
        # table variable exists here because it was called before the Callback
        values = list(table.item(row, 'values'))
        # Store new value in the appropriate row and column
        values[col] = text
        table.item(row, values=values)
        edit = False

    if edit or row <= 0:
        return

    edit = True
    # Get the Tkinter functionality for our window
    root = window.TKroot
    # Gets the Widget object from the PySimpleGUI table - a PySimpleGUI table is really
    # what's called a TreeView widget in TKinter
    table = window[key].Widget
    # Get the row as a dict using .item function and get individual value using [col]
    # Get currently selected value
    text = table.item(row, "values")[col]
    # Return x and y position of cell as well as width and height (in TreeView widget)
    x, y, width, height = table.bbox(row, col)

    # Create a new container that acts as container for the editable text input widget
    frame = sg.tk.Frame(root)
    # put frame in same location as selected cell
    frame.place(x=x, y=y, anchor="nw", width=width, height=height)

    # textvariable represents a text value
    textvariable = sg.tk.StringVar()
    textvariable.set(text)
    # Used to accept single line text input from user - editable text input
    # frame is the parent window, textvariable is the initial value, justify is the position
    entry = sg.tk.Entry(frame, textvariable=textvariable, justify=justify)
    # Organizes widgets into blocks before putting them into the parent
    entry.pack()
    # selects all text in the entry input widget
    entry.select_range(0, sg.tk.END)
    # Puts cursor at end of input text
    entry.icursor(sg.tk.END)
    # Forces focus on the entry widget (actually when the user clicks because this initiates all this Tkinter stuff, e
    # ending with a focus on what has been created)
    entry.focus_force()
    # When you click outside of the selected widget, everything is returned back to normal
    # lambda e generates an empty function, which is turned into an event function 
    # which corresponds to the "FocusOut" (clicking outside of the cell) event
    entry.bind("<FocusOut>", lambda e, r=row, c=col, t=text, k='Focus_Out':Callback(e, r, c, t, k))

# Main Window
def MakeTable():
    global edit

    edit = False

    # Defines heading and info shown
    headings, data = MakeTableData()
    sg.set_options(dpi_awareness=True)

    # Layout of main window
    layout = [[sg.Text("Start a command below. Currently Search doesn't work")],
              
              # Command radio buttons.
              [
                sg.Radio('Add Song', "RADIO1", default=True),
                sg.Radio('Delete Song', "RADIO1"),
                sg.Radio('Search', "RADIO1"),
              ],
                 
              # Continue and close buttons
              [sg.Button('Continue'), sg.Button('Quit')],

      # Table Settings
      [sg.Table(values=data, headings=headings, max_col_width=50,
                        font=("Arial", 15),
                        auto_size_columns=True,
                        # display_row_numbers=True,
                        justification='right',
                        num_rows=20,
                        alternating_row_color=sg.theme_button_color()[1],
                        key='-TABLE-',
                        # selected_row_colors='red on yellow',
                        # enable_events=True,
                        select_mode=sg.TABLE_SELECT_MODE_NONE,
                        expand_x=True,
                        expand_y=True,
                        enable_click_events=False,  # Comment out to not enable header and other clicks
                        )],


              # [sg.Text('Cell clicked:'), sg.T(key='-CLICKED_CELL-')]
             ]


    window = sg.Window('  Song List', layout, resizable=True, finalize=True)

    while True:
        # Updates the table for new info added
        GetSongInfo()
        heading, data = MakeTableData()
        window['-TABLE-'].update(data)
    
        # print()
        event, values = window.read()

        # Closes program
        if event in (sg.WIN_CLOSED, 'Quit'):
            break
            window.close()
        
        # Checks if the event object is of tuple data type, indicating a click on a cell. Currently Unused
        elif isinstance(event, tuple):
            if isinstance(event[2][0], int) and event[2][0] > -1:
                cell = row, col = event[2]
                print(row)

            # Displays that coordinates of the cell that was clicked on. Currently Unused
            window['-CLICKED_CELL-'].update(cell)
            EditCell(window, '-TABLE-', row+1, col, justify='right')

        # Commands
        if values[0]:
          AddSong()
        elif values[1]:
          DelSong()
        elif values[2]:
          SearchSong()



MakeTable()
