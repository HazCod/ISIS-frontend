#!/usr/bin/env python
#
# iwlistparse.py
# Hugo Chargois - 17 jan. 2010 - v.0.1
# Parses the output of iwlist scan into a table

import sys
import subprocess
import re

# You can add or change the functions to parse the properties of each AP (cell)
# below. They take one argument, the bunch of text describing one cell in iwlist
# scan and return a property of that cell.

def get_name(cell):
    return matching_line(cell,"ESSID:")[1:-1]

def get_quality(cell):
    quality = matching_line(cell,"Quality=").split()[0].split('/')
    return str(int(round(float(quality[0]) / float(quality[1]) * 100))).rjust(3) + " %"

def get_channel(cell):
    return matching_line(cell,"Channel:")

def get_encryption(cell):
    enc="?"
    regex = re.compile("\040+IE: (IEEE (.+)/){0,1}WPA(\d)* Version (\d)",re.IGNORECASE|re.MULTILINE)
    if matching_line(cell,"Encryption key:") == "off":
        enc="Open"
    else:
        for line in cell:
            matching = match(line,"IE:")
            if matching!=None:		
            	r = regex.search(line)
           	if r!=None:
			#print(r.groups())
                	eap = r.group(2)
                	wpa = r.group(3)
                	ver = r.group(4)
                	#print('found: ' + eap + wpa + ver)
			enc = 'WPA' + wpa + ' v' + ver
			if eap!=None:
				enc += ' (' + eap + ')'
        if enc=="?":
        	enc="WEP"
    return enc

def get_address(cell):
    return matching_line(cell,"Address: ")

# Here's a dictionary of rules that will be applied to the description of each
# cell. The key will be the name of the column in the table. The value is a
# function defined above.

rules={"name":get_name,
       "quality":get_quality,
       "channel":get_channel,
       "encryption":get_encryption,
       "address":get_address,
       }

# You can choose which columns to display here, and most importantly in what order. Of
# course, they must exist as keys in the dict rules.

columns=["name","address","quality","channel","encryption"]


# Below here goes the boring stuff. You shouldn't have to edit anything below
# this point

def matching_line(lines, keyword):
    """Returns the first matching line in a list of lines. See match()"""
    for line in lines:
        matching=match(line,keyword)
        if matching!=None:
            return matching
    return None

def match(line,keyword):
    """If the first part of line (modulo blanks) matches keyword,
    returns the end of that line. Otherwise returns None"""
    line=line.lstrip()
    length=len(keyword)
    if line[:length] == keyword:
        return line[length:]
    else:
        return None

def parse_cell(cell):
    """Applies the rules to the bunch of text describing a cell and returns the
    corresponding dictionary"""
    parsed_cell={}
    for key in rules:
        rule=rules[key]
        parsed_cell.update({key:rule(cell)})
    return parsed_cell

def print_table(table):
    widths=map(max,map(lambda l:map(len,l),zip(*table))) #functional magic

    justified_table = []
    for line in table:
        justified_line=[]
        for i,el in enumerate(line):
            justified_line.append(el.ljust(widths[i]+2))
        justified_table.append(justified_line)
    
    return(table)

def print_cells(cells):
    table=[columns]
    for cell in cells:
        cell_properties=[]
        for column in columns:
            cell_properties.append(cell[column])
        table.append(cell_properties)
    print_table(table)

def getNetworks():
    #"""Pretty prints the output of iwlist scan into a table"""
    cells=[[]]
    parsed_cells=[]

    for line in subprocess.Popen(["sudo","iwlist", "wlan0", "scan"], stdout=subprocess.PIPE).stdout:
        cell_line = match(line,"Cell ")
        if cell_line != None:
            cells.append([])
            line = cell_line[-27:]
        cells[-1].append(line.rstrip())

    cells=cells[1:]
    #print(cells)

    for cell in cells:
        parsed_cells.append(parse_cell(cell))

    return(parsed_cells)

#main()
