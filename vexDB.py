
"""
Usage:
python vexDB.py vex_sku
(ex: python vexDB.py RE-VRC-17-3358)

SKUs:
Niles West 2018: RE-VRC-17-3342
Rolling Meadows 2018: RE-VRC-17-3212
Neuqua 2018: RE-VRC-17-3406
ISU 2018: RE-VRC-17-4493
Illinois State 2018 (High School): RE-VRC-17-3358
US CREATE 2018 (High School): RE-VRC-17-2559
VEX Worlds 2018 (High School): RE-VRC-17-3805

Random Links:
http://vex-elo-rankings.herokuapp.com/
"""

import sys
import numpy
import operator
from decimal import *
import subprocess
import json


def exe_cmd(cmd):
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	(o, e) = p.communicate()
	p_s = p.wait()
	return o, e, p_s


def get_data(sku):

	teams = {}

	"""
	#we should create an offline database to avoid calls to this
	limit = 0
	while limit < 30000:
		url = '"https://api.vexdb.io/v1/get_teams?program=VRC&limit_start=' + str(limit) + '"'

		(output, err, p_status) = exe_cmd("curl -k " + url)
		teamData = json.loads(output)
		for team in teamData['result']:
			teams[team['number']] = team['team_name']
		limit += 5000
	"""

	f = open('teamdatabase.csv', 'r')
	for line in f.read().split('\n'):
		team = line.split(',')
		if len(team) == 2:
			teams[team[0]] = team[1]

	url = "https://api.vexdb.io/v1/get_events?sku=" + sku
	(output, err, p_status) = exe_cmd("curl -k " + url)
	data = json.loads(output)
	divisions = data['result'][0]['divisions']

	url = "https://api.vexdb.io/v1/get_matches?sku=" + sku
	(output, err, p_status) = exe_cmd("curl -k " + url)
	division_data = json.loads(output)

	return teams, divisions, division_data


def process_data(sku):

	(teams, divisions, division_data) = get_data(sku)

	avrg_vals = {}
	matc = {}
	matcLoss = {}
	avrg = {}
	diff_vals = {}
	diff = {}
	diffLoss_vals = {}
	diffLoss = {}
	avrg_diff = {}

	#this could be made much faster
	for division in divisions:

		print division.upper()

		avrg_vals[division] = {}
		matc[division] = [[]]
		matcLoss[division] = [[]]
		avrg[division] = {}
		diff_vals[division] = {}
		diff[division] = {}
		diffLoss_vals[division] = {}
		diffLoss[division] = {}
		avrg_diff[division] = {}

		for match in division_data['result']:

			if match['division'] != division:
				continue

			if match['red1'] in avrg_vals[division].keys():
				avrg_vals[division][match['red1']].append(int(match['redscore']))
			else:
				avrg_vals[division][match['red1']] = [int(match['redscore'])]
			if match['red2'] in avrg_vals[division].keys():
				avrg_vals[division][match['red2']].append(int(match['redscore']))
			else:
				avrg_vals[division][match['red2']] = [int(match['redscore'])]
			if match['blue1'] in avrg_vals[division].keys():
				avrg_vals[division][match['blue1']].append(int(match['bluescore']))
			else:
				avrg_vals[division][match['blue1']] = [int(match['bluescore'])]
			if match['blue2'] in avrg_vals[division].keys():
				avrg_vals[division][match['blue2']].append(int(match['bluescore']))
			else:
				avrg_vals[division][match['blue2']] = [int(match['bluescore'])]

			if int(match['redscore']) > int(match['bluescore']):
				matc[division].append( [match['red1'], match['red2'], (int(match['redscore'])-int(match['bluescore']))] )
				matcLoss[division].append( [match['blue1'], match['blue2'], (int(match['redscore'])-int(match['bluescore']))] )
			elif int(match['redscore']) < int(match['bluescore']):
				matcLoss[division].append( [match['red1'], match['red2'], (int(match['redscore'])-int(match['bluescore']))] )
				matc[division].append( [match['blue1'], match['blue2'], (int(match['redscore'])-int(match['bluescore']))] )

		for key,val in avrg_vals[division].iteritems():
			avrg[division][key] = numpy.mean(val)

		indx = 1
		while indx < len(matc[division]):
			name1 = matc[division][indx][0]
			name2 = matc[division][indx][1]

			diff1 = (matc[division][indx][2]*avrg[division][name2]) / (avrg[division][name1]+avrg[division][name2])
			diff2 = matc[division][indx][2]-diff1

			if name1 in diff_vals[division].keys():
				diff_vals[division][name1].append(diff1)
			else:
				diff_vals[division][name1] = [diff1]
			if name2 in diff_vals[division].keys():
				diff_vals[division][name2].append(diff2)
			else:
				diff_vals[division][name2] = [diff2]

			indx += 1

		for key,val in diff_vals[division].iteritems():
			diff[division][key] = numpy.mean(val)*(len(diff_vals[division][key]))/(len(avrg_vals[division][key]))


		indx = 1
		while indx < len(matcLoss[division]):
			name1 = matcLoss[division][indx][0]
			name2 = matcLoss[division][indx][1]

			diff1 = (matcLoss[division][indx][2]*avrg[division][name2]) / (avrg[division][name1]+avrg[division][name2])
			diff2 = matcLoss[division][indx][2]-diff1

			if name1 in diffLoss_vals[division].keys():
				diffLoss_vals[division][name1].append(diff1)
			else:
				diffLoss_vals[division][name1] = [diff1]
			if name2 in diffLoss_vals[division].keys():
				diffLoss_vals[division][name2].append(diff2)
			else:
				diffLoss_vals[division][name2] = [diff2]

			indx += 1

		for key,val in diffLoss_vals[division].iteritems():
			diffLoss[division][key] = numpy.mean(val)*(len(diffLoss_vals[division][key]))/(len(avrg_vals[division][key]))

		stdDiff = numpy.std(diff[division].values())
		stdDiffLoss = numpy.std(diffLoss[division].values())
		stdAvrg = numpy.std(avrg[division].values())

		for key in diff[division]:
			diff[division][key] *= 10/stdDiff
		for key in diffLoss[division]:
			diffLoss[division][key] *= 10/stdDiffLoss
		for key in avrg[division]:
			avrg[division][key] *= 10/stdAvrg

		for key,val in avrg[division].iteritems():
			avrg_diff[division][key] = val
			if key in diff[division].keys():
				avrg_diff[division][key] += diff[division][key]
			if key in diffLoss[division].keys():
				avrg_diff[division][key] -= diffLoss[division][key]

		indx = 1
		output = ''
		for key,val in sorted(avrg_diff[division].iteritems(), key=operator.itemgetter(1), reverse=True):
			if key in teams.keys():
				print str(indx) + ' \t' + str(key) + ' \t[' + teams[key] + '] \t' + str(val)
				output += str(indx) + ',' + str(key) + ',' + teams[key] + ',' + str(val) + '\n'
			else:
				print str(indx) + ' \t' + str(key) + ' \t' + str(val)
				output += str(indx) + ',' + str(key) + ',,' + str(val) + '\n'
			indx += 1

		f = open(sku+'_'+division.replace(' ', "")+'.csv', 'w')
		f.write(output);
		f.close()

process_data(sys.argv[1])


