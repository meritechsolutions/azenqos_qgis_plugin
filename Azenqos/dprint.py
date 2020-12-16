import os

# touch a file named 'debug' to activate debug dprint()
debug_file_flag = os.path.isfile(
    os.path.join(
        os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        ),
        "debug"
    )
)

#print("dprint: dprint() debug_file_flag: ",debug_file_flag)
def dprint(*s): # https://stackoverflow.com/questions/919680/can-a-variable-number-of-arguments-be-passed-to-a-function
    if debug_file_flag:
        print("dprint: "+str(s))
