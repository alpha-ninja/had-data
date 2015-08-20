import re
import urllib2
import pprint
import json
import sys
import glob
import os.path

download = False
dataDump = False
dataDumpUseJSON = True
tally = False
debug = True
excludedProjects = set([37, 46])

def fuzzyToNumber(fuzzy):
    if fuzzy is not None:
        factor = 1
        if fuzzy[-1:] is 'k':
            return int(float(fuzzy[:-1]) * 1000)
        elif fuzzy[-1:] is 'm':
            return int(float(fuzzy[:-1]) * 1000000)
        return int(fuzzy)
    else:
        return None

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
        try:
            url = 'http://www.hackaday.io/project/' + str(project)
            f2 = open('had/' + str(project) + '.txt', 'w')
            response = urllib2.urlopen(url)
            html = response.read()
            f2.write(html)
            f2.close()
        except urllib2.HTTPError, e:
            print "---- begin fail ----"
            print e
            print url
            print "---- end fail ----"

        detailsPage = re.search(r'<a href="(/post/\d*)" class=".*">See all details', html, re.IGNORECASE)
        if detailsPage:
            try:
                url = 'http://www.hackaday.io' + detailsPage.group(1)
                f2 = open('had/' + str(project) + 'D.txt', 'w')
                response = urllib2.urlopen(url)
                html = response.read()
                f2.write(html)
                f2.close()
            except urllib2.HTTPError, e:
                print "---- begin fail ----"
                print e
                print url
                print "---- end fail ----"

        logPage = 1
        print
        while logPage < 10:
            url = 'http://www.hackaday.io/project/' + str(project) + '/logs?page=' + str(logPage)
            print url
            f2 = open('had/log/' + str(project) + 'L' + str(logPage) + '.txt', 'w')
            try:
                response = urllib2.urlopen(url)
                html = response.read()
                f2.write(html)
                f2.close()
                if re.search(r'<div class="section section-buildlogs last">\n\s*\n\s*There are no logs for this project\n\s*\n\s*</div>', html, re.IGNORECASE):
                    break;
            except urllib2.HTTPError, e:
                print "---- begin fail ----"
                print e
                print url
                print "---- end fail ----"
                break
            logPage += 1
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

    # PROCESS THE MAIN PROJECT PAGE

    f2 = open('had/' + str(project) + '.txt', 'r')
    projectRaw = f2.read()
    f2.close()
    licenses = re.findall(r'licen[sc]e', projectRaw, re.IGNORECASE)
    youtubes = re.findall(r'["\'](?:https://|http://|//|)(?:www\.|)youtu(?:be|)\.[a-z\.]{2,6}/.*?["\']', projectRaw, re.IGNORECASE)
    bestProductEntry = re.findall(r'<li><a href="/submissions/bestproduct/list">Best Product</a></li>', projectRaw, re.IGNORECASE)
    logScrape = re.search(r'View all (\d*) project logs', projectRaw, re.IGNORECASE)
    creationDate = re.search(r'<p class="project-time">[\n\s]*This project was[\n\s]*created on ([\d/]*)', projectRaw, re.IGNORECASE).group(1)
    if dataDump or tally:
        tags = re.findall(r'<a href="/projects/tag/(?:.*?)" class="tag.*?">(.*)</a>', projectRaw, re.IGNORECASE)
        tags = [tag.lower() for tag in tags]

    # comments, followers, skulls, views

    if dataDump:
        comments = len(re.findall(r'comment-\d{0,10}-content', projectRaw, re.IGNORECASE))
        commentsLogs = re.findall(r'\s*<a class="gray-link" href="/project/\d*/log/\d*#discussion-list">\n\s*(\d*) comments\n\s*</a>', projectRaw, re.IGNORECASE)
        for comment in commentsLogs:
            comments += int(comment)

        followerAmt = re.search(r'id="follower_count">(\d+[km]?)</span>', projectRaw).group(1)
        skullAmt = re.search(r'id="like_count">(\d+[km]?)</span>', projectRaw).group(1)
        try:
            viewAmt = re.search(r'<div class="section section-project-stats">\n.*\n.*title="View Count">(.*)</span>', projectRaw).group(1)
        except AttributeError:
            viewAmt = None

    # tags

    if tally:
        for tag in tags:
            if not tag in tagTally.keys():
                tagTally[tag] = 0
            tagTally[tag] += 1

    # log amount

    if logScrape is not None:
        if tally:
            if not int(logScrape.group(1)) in logTally.keys():
                logTally[int(logScrape.group(1))] = 0
            logTally[int(logScrape.group(1))] += 1
        projectLogAmount = int(logScrape.group(1))
    else:
        logScrape = re.search(r'View project log', projectRaw, re.IGNORECASE)
        if logScrape is not None:
            if tally:
                if not 1 in logTally.keys():
                    logTally[1] = 0
                logTally[1] += 1
            projectLogAmount = 1
        else:
            if tally:
                if not 0 in logTally.keys():
                    logTally[0] = 0
                logTally[0] += 1
            projectLogAmount = 0

    # PROCESS THE LOG PAGES

    logPages = glob.glob('had/log/' + str(project) + 'L*.txt')
    for logPage in logPages:
        f2 = open(logPage, 'r')
        logsRaw = f2.read()
        f2.close()
        licenses = list(licenses) + list(re.findall(r'licen[sc]e', logsRaw, re.IGNORECASE))
        youtubes = list(youtubes) + list(re.findall(
            r'["\'](?:https://|http://|//|)(?:www\.|)youtu(?:be|)\.[a-z\.]{2,6}/.*?["\']', logsRaw, re.IGNORECASE))

    # PROCESS THE DETAILS PAGE

    if os.path.isfile('had/' + str(project) + 'D.txt'):
        f2 = open('had/' + str(project) + 'D.txt')
        detailsRaw = f2.read()
        f2.close()
        licenses = list(licenses) + list(re.findall(r'licen[sc]e', detailsRaw, re.IGNORECASE))
        youtubes = list(youtubes) + list(re.findall(
            r'["\'](?:https://|http://|//|)(?:www\.|)youtu(?:be|)\.[a-z\.]{2,6}/.*?["\']', detailsRaw, re.IGNORECASE))

    # GET QUALIFICATIONS

    qualifiesQF = (projectLogAmount >= 4)# and (len(youtubes) >= 1)
    qualifiesBP = (projectLogAmount >= 8) and (len(bestProductEntry) > 0)# and (len(youtubes) >= 2)

    # Put projects into the qualifying lists if they might qualify
    if qualifiesQF:
        projectsQualifying.append(project)
    if qualifiesBP:
        projectsQualifyingBP.append(project)

    # Make sure no video links are counted twice
    youtubes = set(youtubes)

    if dataDump and dataDumpUseJSON:
        parsedData[int(project)] = {'tags': tags,
                'qual': {'quarterfinals': qualifiesQF, 'bestproduct-1': qualifiesBP},
                'logAmt': projectLogAmount,
                'followerAmt': fuzzyToNumber(followerAmt),
                'skullAmt': fuzzyToNumber(skullAmt),
                'viewAmt': fuzzyToNumber(viewAmt),
                'videoAmt': len(youtubes),
                'commentAmt': comments,
                'creationDate': creationDate};
    elif dataDump: # DIFFERENCES between JSON and tabbed file: JSON has tags.
        parsedData[int(project)] = \
            str(qualifiesQF) + "\t" +\
            str(qualifiesBP) + "\t" +\
            str(projectLogAmount) + "\t" +\
            str(fuzzyToNumber(followerAmt)) + "\t" +\
            str(fuzzyToNumber(skullAmt)) + "\t" +\
            str(fuzzyToNumber(viewAmt)) + "\t" +\
            str(len(youtubes)) + "\t" +\
            str(comments) + "\t" +\
            str(creationDate)

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
    print "Projects QUALIFYING BP - with at least 2 youtube videos and at least 8 logs:"
    print len(projectsQualifyingBP)
    print projectsQualifyingBP

if dataDump and dataDumpUseJSON:
    print json.dumps(parsedData)
elif dataDump:
    print "ID\tQF Qual\tBP Qual\tLogs\tFollowers\tSkulls\tViews\tYouTube Videos\tComments\tCreated"
    for key in sorted(parsedData.keys()):
        print str(key) + "\t" + parsedData[key]
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



MUST SCRAPE:
                                <span><a href="/post/13498" class="grey-gold-button medium-button show">See all details</a></span>
                    <a href="?page=2" class="grey-gold-button next-button show">Next</a>





'''