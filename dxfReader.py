"""This module provides a function for reading dxf files and parsing them into a useful tree of objects and data.

	The convert function is called by the readDXF fuction to convert dxf strings into the correct data based
	on their type code.  readDXF expects a (full path) file name as input.
"""

# --------------------------------------------------------------------------
# DXF Reader v0.9 by Ed Blake (AKA Kitsu)
#  2008.05.08 modif.def convert() by Remigiusz Fiedler (AKA migius)
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------


import sys
import re
from dxfImportObjects import *

class Object:
	"""Empty container class for dxf objects"""

	def __init__(self, _type='', block=False):
		"""_type expects a string value."""
		self.type = _type
		self.name = ''
		self.data = []

	def __str__(self):
		if self.name:
			return self.name
		else:
			return self.type

	def __repr__(self):
		return str(self.data)

	def get_type(self, kind=''):
		"""Despite the name, this method actually returns all objects of type 'kind' from self.data."""
		if type:
			objects = []
			for item in self.data:
				if type(item) != list and item.type == kind:
					# we want this type of object
					objects.append(item)
				elif type(item) == list and item[0] == kind:
					# we want this type of data
					objects.append(item[1])
			return objects


class InitializationError(Exception): pass

class StateMachine:
	"""(finite) State Machine based on one from the great David Mertz's great Charming Python article."""

	def __init__(self):
		self.handlers = []
		self.startState = None
		self.endStates = []

	def add_state(self, handler, end_state=0):
		"""All states and handlers are functions which return
		a state and a cargo."""
		self.handlers.append(handler)
		if end_state:
			self.endStates.append(handler)
	def set_start(self, handler):
		"""Sets the starting handler function."""
		self.startState = handler


	def run(self, cargo=None):
		if not self.startState:
			raise InitializationError(
				"must call .set_start() before .run()")
		if not self.endStates:
			raise InitializationError(
				"at least one state must be an end_state")
		handler = self.startState
		while 1:
			(newState, cargo) = handler(*cargo)
			#print cargo
			if newState in self.endStates:
				return newState(*cargo)
				#break
			elif newState not in self.handlers:
				raise RuntimeError("Invalid target %s" % newState)
			else:
				handler = newState

def get_name(data):
	"""Get the name of an object from its object data.

	Returns a pair of (data_item, name) where data_item is the list entry where the name was found
	(the data_item can be used to remove the entry from the object data).  Be sure to check
	name not None before using the returned values!
	"""
	item, value = None, None
	for item in data:
		if item[0] == 2:
			value = item[1]
			break
	return item, value

def get_layer(data):
	"""Expects object data as input.

	Returns (entry, layer_name) where entry is the data item that provided the layer name.
	"""
	item, value = None, None
	for item in data:
		if item[0] == 8:
			value = item[1]
			break
	return item, value


def convert(code, value):
	"""Convert a string to the correct Python type based on its dxf code.
	code types:
		ints = 60-79, 170-179, 270-289, 370-389, 400-409, 1060-1070
		longs = 90-99, 420-429, 440-459, 1071
		floats = 10-39, 40-59, 110-139, 140-149, 210-239, 460-469, 1010-1059
		hex = 105, 310-379, 390-399
		strings = 0-9, 100, 102, 300-309, 410-419, 430-439, 470-479, 999, 1000-1009
	"""
	import sys
	if 59 < code < 80 or 169 < code < 180 or 269 < code < 290 or 369 < code < 390 or 399 < code < 410 or 1059 < code < 1071:
		value = int(float(value))
	elif 89 < code < 100 or 419 < code < 430 or 439 < code < 460 or code == 1071:
		value = int(float(value))
	elif 9 < code < 60 or 109 < code < 150 or 209 < code < 240 or 459 < code < 470 or 1009 < code < 1060:
		value = float(value)
	elif code == 105 or 309 < code < 380 or 389 < code < 400:
		try:
			value = int(value, 16) # should be left as string?
		except:
			pass
	else: # it's already a string so do nothing
		pass
	return value


def findObject(infile, kind=''):
	"""Finds the next occurance of an object."""
	obj = False
	while 1:
		line = infile.readline()
		if not line: # readline returns '' at eof
			return False
		if not obj: # We're still looking for our object code
			if line.lower().strip() == '0':
				obj = True # found it
		else: # we are in an object definition
			if kind: # if we're looking for a particular kind
				if line.lower().strip() == kind:
					obj = Object(line.lower().strip())
					break
			else: # otherwise take anything non-numeric
				if line.lower().strip() not in string.digits:
					obj = Object(line.lower().strip())
					break
			obj = False # whether we found one or not it's time to start over
	return obj

def handleObject(infile):
	"""Add data to an object until end of object is found."""
	line = infile.readline()
	if line.lower().strip() == 'section':
		return 'section' # this would be a problem
	elif line.lower().strip() == 'endsec':
		return 'endsec' # this means we are done with a section
	else: # add data to the object until we find a new object
		obj = Object(line.lower().strip())
		obj.name = obj.type
		done = False
		data = []
		while not done:
			line = infile.readline()
			if not data:
				if line.lower().strip() == '0':
					#we've found an object, time to return
					return obj
				else:
					# first part is always an int
					data.append(int(line.lower().strip()))
			else:
				data.append(convert(data[0], line.strip()))
				obj.data.append(data)
				data = []

def handleTable(table, infile):
	"""Special handler for dealing with nested table objects."""
	item, name = get_name(table.data)
	if name: # We should always find a name
		table.data.remove(item)
		table.name = name.lower()
	# This next bit is from handleObject
	# handleObject should be generalized to work with any section like object
	while 1:
		obj = handleObject(infile)
		if obj.type == 'table':
			print("Warning: previous table not closed!")
			return table
		elif obj.type == 'endtab':
			return table # this means we are done with the table
		else: # add objects to the table until one of the above is found
			table.data.append(obj)




def handleBlock(block, infile):
	"""Special handler for dealing with nested table objects."""
	item, name = get_name(block.data)
	if name: # We should always find a name
		# block.data.remove(item)
		block.name = name
	# This next bit is from handleObject
	# handleObject should be generalized to work with any section like object
	while 1:
		obj = handleObject(infile)
		if obj.type == 'block':
			print("Warning: previous block not closed!")
			return block
		elif obj.type == 'endblk':
			return block # this means we are done with the table
		else: # add objects to the table until one of the above is found
			block.data.append(obj)




"""These are the states/functions used in the State Machine.
states:
 start - find first section
 start_section - add data, find first object
   object - add obj-data, watch for next obj (called directly by start_section)
 end_section - look for next section or eof
 end - return results
"""

def start(infile, acadVersion):
	"""Initializes the drawing."""
	#print "Entering start state!"
	drawing = Object('drawing')
	section = findObject(infile, 'section')
	if section:
		return start_section, (infile, drawing, section, acadVersion)
	else:
		return error, (infile, "Failed to find any sections!")

def start_section(infile, drawing, section, acadVersion):
	"""Builds a nested section object."""
	#print "Entering start_section state!"
	# read each line, if it is an object declaration go to object mode
	# otherwise create a [index, data] pair and add it to the sections data.
	done = False
	data = []
	while not done:
		line = infile.readline()

		if not data: # if we haven't found a dxf code yet
			if line.lower().strip() == '0':
				# we've found an object
				while 1: # no way out unless we find an end section or a new section
					obj = handleObject(infile)
					if obj == 'section': # shouldn't happen
						print("Warning: failed to close previous section!")
						return end_section, (infile, drawing, acadVersion)
					elif obj == 'endsec': # This section is over, look for the next
						drawing.data.append(section)
						return end_section, (infile, drawing, acadVersion)
					elif obj.type == 'table': # tables are collections of data
						obj = handleTable(obj, infile) # we need to find all there contents
						section.data.append(obj) # before moving on
					elif obj.type == 'block': # the same is true of blocks
						obj = handleBlock(obj, infile) # we need to find all there contents
						section.data.append(obj) # before moving on
					else: # found another sub-object
						section.data.append(obj)
			else:
				data.append(int(line.lower().strip()))
		else: # we have our code, now we just need to convert the data and add it to our list.
			data.append(convert(data[0], line.strip()))
			section.data.append(data)
			data = []
def end_section(infile, drawing, acadVersion):
	"""Verifies if we have version info, searches for next section."""
	#print("Entering end_section state!")
	#if acadVersion:  # DEBUG (pde)
	#	print("Got $ACADVER: " + acadVersion)
	if not acadVersion:
		acadVersion='AC1021' # a sane pre-initialization for DXF files missing $ACADVER (pde)
		headerSection = drawing.data[0]
		if get_name(headerSection.data)[1] != 'HEADER':
			return error, (infile, "First section is not HEADER")
		DXFcodePage, varName = None, None
		for item in headerSection.data:
			if item[0] == 9:
				if item[1] == '$ACADVER' or item[1] == '$DWGCODEPAGE':
					varName = item[1]
				else:
					varName = None
			elif varName and (item[0] == 1 or item[0] == 3):
				varValue = convert(item[0], item[1])
				if varName == '$ACADVER':
					acadVersion = varValue
					#print("$ACADVER: " + acadVersion)  # DEBUG (pde)
				else:
					DXFcodePage = varValue
					#print("CP: " + DXFcodePage)  # DEBUG (pde)
				varName = None
			if acadVersion and DXFcodePage:
				break
		if not acadVersion:
			return error, (infile, "Unable to identify DXF file version, missing $ACADVER in file!")  # Verbose error message (pde)
		if acadVersion > 'AC1018':
			DXFCodePage = 'utf-8'
			#print("Set default CP UTF-8!")  # DEBUG (pde)
		elif DXFcodePage:
			# The codepage name in the DXF file does not use the same convention as the python code page names
			if DXFcodePage.casefold() == 'ansi_936':  # Case insensitive check (pde)
				DXFcodePage = 'gbk'
				#print("Set CP GBK")  # DEBUG (pde)
			else:
				match = re.match('(?i)\\Aansi_([0-9]+)\\Z', DXFcodePage)
				if match:
					DXFcodePage = 'cp'+match.group(1)
					#print("Set CP: " + DXFcodePage)  # DEBUG (pde)
		if DXFcodePage:
			# Restart with infile changed to the correct encoding. There is no way of changing existing infile
			# without losing its current position so we must go back to 'start' state.
			if sys.version_info >= (3, 7):
				infile.seek(0)
				infile.reconfigure(encoding=DXFcodePage)
			else:
				infile.close()
				infile = open(filename, encoding=DXFcodePage)
			return start, (infile, acadVersion)

	section = findObject(infile, 'section')
	if section:
		return start_section, (infile, drawing, section, acadVersion)
	else:
		return end, (infile, drawing)

def end(infile, drawing):
	"""Called when eof has been reached."""
	#print "Entering end state!"
	return (infile, drawing)

def error(infile, err):
	"""Called when there is an error during processing."""
	#print "Entering error state!"
	infile.close()
	print("There has been an error:")
	print(err)
	return False

def readDXF(filename):
	"""Given a file name try to read it as a dxf file.

	Output is an object with the following structure
	drawing
		header
			header data
		classes
			class data
		tables
			table data
		blocks
			block data
		entities
			entity data
		objects
			object data
	where foo data is a list of sub-objects.  True object data
	is of the form [code, data].
"""	
	infile = open(filename, encoding=None)

	sm = StateMachine()
	sm.add_state(error, True)
	sm.add_state(end, True)
	sm.add_state(start_section)
	sm.add_state(end_section)
	sm.add_state(start)
	sm.set_start(start)
	try:
		(infile, drawing) = sm.run((infile, None))
		if drawing:
			drawing.name = filename
			for obj in drawing.data:
				item, name = get_name(obj.data)
				if name:
					obj.data.remove(item)
					obj.name = name.lower()
					setattr(drawing, name.lower(), obj)
					# Call the objectify function to cast
					# raw objects into the right types of object
					obj.data = objectify(obj.data)
				#print obj.name
	finally:
		# if an exception occurs in sm.run after it has reopened infile, this will close a file
		# already closed, and the open file will be closed when garbage-collected.
		infile.close()
	return drawing
if __name__ == "__main__":
	filename = r".\examples\block-test.dxf"
	drawing = readDXF(filename)
	for item in drawing.entities.data:
		print(item)
