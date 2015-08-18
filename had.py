import re
import urllib2
import pprint

f = open('had.txt', 'r')

download = False

pageraw = f.read()

f.close()

excludedProjects = set([37, 46])

projects = re.findall(r'/project/(\d+)', pageraw)
projects = set([int(project) for project in projects])
projects = sorted(projects - excludedProjects)

#print projects

if download:
	for project in projects:
		print str(round((1.0 * projects.index(project)) / len(projects) * 10000) / 100)  + "%"
		url = 'http://www.hackaday.io/project/' + str(project)
		f2 = open('had/' + str(project) + '.txt', 'w')
		response = urllib2.urlopen(url)
		html = response.read()
		f2.write(html)
		f2.close()
		#print url

		url = 'http://www.hackaday.io/project/' + str(project) + '/logs'
		f2 = open('had/' + str(project) + 'L.txt', 'w')
		response = urllib2.urlopen(url)
		html = response.read()
		f2.write(html)
		f2.close()
		#print url

projectVideos = 0
tally = {0: 0}
projectsMin4Logs = 0
projectsQualifying = list()
for project in projects:
	projectVideo = False
	project4Logs = False
	f2 = open('had/' + str(project) + '.txt', 'r')
	projectraw = f2.read()
	f2.close()
	youtubes = re.findall(r'["\'](?:https://|http://|//|)(?:www\.|)youtube\.[a-z\.]{2,6}/.*?["\']', projectraw, re.IGNORECASE)
	#print project
	for youtube in youtubes:
		projectVideo = True
		#print "    " + youtube

	f2 = open('had/' + str(project) + 'L.txt', 'r')
	projectraw = f2.read()
	f2.close()
	youtubes = re.findall(r'["\'](?:https://|http://|//|)(?:www\.|)youtube\.[a-z\.]{2,6}/.*?["\']', projectraw, re.IGNORECASE)
	for youtube in youtubes:
		projectVideo = True
		#print "    " + youtube

	if projectVideo is True:
		projectVideos += 1




	f2 = open('had/' + str(project) + '.txt', 'r')
	projectraw = f2.read()
	f2.close()
	logamt = re.search(r'View all (\d*) project logs', projectraw, re.IGNORECASE)
	if logamt is not None:
		#print logamt.group(0)
		if not int(logamt.group(1)) in tally.keys():
			tally[int(logamt.group(1))] = 0
		tally[int(logamt.group(1))] += 1
		if int(logamt.group(1)) >= 4:
			projectsMin4Logs += 1
			project4Logs = True
	else:
		if not "0" in tally.keys():
			tally["0"] = 0
		tally["0"] += 1
	if project4Logs and projectVideo:
		projectsQualifying.append(project)
		#print "Q: http://hackaday.io/project/" + str(project)


print "Projects with at least one youtube video: " + str(projectVideos)
print "Projects with X project logs:"
pprint.pprint(tally)
print "Projects with 4 or more project logs:"
print projectsMin4Logs
print "Projects QUALIFYING - with at least one youtube video and at least 4 logs:"
print len(projectsQualifying)
print projectsQualifying
'''

--> projects 46 and 37 NO!
                            <a href="/project/46/log/460">Everything 101</a>

                            <a href="/project/37-Feedback---Hackaday-Projects">Give Feedback</a>
                            <a href="/project/37">Give Feedback</a>


'''