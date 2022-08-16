from getpass import getpass

"""Creates a config file in the same directory. Creates file if it doesn't exist. Allows user to set 5 different values each stored on a specific line in the file.
The number entered to select a value corresponds to the line in the file that value is stored on. Line 0 is reserved for the 'last' variable used by the client
(last pull from server), which is not alterable by the user here and is empty by default."""

while True:
    print("Enter a numeric character to configure its associated setting:")
    print("1 - regular FTP pull interval")
    print("2 - server hostname")
    print("3 - server port")
    print("4 - server username")
    print("5 - server password")
    print("(6 - exit program)\n")

    #validate input
    try:
        op = int(input(""))
    except ValueError:
        print("Invalid input.\n")
        continue
    if not (1<=op and op<=6):
        print("Invalid input.\n")
        continue

    #record config file in current state
    with open("config.txt", 'a+') as file:
        file.seek(0)
        lines = file.readlines()
        linesNo = len(lines)
        #if latter fields are blank, add newlines to avoid index error
        if (linesNo<6):
            for i in range (5-linesNo):
                lines.append('\n')
            lines.append('')

    #(exit program)
    if (op == 6):
        break

    var=''
    if (op == 1):
        var = input("Enter new interval (in seconds), or press enter to cancel: ")
    if (op == 2):
        var = input("Enter new server host, or press enter to cancel: ")
    if (op == 3):
        var = input("Enter new server port, or press enter to cancel: ")
    if (op == 4):
        var = input("Enter new username, or press enter to cancel: ")

    #op corresponds to line of file to be changed  
    lines[op] = (var + '\n')     
    
    if (op == 5):
        #getpass doesn't work in idle, but would hide the user's input on the terminal
        var = getpass("Enter new password, or press enter to cancel: ")
        lines[op] = (var)

    #if enter key was pressed, cancel
    if (var == ''):
        print("File write cancelled.\n")
        continue

    #write to file with user's alteration
    with open('config.txt', 'w+') as file:
        for line in lines:
            file.write(line)

    print('')
