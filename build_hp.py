import os
import datetime

subpagePaths = {'jeffHome.html': 'index.html', 'articles/jeffArticles.html': 'articles/index.html'}
tokenPaths = {r'{jeffHeader}': 'header.html', r'{jeffFooter}': 'footer.html', r'{jeffArticleList}': 'articles/article_list.html'}

# add each article to the article path list
articlePaths = {}
for articleName in os.listdir('articles'):
    if os.path.isdir('articles/' + articleName):
        articleInputPath = 'articles/' + articleName + '/article.html'
        articleOutputPath = 'articles/' + articleName + '/index.html'
        articlePaths[articleInputPath] = articleOutputPath

# make inputPath-articleText dictionary and date-inputPath dictionary
articleTexts = {}
articleDates = {}
for articlePath in list(articlePaths.keys()):
    # extract date from first line and remove it from article text
    dateLine = ''
    articleText = ''
    with open(articlePath, 'r', encoding='utf-8') as articleFile:
        lines = articleFile.readlines()
        dateLine = lines[0].replace('\n', '')
        articleText = ''.join(lines[1:])
    articleTexts[articlePath] = articleText

    articleDate = datetime.date.fromisoformat(dateLine)
    articleDates[articleDate.toordinal()] = articlePath

# sort articlePaths by date
sortedArticlePaths = []
for articleDate in sorted(list(articleDates.keys()), reverse=True):
    sortedArticlePaths.append(articleDates[articleDate])

# read article previews
articlePreviewList = ''
for articlePath in sortedArticlePaths[:9]:
    articlePreviewPath = articlePath.replace('article.html', 'article_preview.html')
    with open(articlePreviewPath, 'r', encoding='utf-8') as articlePreviewText:
        articlePreviewList += articlePreviewText

# write article list
with open('articles/article_list.html', 'w', encoding='utf-8') as jeffArticleList:
    jeffArticleList.write(articlePreviewList)

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
for articlePath in list(articleTexts.keys()):
    subpagePaths[articlePath] = articleTexts[articlePath]

# make replacements
for pagePath in list(subpageTexts.keys()):
    for token in list(tokenTexts.keys()):
        subpageTexts[pagePath] = subpageTexts[pagePath].replace(token, tokenTexts[token])

# write output files
for pagePath in list(subpageTexts.keys()):
    with open(subpagePaths[pagePath], 'w', encoding='utf-8') as pageFile:
        pageFile.write(subpageTexts[pagePath])