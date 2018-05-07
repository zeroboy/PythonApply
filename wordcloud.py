#coding=utf-8

from collections import Counter  #计数
from wordcloud import WordCloud
import time
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt
import sys
import re
import jieba
import jieba.posseg as pseg #词性


def get_wordnum(filename):
    with open(filename) as f:
        words_box = []
        for line in f:
            lines = re.sub("\t", "", re.sub("\s", "", re.sub("\n", "", line)))
            words_box.extend(list(jieba.cut(lines, cut_all=True)))

    #print words_box
    words_box_counter = Counter(words_box)
    return words_box_counter



filename = "./txt/redfloor.txt"
wordnum = get_wordnum(filename)
wordnumdict = dict(wordnum)
dict= sorted(wordnumdict.items(), key=lambda c:c[1], reverse = True)
#print wordnum.items()
#sorted(wordnum.iteritems(), key=lambda wordnumtuple:wordnumtuple[1])

cut_text = ""
times = 0
for y in range(len(dict)):
    #print dict[y][0]+"-"+str(dict[y][1])
    #print dict[y][0].encode("utf8")
    once = re.findall(ur'[\u4e00-\u9fa5]{2,999}', dict[y][0])
    if once != []:
        #print once[0]+"-"+str(dict[y][1])
        words = pseg.cut(once[0])
        for w in words:
            if ((w.flag == "v") or (w.flag == "v")) and (times <100): #词性 n或nr 词频前100名
                print('%s %s %s' % (w.word, w.flag, dict[y][1]))
                print times
                cut_text += " "+dict[y][0]
                times += 1


#print cut_text
sys.exit()

#f = open(u'./22600.txt', 'r').read()
alice_coloring = np.array(Image.open("./alice_color.png"))

wordcloud = WordCloud(
    font_path='./font/HYQiHei-25J.ttf',
    background_color="white",
    width=600,
    height=1800,
    margin=2,
    #mask=alice_coloring,
    max_words=1000
).generate(cut_text)

# width,height,margin可以设置图片属性

# generate 可以对全部文本进行自动分词,但是他对中文支持不好,对中文的分词处理请看我的下一篇文章 
#wordcloud = WordCloud(font_path = r'D:\Fonts\simkai.ttf').generate(f)
# 你可以通过font_path参数来设置字体集

#background_color参数为设置背景颜色,默认颜色为黑色


plt.imshow(wordcloud)
plt.axis("off")
plt.show()

#wordcloud.to_file('test_wordcloud_'+str(int(time.time()))+'.png')
# 保存图片,但是在第三模块的例子中 图片大小将会按照 mask 保存


print len(alice_coloring)