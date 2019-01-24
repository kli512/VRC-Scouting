
import subprocess
import json
import re

def exe_cmd(cmd):
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	(o, e) = p.communicate()
	p_s = p.wait()
	return o, e, p_s


def main():

	teams = {}
	size = 5000
	limit = 0

	while size != 0:

		url = '"https://api.vexdb.io/v1/get_teams?program=VRC&limit_start=' + str(limit) + '"'
		(output, err, p_status) = exe_cmd("curl -k " + url)
		teamData = json.loads(output)

		for team in teamData['result']:
			teams[team['number']] = team['team_name']

		size = int(teamData['size'])
		limit += 5000

	f = open('teamdatabase.csv', 'w')
	output = ''

	for key,val in teams.iteritems():
		output += str(key) + ',' + re.sub(r'[^\x00-\x7f]',r' ', val)  + '\n'

	f.write(output)
	f.close()
	print 'team database updated successfully'

main()