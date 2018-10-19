#!/usr/bin/python

import sys
import numpy
import operator
from decimal import *
import subprocess

def exe_cmd(c):
	p = subprocess.Popen(c, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
	(o, e) = p.communicate()
	p_s = p.wait()
	return o, e, p_s

def pull_data(url):
	cmd="curl -k " + url
	(output,err,p_status)=exe_cmd(cmd)
	l_d = []
	if p_status == 0:
		#print output
		flag = 0
		buf = output.split("\n")
		
		for line in buf:
			if not (line.find('<results') == -1):
				flag = 1
			if (flag == 1 ) & (not (line.find('data=') == -1)):
				flag = 0
				# found the result data block
				dline= line.split("}")
				for dlin in dline:
					# dl hs one row of the result
					dli = dlin.split("{")
					if ( len(dli) > 1):
						dl = dli[1].replace("&quot;","")
						#print dl
						# 
						elem = dl.split(",")
						
						d = {}
						for ele in elem:
							el=ele.split(":")
							d[el[0]]=el[1]
						l_d.append(d)
	return l_d

def get_data(buf):
	# create empty dictionary
	avrg_vals = {}

	# create empty 2 dimentian array
	matc = [[]]
	matcLoss = [[]]
	# go though buff line by line
	for line in buf:
		# only process the lin with substring Qualifier
		if (line['round'] == '2'):
			# split the line by , into array
			# red team name in elem[3], elem[4] and score in elem[7]
			# blue team name in elem[8], elem[9] and score in elem[10]
			# save the team data in avrg_vals dic , key is name , value is one of more score
			if line['red1'] in avrg_vals.keys():
				# if key already existed in the dic
				avrg_vals[line['red1']].append(int(line['redscore']))
			else:
				# if key not existed in the dic
				avrg_vals[line['red1']] = [int(line['redscore'])]

			if line['red2'] in avrg_vals.keys():
				# if key already existed in the dic
				avrg_vals[line['red2']].append(int(line['redscore']))
			else:
				# if key not existed in the dic
				avrg_vals[line['red2']] = [int(line['redscore'])]

			if line['blue1'] in avrg_vals.keys():
				# if key already existed in the dic
				avrg_vals[line['blue1']].append(int(line['bluescore']))
			else:
				# if key not existed in the dic
				avrg_vals[line['blue1']] = [int(line['bluescore'])]

			if line['blue2'] in avrg_vals.keys():
				# if key already existed in the dic
				avrg_vals[line['blue2']].append(int(line['bluescore']))
			else:
				# if key not existed in the dic
				avrg_vals[line['blue2']] = [int(line['bluescore'])]

			# save the winning team names and score diff in the matc 2 dimention array and save losing teams into matcLoss 2 dimension array
			if int(line['redscore']) > int(line['bluescore']) :
				matc.append([line['red1'],line['red2'],(int(line['redscore']) - int(line['bluescore']))])
				matcLoss.append([line['blue1'],line['blue2'],(int(line['redscore']) - int(line['bluescore']))])
			elif int(line['redscore']) < int(line['bluescore']) :
				matc.append([line['blue1'],line['blue2'],(int(line['bluescore']) - int(line['redscore']))])
				matcLoss.append([line['red1'],line['red2'],(int(line['bluescore']) - int(line['redscore']))])

	# create a new dic for team avg
	avrg = {}

	for key,val in avrg_vals.iteritems():
		avrg[key]=numpy.mean(val)


	# go through the matc 2 dimention array to create a new dic diff_vals , key is the team name, value is the weighted win score
	diff_vals = {}
	indx = 1
	while indx < len(matc):
		# win teams names
		name1 = matc[indx][0]
		name2 = matc[indx][1]
		# win teams weighted win score
		diff1 = (matc[indx][2]*avrg[name1])/(avrg[name1] + avrg[name2])
		diff2 = matc[indx][2]-diff1

		if name1 in diff_vals.keys():
			# if key existed in the dic
			diff_vals[name1].append(diff1)
		else:
			# if key not existed in the dic
			diff_vals[name1] = [diff1]

		if name2 in diff_vals.keys():
			diff_vals[name2].append(diff2)
		else:
			diff_vals[name2] = [diff2]

		indx += 1

	# create a new dic for team weighted win difference
	diff = {}
	for key,val in diff_vals.iteritems():
		#diff[key]=numpy.mean(val)
		diff[key]=numpy.mean(val)*(len(diff_vals[key]))/(len(avrg_vals[key]))


	# go through the matcLoss 2 dimention array to create a new dic diffLoss_vals , key is the team name, value is the weighted loss score
	diffLoss_vals = {}
	indx = 1
	while indx < len(matcLoss):
		# win teams names
		name1 = matcLoss[indx][0]
		name2 = matcLoss[indx][1]
		# win teams weighted win score
		diff1 = (matcLoss[indx][2]*avrg[name2])/( avrg[name1] +avrg[name2])
		diff2 = matcLoss[indx][2]-diff1

		if name1 in diffLoss_vals.keys():
			# if key existed in the dic
			diffLoss_vals[name1].append(diff1)
		else:
			# if key not existed in the dic
			diffLoss_vals[name1] = [diff1]

		if name2 in diffLoss_vals.keys():
			diffLoss_vals[name2].append(diff2)
		else:
			diffLoss_vals[name2] = [diff2]

		indx += 1

	# create a new dic for team weighted loss difference
	diffLoss = {}
	for key,val in diffLoss_vals.iteritems():
		#diffLoss[key]=numpy.mean(val)
		diffLoss[key]=numpy.mean(val)*(len(diffLoss_vals[key]))/(len(avrg_vals[key]))

	# finds standard deviations for each list in order to adjust
	stdDiff = numpy.std(diff.values())
	stdDiffLoss = numpy.std(diffLoss.values())
	stdAvrg = numpy.std(avrg.values())

	for key in diff:
		diff[key] *=  10/stdDiff
	for key in diffLoss:
		diffLoss[key] *=  10/stdDiffLoss
	for key in avrg:
		avrg[key] *=  10/stdAvrg

	# create a dic for average score plus difference score
	avrg_diff = {}
	for key,val in avrg.iteritems():
		avrg_diff[key]=val
		if key in diff.keys():
			avrg_diff[key] += diff[key]
		if key in diffLoss.keys():
			avrg_diff[key] -= diffLoss[key]

	stdDiff = numpy.std(diff.values())
	stdDiffLoss = numpy.std(diffLoss.values())
	stdAvrg = numpy.std(avrg.values())

	# print the teams based on the win difference , highest 1st
	print 'Win Share'
	indx = 0
	for key,val in sorted(diff.iteritems(), key=operator.itemgetter(1), reverse=True):
		print key + ' ' + str(val)
		if indx > 13:
			break
		indx +=1

	print str(stdDiff)
	print ''

	# print the teams based on diffLoss
	print 'Loss Share'
	indx = 0
	for key,val in sorted(diffLoss.iteritems(), key=operator.itemgetter(1)):
		print key + ' ' + str(val)
		if indx > 13:
			break
		indx +=1

	print str(stdDiffLoss)
	print ''

	# print the teams based on average scores
	print 'Average Score'
	indx = 0
	for key,val in sorted(avrg.iteritems(), key=operator.itemgetter(1), reverse=True):
		print key + ' ' + str(val)
		if indx > 13:
			break
		indx +=1

	print str(stdAvrg)
	print ''

	# print the teams based on avrg score + difference
	print 'Total Score'
	indx = 0
	for key,val in sorted(avrg_diff.iteritems(), key=operator.itemgetter(1), reverse=True):
		print key + ' ' + str(val)
		if indx > 13:
			break
		indx +=1

#
get_data(pull_data(sys.argv[1]))