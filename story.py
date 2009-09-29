#Story.py
#Copyright (C) 2009 Robin Wellner (gvx)
#Part of SpaceFlight2D
#
#SpaceFlight2D is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

import random
import sectors

SystemPrimitives = ['Yu', 'Zega', 'Fnurax', 'Pera', 'Zepo', 'Qnax', 'Tyari',
					'Gnorplax', 'Veolan', 'Frrt', 'Hemano', 'Torqis', 'Retora',
					'Blagulon', 'Maximegalon', 'Zondostina', 'Zarss', 'Stavromula',
					'Spamalot', 'Aaaaarg', 'Monty', 'Parrota', 'Ministeria', 'Silwalk', 'Cheeshop',
					'Eastasia', 'Roomwanowa', 'Bigbrotha', 'Yatria', 'Semitru', 'Watsioname',
					'Fesia', 'Zelka', 'Oxuek', 'Mixje', 'Komex', 'Quriali', 'Karika', 'Jasion',
					'Yggials', 'Pfsip', 'Dimn', 'Suzk', 'Miraia', 'Tenkalo', 'Hoeisa', 'Io',
					'Mingel', 'Zing', 'Poiing', 'Dendrox', 'Peramia', 'Konquis', 'Merkal',
					'Foo', 'Bar', 'Baz', 'Ploz', 'Meng', 'Too', 'Zif', 'Quork', 'Olm',
					'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota',
					'Kapa', 'Labda', 'Mu', 'Nu', 'Xi', 'Omikron', 'Pi', 'Rho', 'Sigma', 'Tau',
					'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega'
					]

def NewSystemName():
	return random.choice(SystemPrimitives) + ' ' + random.choice(SystemPrimitives)

CORP = 0
GAME = 1
UNKNOWN = 2
CAPTIONS = ('HyperCorp Mission Control', 'Game', 'Unknown Source')

Messages = {0000: (CORP, 'Good morning, captain. Today is a great day to explore space for HyperCorp!'),
			0001: (CORP, 'Now, go to a few planets and build a base on them.'),
			0002: (CORP, 'Congratulations on your first base! Now, go explore the rest of the system, and don\'t forget to bring home the oil you find.'),
			0100: (CORP, 'You conquered the whole system! We found a new system for you to explore. Fly to the coordinates we send you.'),
			0200: (CORP, 'Return to Home System immediately.'),
			9999: (GAME, 'You completed the game!')
		   }

###################################
#Check Progress & Continue Story Line
def check(action, *globals): #Awful, but I can think of no better way.
	"""story.check(action, gameData, DisplayMessage, SystemContainer, Planet, ArchiveContainer, enemyShip, playerShip, ReprKey, KEYS, GRID_WIDTH)"""
	gameData = globals[0]
	DisplayMessage = globals[1]
	SystemContainer = globals[2]
	Planet = globals[3]
	ArchiveContainer = globals[4]
	enemyShip = globals[5]
	playerShip = globals[6]
	ReprKey = globals[7]
	KEYS = globals[8]
	GRID_WIDTH = globals[9]
	if not gameData.tutorial:
		if action == 'game started':
			DisplayMessage(Messages[0000][1],CAPTIONS[Messages[0000][0]])
			DisplayMessage(Messages[0001][1],CAPTIONS[Messages[0001][0]])
			gameData.tasks.append("Build a base on another planet")
		elif action == 'base built':
			if (gameData.basesBuilt % 9) == 8:
				if gameData.basesBuilt == 26:
					DisplayMessage(Messages[0200][1],CAPTIONS[Messages[0200][0]])
					gameData.tasks.append("Fly to Sector 0:0")
					gameData.stage = 1
				else:
					DisplayMessage(Messages[0100][1],CAPTIONS[Messages[0100][0]])
					rndX = random.choice((-1, 1)) * random.randint(3, 10) * 10000
					rndY = random.choice((-1, 1)) * random.randint(3, 10) * 10000
					SystemContainer.append((rndX*GRID_WIDTH/sectors.SECTOR_SIZE, rndY*GRID_WIDTH/sectors.SECTOR_SIZE, NewSystemName()))#"Unnamed system")
					for newPlanetX in range(-1, 2):
						for newPlanetY in range(-1, 2):
							ArchiveContainer.append(Planet(rndX + newPlanetX * 20000 + random.randint(-8000, 8000), -rndY + newPlanetY * 18000 + random.randint(-6000, 6000), random.randint(250, 1500)))
							ArchiveContainer[-1].enemyAt = random.choice((None, random.randint(0, 360)))
					gameData.tasks.append("Fly to Sector "+ sectors.pixels2sector(rndX,rndY))
				try:
					gameData.tasks.remove("Conquer this system")
				except:
					pass
			elif gameData.basesBuilt == 1:
				DisplayMessage(Messages[0002][1],CAPTIONS[Messages[0002][0]])
				gameData.tasks.remove("Build a base on another planet")
				gameData.tasks.append("Conquer this system")
			elif gameData.stage == 2.5:
				gameData.tasks.remove("Build a base on that planet")
				DisplayMessage("That was a stupid move of you.", "The other spaceship")
				DisplayMessage("Just stay away from our main planet. I'll give you the coordinates, so you can avoid it.", "The other spaceship")
				rndX = random.choice((-1, 1)) * 140000
				rndY = random.choice((-1, 1)) * 140000
				pX = rndX + random.randint(-3000, 3000)
				pY = rndY + random.randint(-3000, 3000)
				ArchiveContainer.append(Planet(pX, pY, 2000))
				ArchiveContainer[-1].enemyAt = random.randint(0, 360)
				for n in range(1, 10):
					o = random.randint(0, 360)
					bound = 2000+n*400
					ArchiveContainer.append(enemyShip(pX + bound*cos(radians(o)), pY + bound*sin(radians(o)), 0, 0, 2+4.0/n ,(pX,pY,bound)))
					ArchiveContainer[-1].orbitpos = o
				DisplayMessage("You got what from who? Well, I think you should go there anyway.", 'Misson Control')
				gameData.tasks.append("Fly to Sector "+ sectors.pixels2sector(rndX,rndY))
				gameData.stage = 3
		elif action == 'sector changed':
			try:
				gameData.tasks.remove("Fly to Sector " + sectors.pixels2sector(playerShip.X,playerShip.Y))
				if gameData.stage == 0:
					gameData.tasks.append("Conquer this system")
				elif gameData.stage == 1:
					DisplayMessage("Good. You'll get a better hull and a larger oilsupply. You only have to fill it yourself.", 'Misson Control')
					playerShip.maxoil = 3000
					playerShip.maxhull = 1200
					DisplayMessage("If you think you're ready, just go to the sector on your task list.", 'Misson Control')
					rndX = random.choice((-1, 1)) * random.randint(11, 12) * 10000
					rndY = random.choice((-1, 1)) * random.randint(11, 12) * 10000
					pX = rndX + random.randint(-3000, 3000)
					pY = rndY + random.randint(-3000, 3000)
					ArchiveContainer.append(Planet(pX, pY, 1700))
					ArchiveContainer[-1].enemyAt = random.randint(0, 360)
					ArchiveContainer.append(enemyShip(pX + 2000, pY, 0, 0, 5 ,(pX,pY,2000)))
					gameData.tasks.append("Fly to Sector "+ sectors.pixels2sector(rndX,rndY))
					gameData.stage = 2
				elif gameData.stage == 2:
					DisplayMessage("Who are you, and what are you doing here?", "Unknown source")
					DisplayMessage("This is our planet. Get away before we attack you.", "The same unknown source")
					DisplayMessage("What are you waiting for? Go investigate that planet!", "Mission Control")
					gameData.tasks.append("Build a base on that planet")
					gameData.stage = 2.5
				elif gameData.stage == 3:
					DisplayMessage("This is the end of the storyline so far. Congratulations!", "Game")
			except:
				pass
	else:
		if action == 'game started':
			DisplayMessage("Welcome to this tutorial! You will learn the basic controls and tricks of SpaceFlight2D.", "Tutorial")
			DisplayMessage(ReprKey(KEYS['UP'])+", "+ReprKey(KEYS['LEFT'])+", and "+ReprKey(KEYS['RIGHT'])+" will get you everywhere. Try it a bit, and land on the planet when you're done.", "Tutorial")
			gameData.tasks.append("Fly around, and land on the planet.")
			gameData.stage = 1
		if action == 'player landed':
			if gameData.stage == 1:
				gameData.tasks.remove("Fly around, and land on the planet.")
				DisplayMessage("If you had a base on this planet, you could use the oil in it for your shield or you could use it as fuel.", "Tutorial")
				DisplayMessage("Press "+ReprKey(KEYS['BUILD'])+" to build a base.", "Tutorial")
				gameData.tasks.append("Build a base.")
				gameData.stage = 2
		if action == 'base failed':
			if gameData.stage == 2:
				gameData.tasks.remove("Build a base.")
				DisplayMessage("That didn't work. That's because on the other side of the planet lies an enemy base.", "Tutorial")
				DisplayMessage("Use "+ReprKey(KEYS['ZOOMIN'])+" and "+ReprKey(KEYS['ZOOMOUT'])+" to zoom in and out, so you can get a clear look at it.", "Tutorial")
				DisplayMessage("Then go to it and distroy the base with "+ReprKey(KEYS['FIRE'])+". Afterwards, build your base.", "Tutorial")
				DisplayMessage("And one tip: approach the enemy base quickly and shoot it right away. It WILL fire back.", "Tutorial")
				gameData.tasks.append("Destroy the enemy's base.")
				gameData.tasks.append("Build your own base.")
				gameData.stage = 3
		if action == 'base built':
			if gameData.stage == 3:
				gameData.tasks.remove("Destroy the enemy's base.")
				gameData.tasks.remove("Build your own base.")
				DisplayMessage("Now, nearby lies a small moon. You can fly to that and conquer it by building a base on it.", "Tutorial")
				DisplayMessage("However, it might be a good idea to fill your oil tank with "+ReprKey(KEYS['FILL'])+" and repair your shield with "+ReprKey(KEYS['REPAIR'])+" before flying to another world.", "Tutorial")
				gameData.tasks.append("Build a base on the moon.")
				gameData.stage = 4
			elif gameData.stage == 4:
				gameData.tasks.remove("Build a base on the moon.")
				DisplayMessage("Congratulations, you almost completed the tutorial!", "Tutorial")
				DisplayMessage("If you press S you can save your progress. When you press "+ReprKey(KEYS['LAUNCH'])+" you will speed up very quickly (and drain your oil tank even more quickly). Finally, "+ReprKey(KEYS['PAUSE'])+" pauses the game.", "Tutorial")
				DisplayMessage("If you are done playing with just one planet and a moon, press Escape and start a REAL game.", "Tutorial")
				gameData.tasks.remove("Follow the instructions.")
