#Sectors.py
#Copyright (C) 2009 Robin Wellner (gvx)
#Part of SpaceFlight2D
#
#SpaceFlight2D is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

SECTOR_SIZE = 40000

def pixels2sector(x, y):
	return str(int(x/SECTOR_SIZE+.5)) + ":" + str(int(-y/SECTOR_SIZE+.5))

def sector2pixels(sec):
	x, y = sec.split(":")
	return int(x)*SECTOR_SIZE, -int(y)*SECTOR_SIZE
