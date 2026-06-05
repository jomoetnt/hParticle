import os
import datetime
import json
import re
import sys

DEBUG_MODE = True

if len(sys.argv) > 1:
    if sys.argv[1] == '--debug' or sys.argv[1] == '-d':
        if sys.argv[2] == 'true':
            DEBUG_MODE = True
        elif sys.argv[2] == 'false':
            DEBUG_MODE = False
        else:
            print('Invalid arguments. Debug mode must be either \'true\' or \'false\'.')
            quit()

PAGE_LIST_LENGTH = 5

topicColours = {'Physics and Astronomy': 'physics', 'Mathematics': 'mathematics', 'Biology': 'biology', 'Chemistry': 'chemistry', 'Computing': 'computing', 'Psychology and Psychiatry': 'psychology', 'Linguistics': 'linguistics', 'Philosophy': 'philosophy', 'Other': 'other'}

subpagePaths = {'jeffHome.html': 'index.html', 'articles/jeffArticles.html': 'articles/index.html', 'about/jeffAbout.html': 'about/index.html', 'announcements/jeffAnnouncements.html': 'announcements/index.html'}
tokenPaths = {r'{jeffHeader}': 'jeffHeader.html', r'{jeffFooter}': 'jeffFooter.html', r'{jeffArticleList}': 'articles/article_list.html', r'{jeffAnnouncementList}': 'announcements/announcement_list.html', r'{jeffFeaturedArticle}': 'articles/featured.html', r'{jeffFeaturedAnnouncement}': 'announcements/featured.html'}

licenseTypes = {'CC4': ('https://creativecommons.org/licenses/by-sa/4.0/deed.en', 'CC 4.0')}

# add each article to the article path list
articlePaths = {}
for articleName in os.listdir('articles'):
    if os.path.isdir('articles/' + articleName):
        if os.path.isfile('articles/' + articleName + '/article.jeml'):
            articleInputPath = 'articles/' + articleName + '/article.jeml'
            articleOutputPath = 'articles/' + articleName + '/index.html'
            articlePaths[articleInputPath] = articleOutputPath
        elif os.path.isfile('articles/' + articleName + '/jeffArticle.html'):
            articleInputPath = 'articles/' + articleName + '/jeffArticle.html'
            articleOutputPath = 'articles/' + articleName + '/index.html'
            articlePaths[articleInputPath] = articleOutputPath
        
# add each announcement to the announcement path list
announcementPaths = {}
for announcementName in os.listdir('announcements'):
    if os.path.isdir('announcements/' + announcementName):
        announcementInputPath = 'announcements/' + announcementName + '/jeffAnnouncement.html'
        announcementOutputPath = 'announcements/' + announcementName + '/index.html'
        announcementPaths[announcementInputPath] = announcementOutputPath

class jeffArticle:
    def __init__(self, enabled, title, teaser, date, topic, thumbnail, bodyText, outputPath):
        self.enabled = enabled
        self.title = title
        self.teaser = teaser
        self.date = date
        self.topic = topic
        self.thumbnail = thumbnail
        self.bodyText = bodyText
        self.outputPath = outputPath
    
    def replaceTokens(self, inputText):        
        return inputText.replace(r'{title}', self.title).replace(r'{teaser}', self.teaser).replace(r'{date}', datetime.date.fromordinal(self.date).strftime('%B %d, %Y')).replace(r'{topic}', self.topic).replace(r'{colour}', topicColours[self.topic]).replace(r'{thumbnail}', self.thumbnail).replace(r'{link}', self.outputPath.replace('index.html', ''))

class jeffAnnouncement:
    def __init__(self, title, date, bodyText, outputPath):
        self.title = title
        self.date = date
        self.bodyText = bodyText
        self.outputPath = outputPath
    
    def replaceTokens(self, inputText):        
        return inputText.replace(r'{title}', self.title).replace(r'{date}', datetime.date.fromordinal(self.date).strftime('%B %d, %Y')).replace(r'{link}', self.outputPath.replace('index.html', ''))

# turn jeml file into HTML article
def jemlToArticle(jemlText, metadata):
    articleBody = ''
    # read jeml line by line
    lines = jemlText.splitlines()
    skip_numbers = []
    for i in range(len(lines)):
        if i in skip_numbers:
            continue
        # skip empty lines
        if lines[i] == '':
            continue
        # level 2 heading
        elif lines[i].startswith('## '):
            heading2 = lines[i][3:]
            articleBody = articleBody + '<h2>{0}</h2>'.format(heading2)
        # level 3 heading
        elif lines[i].startswith('### '):
            heading3 = lines[i][4:]
            articleBody = articleBody + '<h3>{0}</h3>'.format(heading3)
        # image
        elif lines[i].startswith('['):
            imgSource = ''
            imgAttribution = ''
            # look for attributed image match
            imgAttrMatches = re.findall(r'\[(.*?)\]\{(.*?)\}\((.*?)\)\{(.*?)\}', lines[i], flags=re.DOTALL)
            if len(imgAttrMatches) == 1:
                # extract image source
                imgSource = imgAttrMatches[0][0]

                # extract attribution details
                imgAttrSrcLink = imgAttrMatches[0][1]
                imgAttrSrcName = imgAttrMatches[0][2]
                imgAttrLicense = imgAttrMatches[0][3]
                
                # construct image attribution
                imgAttribution = ' <div class="jeffAttribution"><a href="{0}">{1}</a>'.format(imgAttrSrcLink, imgAttrSrcName)

                # look up license name and link from ID
                if imgAttrLicense != '':
                    imgLicenseLink = licenseTypes[imgAttrLicense][0]
                    imgLicenseName = licenseTypes[imgAttrLicense][1]

                    imgLicense = '(<a href="{0}">{1}</a>)</div>'.format(imgLicenseLink, imgLicenseName)
                    imgAttribution = imgAttribution + ' ' + imgLicense
                else:
                    imgAttribution = imgAttribution + '</div>'
            else:
                # look for image match
                imgMatches = re.findall(r'\[(.*?)\]', lines[i], flags=re.DOTALL)
                # extract image source
                imgSource = imgMatches[0]
            # read image caption
            imgCaption = lines[i + 1]
            # skip line so it isn't also the next paragraph
            skip_numbers.append(i + 1)

            # get image template
            jeffImageTemplate = ''
            with open('articles/jeffImage.html', 'r', encoding='utf-8') as imageTemplateFile:
                jeffImageTemplate = imageTemplateFile.read()
            
            # construct image
            jeffImage = jeffImageTemplate.replace(r'{source}', 'images/' + imgSource).replace(r'{jeffAttribution}', imgAttribution).replace(r'{jeffCaption}', imgCaption)
            articleBody = articleBody + jeffImage
        # paragraph
        else:
            articleBody = articleBody + '<div class="jeffArticleParagraph">{0}</div>'.format(lines[i])
    
    # put article body in article template
    articleTemplateBody = ''
    with open('articles/jeffArticleTemplate.html', 'r', encoding='utf-8') as articleTemplateBodyFile:
        articleTemplateBody = articleTemplateBodyFile.read()

    outputText = articleTemplateBody.replace(r'{jeffArticle}', articleBody)

    return outputText

# make outputPath-article dictionary
jeffArticles = {}
for articlePath in list(articlePaths.keys()):
    # read jeml/html text
    jemlText = ''
    with open(articlePath, 'r', encoding='utf-8') as articleFile:
        jemlText = articleFile.read()

    legacy_article = False

    # set legacy mode and article metadata path
    articlePreviewPath = ''
    if articlePath.endswith('article.jeml'):
        articlePreviewPath = articlePath.replace('article.jeml', 'article_details.json')
    elif articlePath.endswith('jeffArticle.html'):
        articlePreviewPath = articlePath.replace('jeffArticle.html', 'article_details.json')
        legacy_article = True
    # read article details
    articleMetadata = {}
    with open(articlePreviewPath, 'r', encoding='utf-8') as articleFile:
        articleDetails = json.load(articleFile)

        articleMetadata = articleDetails

        articleDate = datetime.date.fromisoformat(articleDetails['date'])
        articleMetadata['date'] = articleDate.toordinal()

    articleText = jemlText
    # turn jeff markdown into HTML article
    if legacy_article == False:
        articleText = jemlToArticle(jemlText, articleMetadata)
    
    folderName = articlePath.replace('article.jeml', '').replace('jeffArticle.html', '').replace('articles/', '')

    # replace tokens in article itself
    articleText = articleText.replace(r'{title}', articleMetadata['title'])
    articleText = articleText.replace(r'{folder}', folderName)
    articleText = articleText.replace(r'{date}', datetime.date.fromordinal(articleMetadata['date']).strftime('%B %d, %Y'))
    articleText = articleText.replace(r'{teaser}', articleMetadata['teaser'])
    articleText = articleText.replace(r'{thumbnail}', articleMetadata['thumbnail'])

    # fix thumbnail path
    jeffThumbnail = folderName + articleMetadata['thumbnail']

    # add article to dictionary
    jeffArticles[articlePaths[articlePath]] = jeffArticle(articleMetadata['enabled'], articleMetadata['title'], articleMetadata['teaser'], articleMetadata['date'], articleMetadata['topic'], jeffThumbnail, articleText, articlePaths[articlePath])

# sort articlePaths by date
sortedArticles = sorted(list(jeffArticles.values()), key=lambda jeffArticle: jeffArticle.date, reverse=True)

# write article list and featured article
with open('articles/jeffArticlePreview.html', 'r', encoding='utf-8') as jeffArticleItem:
    # make replacements to preview
    jeffArticlePreviewTemplate = jeffArticleItem.read()
    jeffArticlePreviews = []
    for sortedArticle in sortedArticles:
        if sortedArticle.enabled == False and DEBUG_MODE == False:
            continue
        # remove 'articles/' in path
        sortedArticle.outputPath = sortedArticle.outputPath.replace('articles/', '')

        # replace tokens in article preview and add to list
        jeffArticlePreview = sortedArticle.replaceTokens(jeffArticlePreviewTemplate)
        jeffArticlePreviews.append(jeffArticlePreview)

        # put 'articles/' back
        sortedArticle.outputPath = 'articles/' + sortedArticle.outputPath
    
    # construct article list, separated into pages
    articleListPages = ''
    numPages = -(len(jeffArticlePreviews) // -PAGE_LIST_LENGTH)
    # combine previews
    for i in range(numPages):
        # get list of articles for page
        pagePreviews = jeffArticlePreviews[(i * PAGE_LIST_LENGTH):((i * PAGE_LIST_LENGTH) + PAGE_LIST_LENGTH)]
        # combine list
        combinedPreview = ''.join(pagePreviews)
        # wrap with div
        wrappedPreview = '<div class="jeffArticleListPage" id="page_{0}">{1}</div>'.format(i + 1, combinedPreview)
        # add to combined text
        articleListPages = articleListPages + wrappedPreview

    # write combined list to file
    with open('articles/article_list.html', 'w', encoding='utf-8') as jeffArticleList:
        jeffArticleList.write(articleListPages)
    
    # make featured article preview
    featuredArticle = sortedArticles[0]
    if sortedArticles[0].enabled == False and DEBUG_MODE == False:
        featuredArticle = sortedArticles[1]
    featuredArticle.thumbnail = 'articles/' + featuredArticle.thumbnail
    featuredArticleTemplate = jeffArticlePreviewTemplate.replace('jeffArticleListItem', 'jeffFeaturedArticle').replace('jeffArticleLink', 'jeffFeaturedArticleLink').replace('jeffTopicSmall', 'jeffTopic').replace('jeffArticleHeadingSmall', 'jeffFeaturedArticleHeading').replace('jeffDateSmall', 'jeffDateBig').replace('jeffArticleImageSmall', 'jeffFeaturedImageBig').replace('jeffSmallArticlePreview', 'jeffBigArticlePreview')
    featuredArticlePreview = featuredArticle.replaceTokens(featuredArticleTemplate)

    with open('articles/featured.html', 'w', encoding='utf-8') as jeffArticleFeaturedPreview:
        jeffArticleFeaturedPreview.write(featuredArticlePreview)

# make outputPath-announcement dictionary
jeffAnnouncements = {}
for announcementPath in list(announcementPaths.keys()):
    # read announcement text
    announcementText = ''
    with open(announcementPath, 'r', encoding='utf-8') as announcementFile:
        announcementText = announcementFile.read()

    # read announcement details
    announcementPreviewPath = announcementPath.replace('jeffAnnouncement.html', 'announcement_details.json')
    announcementMetadata = {}
    with open(announcementPreviewPath, 'r', encoding='utf-8') as announcementFile:
        announcementDetails = json.load(announcementFile)

        announcementMetadata = announcementDetails

        announcementDate = datetime.date.fromisoformat(announcementDetails['date'])
        announcementMetadata['date'] = announcementDate.toordinal()
    
    folderName = announcementPath.replace('jeffAnnouncement.html', '').replace('announcements/', '')

    # replace tokens in announcement itself
    announcementText = announcementText.replace(r'{title}', announcementMetadata['title'])
    announcementText = announcementText.replace(r'{folder}', folderName)
    announcementText = announcementText.replace(r'{date}', datetime.date.fromordinal(announcementMetadata['date']).strftime('%B %d, %Y'))

    # add announcement to dictionary
    jeffAnnouncements[announcementPaths[announcementPath]] = jeffAnnouncement(announcementMetadata['title'], announcementMetadata['date'], announcementText, announcementPaths[announcementPath])

# sort announcementPaths by date
sortedAnnouncements = sorted(list(jeffAnnouncements.values()), key=lambda jeffAnnouncement: jeffAnnouncement.date, reverse=True)

# write announcement list and featured announcement
with open('announcements/jeffAnnouncementPreview.html', 'r', encoding='utf-8') as jeffAnnouncementItem:
    # make replacements to preview
    jeffAnnouncementPreviewTemplate = jeffAnnouncementItem.read()
    jeffAnnouncementPreviews = []
    for sortedAnnouncement in sortedAnnouncements:
        # remove 'announcements/' in path
        sortedAnnouncement.outputPath = sortedAnnouncement.outputPath.replace('announcements/', '')

        # replace tokens in announcement preview and add to list
        jeffAnnouncementPreview = sortedAnnouncement.replaceTokens(jeffAnnouncementPreviewTemplate)
        jeffAnnouncementPreviews.append(jeffAnnouncementPreview)

        # put 'announcements/' back
        sortedAnnouncement.outputPath = 'announcements/' + sortedAnnouncement.outputPath
    
    # combine previews
    with open('announcements/announcement_list.html', 'w', encoding='utf-8') as jeffAnnouncementList:
        jeffAnnouncementList.write(''.join(jeffAnnouncementPreviews))
    
    # make featured announcement preview
    featuredAnnouncement = sortedAnnouncements[0]
    #featuredAnnouncementTemplate = jeffAnnouncementPreviewTemplate.replace('jeffArticleListItem', 'jeffFeaturedArticle').replace('jeffArticleLink', 'jeffFeaturedArticleLink').replace('jeffTopicSmall', 'jeffTopic').replace('jeffArticleHeadingSmall', 'jeffFeaturedArticleHeading').replace('jeffDateSmall', 'jeffDateBig').replace('jeffArticleImageSmall', 'jeffFeaturedImageBig').replace('jeffSmallArticlePreview', 'jeffBigArticlePreview')
    featuredAnnouncementTemplate = jeffAnnouncementPreviewTemplate
    featuredAnnouncementPreview = featuredAnnouncement.replaceTokens(featuredAnnouncementTemplate)

    with open('announcements/featured.html', 'w', encoding='utf-8') as jeffAnnouncementFeaturedPreview:
        jeffAnnouncementFeaturedPreview.write(featuredAnnouncementPreview)

# read special term template
termTemplate = ''
with open('articles/jeffTerm.html', 'r', encoding='utf-8') as termFile:
    termTemplate = termFile.read()

# read token files
tokenTexts = {}
for token in list(tokenPaths.keys()):
    with open(tokenPaths[token], 'r', encoding='utf-8') as tokenFile:
        tokenTexts[token] = tokenFile.read()

# read input files
subpageTexts = {}
for pagePath in list(subpagePaths.keys()):
    with open(pagePath, 'r', encoding='utf-8') as pageFile:
        subpageTexts[pagePath] = pageFile.read()

# add each article to the subpage dictionary
for articlePath in list(articlePaths.keys()):
    subpagePaths[articlePath] = articlePaths[articlePath]
    subpageTexts[articlePath] = jeffArticles[subpagePaths[articlePath]].bodyText

# add each announcement to the subpage dictionary
for announcementPath in list(announcementPaths.keys()):
    subpagePaths[announcementPath] = announcementPaths[announcementPath]
    subpageTexts[announcementPath] = jeffAnnouncements[subpagePaths[announcementPath]].bodyText

# make replacements 
for pagePath in list(subpageTexts.keys()):
    # replace static tokens
    for token in list(tokenTexts.keys()):
        subpageTexts[pagePath] = subpageTexts[pagePath].replace(token, tokenTexts[token])
    
    # replace escaped parentheses
    escapedText = subpageTexts[pagePath] = subpageTexts[pagePath].replace(r'\(', r'{LPAR}').replace(r'\)', r'{RPAR}')

    # replace special terms
    # find matches of [termText](termExplanation), returns an array of tuples (termText, termExplanation)
    termMatches = re.findall(r'\[(.*?)\]\((.*?)\)', escapedText, flags=re.DOTALL)
    for termMatch in termMatches:
        # extract termText and termExplanation from termMatch tuple
        termText = termMatch[0]
        termExplanation = termMatch[1]

        # recreate original '[termText](termExplanation)' match
        matchedExpression = '[{0}]({1})'.format(termText, termExplanation)

        # replace escaped tokens in explanation
        replacementExplanation = termExplanation.replace(r'{LPAR}', '(').replace(r'{RPAR}', ')')

        # replace tokens in term template
        jeffTerm = termTemplate.replace(r'{jeffTermText}', termText).replace(r'{jeffTermExplanation}', replacementExplanation)

        # replace special term pattern with HTML element
        subpageTexts[pagePath] = subpageTexts[pagePath].replace(matchedExpression, jeffTerm)
    
    # replace debug terms
    # find matches of {releaseValue}:{debugValue}
    debugMatches = re.findall(r'\{(.*?)\}:\{(.*?)\}', subpageTexts[pagePath], flags=re.DOTALL)
    for debugMatch in debugMatches:
        # extract releaseValue and debugValue from debugMatch tuple
        releaseValue = debugMatch[0]
        debugValue = debugMatch[1]

        # recreate original '{releaseValue}:{debugValue}' match
        matchedExpression = '{{{0}}}:{{{1}}}'.format(releaseValue, debugValue)

        # set replacement value
        debugReplacement = None
        if DEBUG_MODE == False:
            debugReplacement = releaseValue
        else:
            debugReplacement = debugValue
        
        # replace debug term
        subpageTexts[pagePath] = subpageTexts[pagePath].replace(matchedExpression, debugReplacement)

# write output files
for pagePath in list(subpageTexts.keys()):
    with open(subpagePaths[pagePath], 'w', encoding='utf-8') as pageFile:
        pageFile.write(subpageTexts[pagePath])