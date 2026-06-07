import json
import sys
import os

article_name = ''

if len(sys.argv) == 2:
    article_name = sys.argv[1]
else:
    print('Usage: py new_article.py "[article name]"')
    quit(1)

folder_name = article_name.lower().replace(' ', '_')

if os.path.isdir('articles/' + folder_name):
    print('ERROR: Article already exists.')
    quit(1)
else:
    os.mkdir('articles/' + folder_name)
    os.mkdir('articles/' + folder_name + '/images')

with open('articles/' + folder_name + '/article.jeml', 'w', encoding='utf-8') as articleFile:
    articleFile.write('\n\n[image_file]{source_link}(source_name){license}\n\n')

article_details = {'enabled': False, 'title': article_name, 'teaser': '', 'date': '', 'topic': '', 'thumbnail': ''}

with open('articles/' + folder_name + '/article_details.json', 'w', encoding='utf-8') as detailsFile:
    details_json = json.dump(article_details, detailsFile, indent='\t')