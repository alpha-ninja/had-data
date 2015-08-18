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
projectsMin8Logs = 0
projectsQualifying = list()
projectsQualifyingBP = list()
for project in projects:
	projectLogAmount = 0
	projectVideo = 0
	projectMentionsLicense = False




	f2 = open('had/' + str(project) + '.txt', 'r')
	projectraw = f2.read()
	f2.close()
	licenses = re.findall(r'licen[sc]e', projectraw, re.IGNORECASE)
	youtubes = re.findall(r'["\'](?:https://|http://|//|)(?:www\.|)youtu(?:be|)\.[a-z\.]{2,6}/.*?["\']', projectraw, re.IGNORECASE)
	product = re.findall(r'<li><a href="/submissions/bestproduct/list">Best Product</a></li>', projectraw, re.IGNORECASE)
	logamt = re.search(r'View all (\d*) project logs', projectraw, re.IGNORECASE)
	if logamt is not None:
		#print logamt.group(0)
		if not int(logamt.group(1)) in tally.keys():
			tally[int(logamt.group(1))] = 0
		tally[int(logamt.group(1))] += 1
		projectLogAmount = int(logamt.group(1))
	else:
		if not "0" in tally.keys():
			tally["0"] = 0
		tally["0"] += 1
		projectLogAmount = 0




	f2 = open('had/' + str(project) + 'L.txt', 'r')
	projectraw = f2.read()
	f2.close()
	licenses = list(licenses) + list(re.findall(r'licen[sc]e', projectraw, re.IGNORECASE))
	youtubes = list(youtubes) + list(re.findall(r'["\'](?:https://|http://|//|)(?:www\.|)youtu(?:be|)\.[a-z\.]{2,6}/.*?["\']', projectraw, re.IGNORECASE))




	if (projectLogAmount >= 4) and (len(youtubes) >= 1):
		projectsQualifying.append(project)
	if (projectLogAmount >= 8) and (len(youtubes) >= 2) and (len(licenses) > 0) and (len(product) > 0):
		projectsQualifyingBP.append(project)
		#print "Q: http://hackaday.io/project/" + str(project)


#print "Projects with at least one youtube video: " + str(projectVideos)
#print "Projects with X project logs:"
#pprint.pprint(tally)
#print "Projects with 4 or more project logs:"
#print projectsMin4Logs
print "Projects QUALIFYING - with at least one youtube video and at least 4 logs:"
print len(projectsQualifying)
print projectsQualifying
print "Projects QUALIFYING BP - with at least 2 youtube videos and at least 8 logs, mentioning 'license':"
print len(projectsQualifyingBP)
print projectsQualifyingBP
'''

--> projects 46 and 37 NO!
                            <a href="/project/46/log/460">Everything 101</a>

                            <a href="/project/37-Feedback---Hackaday-Projects">Give Feedback</a>
                            <a href="/project/37">Give Feedback</a>


'''