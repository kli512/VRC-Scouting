#!/usr/bin/python

#Usage: python this_file scouting_data_file
"""
To-Do:
- Keep Track of Each Team's Autonomous Abiltiy, Issues, and Notes

"""

import sys
import numpy
import operator
from decimal import *
import subprocess
#import os
#import errno
from turtle import Turtle

#statistics
averageConeVals = {} #values for the average number of cones scored per match
averageCones = {} #average cones assuming a 50:50 work ratio between the two teams
adjustedAverageConeVals = {}
adjustedAverageCones = {} #adjusted average assuming a 66:34 work ratio between dominant and non-dominant
dominance = {} #counts the number of teams this team is dominant over
dominated = {} #the other teams that this team is dominant over
adjustedDominance = {} #adjusted for the dominance scores of the teams this team is dominant over
adjustedDominance2 = {}
carried = {}
carriedBy = {}
adjustedCarried = {}
adjustedCarried2 = {}

#information on the robots
robotType = {}
issues = {}
notes = {}



def pullData(file):

	l_d = []
	buf = open(file,"r").read().split("\n")
		
	for line in buf:
		dline = line.split("&")

		d = {}
		for elem in  dline:
			el = elem.split("=")
			d[el[0]] = el[1]
		l_d.append(d)

	return l_d



#func(line[dominant], line[secondTeam], numberOfCones)
def func(team1, team2, cones):

	#dominance
	if team1 in dominance.keys():
		dominance[team1] += 1
		dominated[team1].append(team2)
	else:
		dominance[team1] = 1
		dominated[team1] = [team2]


	#carried
	if team2 in carried.keys():
		carried[team2] += 1
		carriedBy[team2].append(team1)
	else:
		carried[team2] = 1
		carriedBy[team2] = [team1]


	#adjusted average cones
	if team1 in adjustedAverageConeVals.keys():
		adjustedAverageConeVals[team1].append(0.66 * cones)
	else:
		adjustedAverageConeVals[team1] = [0.66 * cones]

	if team2 in adjustedAverageConeVals.keys():
		adjustedAverageConeVals[team2].append(0.34 * cones)
	else:
		adjustedAverageConeVals[team2] = [0.34 * cones]



def processData(buf):
	# go though buff line by line
	for line in buf:

		red_cones = int(line['red_score']) - int(line['red_5pointzone']) - int(line['red_10pointzone']) - int(line['red_20pointzone'])
		blue_cones = int(line['blue_score']) - int(line['blue_5pointzone']) - int(line['blue_10pointzone']) - int(line['blue_20pointzone'])

		#autonomous winner
		if line['autonomousWinner'] == "red":
			red_cones -= 10
		elif line['autonomousWinner'] == "blue":
			blue_cones -= 10

		#high stack on stationary goal
		if line['highStackStationary'] == "red":
			red_cones -= 5
		elif line['highStackStationary'] == "blue":
			blue_cones -= 5

		#high stack in 5 point zone
		if line['highStack5'] == "red":
			red_cones -= 5
		elif line['highStack5'] == "blue":
			blue_cones -= 5

		#high stack in 10 point zone
		if line['highStack10'] == "red":
			red_cones -= 5
		elif line['highStack10'] == "blue":
			blue_cones -= 5

		#high stack in 20 point zone
		if line['highStack20'] == "red":
			red_cones -= 5
		elif line['highStack20'] == "blue":
			blue_cones -= 5

		red_cones /= 2
		blue_cones /= 2

		if line['red_team1'] in averageConeVals.keys():
			averageConeVals[line['red_team1']].append(red_cones/2)
		else:
			averageConeVals[line['red_team1']] = [red_cones/2]

		if line['red_team2'] in averageConeVals.keys():
			averageConeVals[line['red_team2']].append(red_cones/2)
		else:
			averageConeVals[line['red_team2']] = [red_cones/2]

		if line['blue_team1'] in averageConeVals.keys():
			averageConeVals[line['blue_team1']].append(blue_cones/2)
		else:
			averageConeVals[line['blue_team1']] = [blue_cones/2]

		if line['blue_team2'] in averageConeVals.keys():
			averageConeVals[line['blue_team2']].append(blue_cones/2)
		else:
			averageConeVals[line['blue_team2']] = [blue_cones/2]

		if line['red_dominant'] == "team1":
			func(line['red_team1'], line['red_team2'], red_cones)
		elif line['red_dominant'] == "team2":
			func(line['red_team2'], line['red_team1'], red_cones)
		else:
			if line['red_team1'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['red_team1']].append(red_cones / 2)
			else:
				adjustedAverageConeVals[line['red_team1']] = [red_cones / 2]
			if line['red_team2'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['red_team2']].append(red_cones / 2)
			else:
				adjustedAverageConeVals[line['red_team2']] = [red_cones / 2]

		if line['blue_dominant'] == "team1":
			func(line['blue_team1'], line['blue_team2'], blue_cones)
		elif line['blue_dominant'] == "team2":
			func(line['blue_team2'], line['blue_team1'], blue_cones)
		else:
			if line['blue_team1'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['blue_team1']].append(blue_cones / 2)
			else:
				adjustedAverageConeVals[line['blue_team1']] = [blue_cones / 2]
			if line['blue_team2'] in adjustedAverageConeVals.keys():
				adjustedAverageConeVals[line['blue_team2']].append(blue_cones / 2)
			else:
				adjustedAverageConeVals[line['blue_team2']] = [blue_cones / 2]

		if line['red_team1_type'] != "na":
			if line['red_team1'] in robotType.keys():
				if line['red_team1_type'] != robotType[line['red_team1']]:
					robotType[line['red_team1']] = "Conflicting Data Available"
			else:
				robotType[line['red_team1']] = line['red_team1_type']
		if line['red_team2_type'] != "na":
			if line['red_team2'] in robotType.keys():
				if line['red_team2_type'] != robotType[line['red_team2']]:
					robotType[line['red_team2']] = "Conflicting Data Available"
			else:
				robotType[line['red_team2']] = line['red_team2_type']

		if line['blue_team1_type'] != "na":
			if line['blue_team1'] in robotType.keys():
				if line['blue_team1_type'] != robotType[line['blue_team1']]:
					robotType[line['blue_team1']] = "Conflicting Data Available"
			else:
				robotType[line['blue_team1']] = line['blue_team1_type']
		if line['blue_team2_type'] != "na":
			if line['blue_team2'] in robotType.keys():
				if line['blue_team2_type'] != robotType[line['blue_team2']]:
					robotType[line['blue_team2']] = "Conflicting Data Available"
			else:
				robotType[line['blue_team2']] = line['blue_team2_type']

		if line['red_team1_issues'] != "":
			if line['red_team1'] in issues.keys():
				issues[line['red_team1']].append(line['red_team1_issues'])
			else:
				issues[line['red_team1']] = line['red_team1_issues']
		if line['red_team2_issues'] != "":
			if line['red_team2'] in issues.keys():
				issues[line['red_team2']].append(line['red_team2_issues'])
			else:
				issues[line['red_team2']] = line['red_team2_issues']
		if line['blue_team1_issues'] != "":
			if line['blue_team1'] in issues.keys():
				issues[line['blue_team1']].append(line['blue_team1_issues'])
			else:
				issues[line['blue_team1']] = line['blue_team1_issues']
		if line['blue_team2_issues'] != "":
			if line['blue_team2'] in issues.keys():
				issues[line['blue_team2']].append(line['blue_team2_issues'])
			else:
				issues[line['blue_team2']] = line['blue_team2_issues']

		if line['red_team1_notes'] != "":
			if line['red_team1'] in notes.keys():
				notes[line['red_team1']].append(line['red_team1_notes'])
			else:
				notes[line['red_team1']] = line['red_team1_notes']
		if line['red_team2_notes'] != "":
			if line['red_team2'] in notes.keys():
				notes[line['red_team2']].append(line['red_team2_notes'])
			else:
				notes[line['red_team2']] = line['red_team2_notes']
		if line['blue_team1_notes'] != "":
			if line['blue_team1'] in notes.keys():
				notes[line['blue_team1']].append(line['blue_team1_notes'])
			else:
				notes[line['blue_team1']] = line['blue_team1_notes']
		if line['blue_team2_notes'] != "":
			if line['blue_team2'] in notes.keys():
				notes[line['blue_team2']].append(line['blue_team2_notes'])
			else:
				notes[line['blue_team2']] = line['blue_team2_notes']

	for key,val in averageConeVals.iteritems():
		#Note: final cone calculation will be off if the teams parked
		averageCones[key] = numpy.mean(val)

	for key,val in adjustedAverageConeVals.iteritems():
		adjustedAverageCones[key] = numpy.mean(val)

	for key,val in dominated.iteritems():
		adjustedDominance[key] = dominance[key]
		for item in val:
			if item in dominance.keys():
				adjustedDominance[key] += dominance[item]

	for key,val in dominated.iteritems():
		adjustedDominance2[key] = adjustedDominance[key]
		for item in val:
			if item in adjustedDominance.keys():
				adjustedDominance2[key] += adjustedDominance[item]

	for key,val in carriedBy.iteritems():
		adjustedCarried[key] = carried[key]
		for item in val:
			if item in carried.keys():
				adjustedCarried[key] += carried[key]

	for key,val in carriedBy.iteritems():
		adjustedCarried2[key] = adjustedCarried[key]
		for item in val:
			if item in adjustedCarried.keys():
				adjustedCarried2[key] += adjustedCarried[key]



class idk(Turtle):

	text = ''
	x = 0
	y = 0


def displayData():

	print('Average Cones Scored Per Match')
	rank = 1
	for key,val in sorted(averageCones.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( str(rank) + ': ' + key + ' ' + str(val) )
		rank += 1

	rank = 1
	print('Adjusted Average Cones Scored Per Match')
	for key,val in sorted(adjustedAverageCones.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( str(rank) + ': ' + key + ' ' + str(val) )
		rank += 1

	rank = 1
	print('Dominance Points')
	for key,val in sorted(dominance.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( str(rank) + ': ' + key + ' ' + str(val) )
		rank += 1

	rank = 1
	print('Adjusted Dominance Points')
	for key,val in sorted(adjustedDominance.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( str(rank) + ': ' + key + ' ' + str(val) )
		rank += 1

	rank = 1
	print('Adjusted 2x Dominance Points')
	for key,val in sorted(adjustedDominance2.iteritems(), key=operator.itemgetter(1), reverse=True):
		print( str(rank) + ': ' + key + ' ' + str(val) )
		rank += 1

	rank = 1
	print('Carried Points')
	for key,val in sorted(carried.iteritems(), key=operator.itemgetter(1)):
		print( str(rank) + ': ' + key + ' ' + str(val) )
		rank += 1

	rank = 1
	print('Adjusted Carried Points')
	for key,val in sorted(adjustedCarried.iteritems(), key=operator.itemgetter(1)):
		print( str(rank) + ': ' + key + ' ' + str(val) )
		rank += 1

	rank = 1
	print('Adjusted 2x Carried Points')
	for key,val in sorted(adjustedCarried2.iteritems(), key=operator.itemgetter(1)):
		print( str(rank) + ': ' + key + ' ' + str(val) )
		rank += 1

	
	graphStuff = []
	for key,val in sorted(adjustedDominance2.iteritems(), key=operator.itemgetter(1), reverse=True):
		temp = idk()
		temp.text = str(key)
		temp.x = val
		if key in adjustedCarried2.keys():
			temp.y = adjustedCarried2[key]
		else:
			temp.y = 0
		print( str(temp.x) + ',' + str(temp.y) )
		temp.pencolor('blue')
		graphStuff.append(temp)

	for key,val in sorted(adjustedCarried2.iteritems(), key=operator.itemgetter(1), reverse=True):
		if key not in adjustedDominance2.keys():
			temp = idk()
			temp.text = str(key)
			temp.x = 0
			temp.y = val
			print( str(temp.x) + ',' + str(temp.y) )
			temp.pencolor('blue')
			graphStuff.append(temp)

	minX = graphStuff[0].x
	maxX = graphStuff[0].x
	minY = graphStuff[0].y
	maxY = graphStuff[0].y
	for item in graphStuff:
		if item.x < minX:
			minX = item.x
		if item.x > maxX:
			maxX = item.x
		if item.y < minY:
			minY = item.y
		if item.y > maxY:
			maxY = item.y

	rangeX = maxX-minX
	rangeY = maxY-minY

	for item in graphStuff:
		item.x -= minX
		item.x *= 450
		item.x /= rangeX
		item.x -= 275

		item.y -= minY
		item.y *= 450
		item.y /= rangeY
		item.y -= 250

	temp = idk()
	temp.x = -275
	temp.y = rangeY * 450 / rangeY - 225
	temp.text = "Worst"
	temp.pencolor('red')
	graphStuff.append(temp)

	temp = idk()
	temp.x = rangeX * 450 / rangeX - 225
	temp.y = -250
	temp.text = "Best"
	temp.pencolor('green')
	graphStuff.append(temp)


	for item in graphStuff:
		item.penup()
		item.hideturtle()
		item.goto(item.x, item.y)
		#item.dot(4)
		item.write(item.text,move=True,align="center",font=("Freestyle Script",10,"normal"))

	count = 0
	while count < 1e20:
		count += 1



#
processData(pullData(sys.argv[1]))
displayData()