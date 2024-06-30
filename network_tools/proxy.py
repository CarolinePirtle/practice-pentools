import sys
import socket
import threading

#Contains ASCII characters if they exisit, . otherwise
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

#Takes some input as bytes or a string and prints a hexdump to the console
def hexdump(serc, length = 16, show = True):
    #Checks if we have a string
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
       #Grab part of a string
        word = str(src[i:i+length])
        #Use the built in translae function to subistute the string rep for the byte vals
        printable = word.translate(HEX_FILTER)
        #Same as above, but with hex representation
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        #Create a new array to hold teh strings, result
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results