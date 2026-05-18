import os
import datetime
import json

subpagePaths = {'jeffHome.html': 'index.html', 'articles/jeffArticles.html': 'articles/index.html', 'about/jeffAbout.html': 'about/index.html'}
tokenPaths = {r'{jeffHeader}': 'header.html', r'{jeffFooter}': 'footer.html', r'{jeffArticleList}': 'articles/article_list.html', r'{jeffFeatured}': 'articles/featured.html'}

# add each article to the article path list
articlePaths = {}
for articleName in os.listdir('articles'):
    if os.path.isdir('articles/' + articleName):
        articleInputPath = 'articles/' + articleName + '/article.html'
        articleOutputPath = 'articles/' + articleName + '/index.html'
        articlePaths[articleInputPath] = articleOutputPath

class jeffArticle:
    def __init__(self, title, teaser, date, topic, colour, thumbnail, bodyText, outputPath):
        self.title = title
        self.teaser = teaser
        self.date = date
        self.topic = topic
        self.colour = colour
        self.thumbnail = thumbnail
        self.bodyText = bodyText
        self.outputPath = outputPath
    
    def replaceTokens(self, inputText):        
        return inputText.replace(r'{title}', self.title).replace(r'{teaser}', self.teaser).replace(r'{date}', datetime.date.fromordinal(self.date).strftime('%B %d, %Y')).replace(r'{topic}', self.topic).replace(r'{colour}', self.colour).replace(r'{thumbnail}', self.thumbnail).replace(r'{link}', self.outputPath.replace('index.html', ''))

# make outputPath-article dictionary
jeffArticles = {}
for articlePath in list(articlePaths.keys()):
    # read article text
    articleText = ''
    with open(articlePath, 'r', encoding='utf-8') as articleFile:
        articleText = articleFile.read()

    # read article details
    articlePreviewPath = articlePath.replace('article.html', 'article_details.json')
    articleMetadata = {}
    with open(articlePreviewPath, 'r', encoding='utf-8') as articleFile:
        articleDetails = json.load(articleFile)

        articleMetadata = articleDetails

        articleDate = datetime.date.fromisoformat(articleDetails['date'])
        articleMetadata['date'] = articleDate.toordinal()
    
    # replace title token
    articleText = articleText.replace(r'{title}', articleMetadata['title'])

    # fix thumbnail path
    jeffThumbnail = articlePath.replace('article.html', '').replace('articles/', '') + articleMetadata['thumbnail']

    # add article to dictionary
    jeffArticles[articlePaths[articlePath]] = jeffArticle(articleMetadata['title'], articleMetadata['teaser'], articleMetadata['date'], articleMetadata['topic'], articleMetadata['colour'], jeffThumbnail, articleText, articlePaths[articlePath])

# sort articlePaths by date
sortedArticles = sorted(list(jeffArticles.values()), key=lambda jeffArticle: jeffArticle.date, reverse=True)

# write article list and featured article
with open('articles/jeffArticlePreview.html', 'r', encoding='utf-8') as jeffArticleItem:
    # make replacements to preview
    jeffArticlePreviewTemplate = jeffArticleItem.read()
    jeffArticlePreviews = []
    for sortedArticle in sortedArticles[:9]:
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
    featuredArticle.thumbnail = 'articles/' + featuredArticle.thumbnail
    featuredArticleTemplate = jeffArticlePreviewTemplate.replace('jeffArticleListItem', 'jeffFeaturedArticle').replace('jeffArticleLink', 'jeffFeaturedArticleLink').replace('jeffTopicSmall', 'jeffTopic').replace('jeffArticleHeadingSmall', 'jeffFeaturedArticleHeading').replace('jeffDateSmall', 'jeffDateBig').replace('jeffArticleImageSmall', 'jeffFeaturedImageBig').replace('jeffSmallArticlePreview', 'jeffBigArticlePreview')
    featuredArticlePreview = featuredArticle.replaceTokens(featuredArticleTemplate)

    with open('articles/featured.html', 'w', encoding='utf-8') as jeffArticleFeaturedPreview:
        jeffArticleFeaturedPreview.write(featuredArticlePreview)

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

# make replacements
for pagePath in list(subpageTexts.keys()):
    for token in list(tokenTexts.keys()):
        subpageTexts[pagePath] = subpageTexts[pagePath].replace(token, tokenTexts[token])

# write output files
for pagePath in list(subpageTexts.keys()):
    with open(subpagePaths[pagePath], 'w', encoding='utf-8') as pageFile:
        pageFile.write(subpageTexts[pagePath])