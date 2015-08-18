import re
import urllib2

f = open('had.txt', 'r')

download = True


pageraw = f.read()

f.close()

excludedProjects = set([37, 46])

projects = re.findall(r'/project/(\d+)', pageraw)
projects = set([int(project) for project in projects])
projects = sorted(projects - excludedProjects)

print projects

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

quarterfinalsMentions = 0

for project in projects:
	quarterfinalsMentioned = False
	f2 = open('had/' + str(project) + '.txt', 'r')
	projectraw = f2.read()
	f2.close()
	youtubes = re.findall(r'[\'"]https?://www.youtube\.com.*?</a>', projectraw, re.IGNORECASE)
	print project
	for youtube in youtubes:
		if re.search(r'quarterfinal', youtube, re.IGNORECASE):
			quarterfinalsMentioned = True
		print "    " + youtube

	f2 = open('had/' + str(project) + 'L.txt', 'r')
	projectraw = f2.read()
	f2.close()
	youtubes = re.findall(r'[\'"]https?://www.youtube\.com.*?</a>', projectraw, re.IGNORECASE)
	print project
	for youtube in youtubes:
		if re.search(r'quarterfinal', youtube, re.IGNORECASE):
			quarterfinalsMentioned = True
		print "    " + youtube

	if quarterfinalsMentioned:
		quarterfinalsMentions += 1

print "Mentions of 'quarterfinal[s]': " + str(quarterfinalsMentions)

'''

--> projects 46 and 37 NO!
                            <a href="/project/46/log/460">Everything 101</a>

                            <a href="/project/37-Feedback---Hackaday-Projects">Give Feedback</a>
                            <a href="/project/37">Give Feedback</a>


'''