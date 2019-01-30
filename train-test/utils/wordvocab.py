# coding : utf-8


from gensim.test.utils import get_tmpfile
from gensim.models import Word2Vec

path = './word2vec'
pathOut = path + '/' + 'word.vocab.txt'
pathModel = path + '/' + 'word2vec_zh.model'

fout = open(pathOut, 'w', encoding='utf-8')
fout.write('<PAD>\n')
vec_model = Word2Vec.load(pathModel)

num = 0
for word in vec_model.wv.vocab:
    num += 1
    fout.write(word+'\n')

print(num+2)
fout.close()
