import os
import datetime
import json

topicColours = {'Physics and Astronomy': 'physics', 'Mathematics': 'mathematics', 'Biology': 'biology', 'Chemistry': 'chemistry', 'Computing': 'computing', 'Psychology and Psychiatry': 'psychology', 'Linguistics': 'linguistics', 'Philosophy': 'philosophy'}

subpagePaths = {'jeffHome.html': 'index.html', 'articles/jeffArticles.html': 'articles/index.html', 'about/jeffAbout.html': 'about/index.html', 'announcements/jeffAnnouncements.html': 'announcements/index.html'}
tokenPaths = {r'{jeffHeader}': 'header.html', r'{jeffFooter}': 'footer.html', r'{jeffArticleList}': 'articles/article_list.html', r'{jeffAnnouncementList}': 'announcements/announcement_list.html', r'{jeffFeaturedArticle}': 'articles/featured.html', r'{jeffFeaturedAnnouncement}': 'announcements/featured.html'}

# add each article to the article path list
articlePaths = {}
for articleName in os.listdir('articles'):
    if os.path.isdir('articles/' + articleName):
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

# make outputPath-article dictionary
jeffArticles = {}
for articlePath in list(articlePaths.keys()):
    # read article text
    articleText = ''
    with open(articlePath, 'r', encoding='utf-8') as articleFile:
        articleText = articleFile.read()

    # read article details
    articlePreviewPath = articlePath.replace('jeffArticle.html', 'article_details.json')
    articleMetadata = {}
    with open(articlePreviewPath, 'r', encoding='utf-8') as articleFile:
        articleDetails = json.load(articleFile)

        articleMetadata = articleDetails

        articleDate = datetime.date.fromisoformat(articleDetails['date'])
        articleMetadata['date'] = articleDate.toordinal()
    
    # replace tokens in article itself
    articleText = articleText.replace(r'{title}', articleMetadata['title'])
    articleText = articleText.replace(r'{date}', datetime.date.fromordinal(articleMetadata['date']).strftime('%B %d, %Y'))
    articleText = articleText.replace(r'{teaser}', articleMetadata['teaser'])
    articleText = articleText.replace(r'{thumbnail}', articleMetadata['thumbnail'])

    # fix thumbnail path
    jeffThumbnail = articlePath.replace('jeffArticle.html', '').replace('articles/', '') + articleMetadata['thumbnail']

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
        if sortedArticle.enabled != True:
            continue
        # remove 'articles/' in path
        sortedArticle.outputPath = sortedArticle.outputPath.replace('articles/', '')

        # replace tokens in article preview and add to list
        jeffArticlePreview = sortedArticle.replaceTokens(jeffArticlePreviewTemplate)
        jeffArticlePreviews.append(jeffArticlePreview)

        # put 'articles/' back
        sortedArticle.outputPath = 'articles/' + sortedArticle.outputPath
    
    # combine previews
    with open('articles/article_list.html', 'w', encoding='utf-8') as jeffArticleList:
        jeffArticleList.write(''.join(jeffArticlePreviews))
    
    # make featured article preview
    featuredArticle = sortedArticles[0]
    if sortedArticles[0].enabled != True:
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
    
    # replace tokens in announcement itself
    announcementText = announcementText.replace(r'{title}', announcementMetadata['title'])
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
    for token in list(tokenTexts.keys()):
        subpageTexts[pagePath] = subpageTexts[pagePath].replace(token, tokenTexts[token])

# write output files
for pagePath in list(subpageTexts.keys()):
    with open(subpagePaths[pagePath], 'w', encoding='utf-8') as pageFile:
        pageFile.write(subpageTexts[pagePath])