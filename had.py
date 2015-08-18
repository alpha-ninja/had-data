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
		url = 'http://www.hackaday.io/project/' + str(project)
		f2 = open('had/' + str(project) + '.txt', 'w')
		response = urllib2.urlopen(url)
		html = response.read()
		f2.write(html)
		f2.close()
		print url

'''

--> projects 46 and 37 NO!
                            <a href="/project/46/log/460">Everything 101</a>

                            <a href="/project/37-Feedback---Hackaday-Projects">Give Feedback</a>
                            <a href="/project/37">Give Feedback</a>


'''