import re
import urllib2
import pprint
import json
import sys

download = False
dataDump = False
tally = False
debug = False
excludedProjects = set([37, 46])

f = open('had.txt', 'r')
pageraw = f.read()
f.close()

projects = re.findall(r'/project/(\d+)', pageraw)
projects = set([int(project) for project in projects])
projects = sorted(projects - excludedProjects)

#print projects
if download:
    for project in projects:
        sys.stdout.write("\rDownloading Projects: " + str(round((1.0 * projects.index(project)) / len(projects) * 10000) / 100) + "%")
        sys.stdout.flush()

        url = 'http://www.hackaday.io/project/' + str(project)
        f2 = open('had/' + str(project) + '.txt', 'w')
        response = urllib2.urlopen(url)
        html = response.read()
        f2.write(html)
        f2.close()

        url = 'http://www.hackaday.io/project/' + str(project) + '/logs'
        f2 = open('had/' + str(project) + 'L.txt', 'w')
        response = urllib2.urlopen(url)
        html = response.read()
        f2.write(html)
        f2.close()
    print

projectVideos = 0
if tally:
    logTally = {}
    tagTally = {}
projectsMin4Logs = 0
projectsMin8Logs = 0
projectsQualifying = list()
projectsQualifyingBP = list()
if dataDump:
    parsedData = dict()
for project in projects:
    sys.stdout.write("\rProcessing Projects: " + str(round((1.0 * projects.index(project)) / len(projects) * 10000) / 100) + "%")
    sys.stdout.flush()
    projectLogAmount = 0
    projectVideo = 0
    projectMentionsLicense = False

    f2 = open('had/' + str(project) + '.txt', 'r')
    projectRaw = f2.read()
    f2.close()
    licenses = re.findall(r'licen[sc]e', projectRaw, re.IGNORECASE)
    youtubes = re.findall(r'["\'](?:https://|http://|//|)(?:www\.|)youtu(?:be|)\.[a-z\.]{2,6}/.*?["\']', projectRaw, re.IGNORECASE)
    bestProductEntry = re.findall(r'<li><a href="/submissions/bestproduct/list">Best Product</a></li>', projectRaw, re.IGNORECASE)
    logScrape = re.search(r'View all (\d*) project logs', projectRaw, re.IGNORECASE)
    if dataDump or tally:
        tags = re.findall(r'<a href="/projects/tag/(?:.*?)" class="tag.*?">(.*)</a>', projectRaw, re.IGNORECASE)
        tags = [tag.lower() for tag in tags]
    if dataDump:
        comments = len(re.findall(r'comment-\d{0,10}-content', projectRaw, re.IGNORECASE))
        commentsLogs = re.findall(r'\s*<a class="gray-link" href="/project/\d*/log/\d*#discussion-list">\n\s*(\d*) comments\n\s*</a>', projectRaw, re.IGNORECASE)
        for comment in commentsLogs:
            comments += int(comment)
    if dataDump:
        followerAmt = int(re.search(r'id="follower_count">(\d+)</span>', projectRaw).group(1))
        skullAmt = int(re.search(r'id="like_count">(\d+)</span>', projectRaw).group(1))
        try:
            viewAmt = int(re.search(r'title="View Count">(\d+)</span>', projectRaw).group(1))
        except AttributeError:
            viewAmt = None

    if tally:
        for tag in tags:
            if not tag in tagTally.keys():
                tagTally[tag] = 0
            tagTally[tag] += 1
    if logScrape is not None:
        if tally:
            if not int(logScrape.group(1)) in logTally.keys():
                logTally[int(logScrape.group(1))] = 0
            logTally[int(logScrape.group(1))] += 1
        projectLogAmount = int(logScrape.group(1))
    else:
        if tally:
            if not "0" in logTally.keys():
                logTally["0"] = 0
            logTally["0"] += 1
        projectLogAmount = 0

    f2 = open('had/' + str(project) + 'L.txt', 'r')
    logsRaw = f2.read()
    f2.close()
    licenses = list(licenses) + list(re.findall(r'licen[sc]e', logsRaw, re.IGNORECASE))
    youtubes = list(youtubes) + list(re.findall(
        r'["\'](?:https://|http://|//|)(?:www\.|)youtu(?:be|)\.[a-z\.]{2,6}/.*?["\']', logsRaw, re.IGNORECASE))

    qualifiesQF = (projectLogAmount >= 4) and (len(youtubes) >= 1)
    qualifiesBP = (projectLogAmount >= 8) and (len(youtubes) >= 2) and (len(licenses) > 0) and (len(bestProductEntry) > 0)

    if qualifiesQF:
        projectsQualifying.append(project)
    if qualifiesBP:
        projectsQualifyingBP.append(project)

    if dataDump:
        parsedData[int(project)] = {'tags': tags,
                'qual': {'quarterfinals': qualifiesQF, 'bestproduct-1': qualifiesBP},
                'logAmt': projectLogAmount,
                'followerAmt': followerAmt,
                'skullAmt': skullAmt,
                'viewAmt': viewAmt,
                'videoAmt': len(youtubes),
                'commentAmt': comments};

print

if tally:
    print "Projects with X project logs:"
    pprint.pprint(logTally)
    print "Projects with tag X:"
    pprint.pprint(tagTally)

if debug:
    print "Projects with 4 or more project logs:"
    print projectsMin4Logs
    print "Projects QUALIFYING - with at least one youtube video and at least 4 logs:"
    print len(projectsQualifying)
    print projectsQualifying
    print "Projects QUALIFYING BP - with at least 2 youtube videos and at least 8 logs, mentioning 'license':"
    print len(projectsQualifyingBP)
    print projectsQualifyingBP

if dataDump:
    print json.dumps(parsedData)
'''

--> projects 46 and 37 NO!
                            <a href="/project/46/log/460">Everything 101</a>

                            <a href="/project/37-Feedback---Hackaday-Projects">Give Feedback</a>
                            <a href="/project/37">Give Feedback</a>

                                                <span class="icon-view oi-font-color-grey" title="Followers" id="follower_count">73</span>
                    <span class="icon-comment-with-hover oi-font-color-grey" title="Comments" id="comment_count">1</span>
                            <span class="icon-skull oi-font-color-grey" title="Skulls" id="like_count">22</span>
                                                <span class="icon-view-count" title="View Count">5.1k</span>



Info for export: tags (json array); BP qual; 1/4finals qual; project logs; followers; skulls; views; youtube videos; comments

'''