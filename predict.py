# coding: utf-8

from __future__ import print_function

import os
import tensorflow as tf
import tensorflow.contrib.keras as kr

from cnn_model import TCNNConfig, TextCNN
from data.cnews_loader import read_category, read_vocab
import matplotlib.pyplot as plt

try:
    bool(type(unicode))
except NameError:
    unicode = str

base_dir = 'data/poemdata'
vocab_dir = os.path.join(base_dir, 'cnews.vocab.txt')

save_dir = 'checkpoints'  #模型文件的保存路径，建议多选备份模型
save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径

def piePlot(title, data, result):
	'''根据结果绘制饼图'''
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    labels = []
    sizes = []
    for i in data:
        labels.append(i[0])
        sizes.append(i[1])

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=False, startangle=150)
    title = "《{}》的风格当属于：{}".format(title, result)
    plt.title(title, color='red')
    plt.axis('equal')  # 该行代码使饼图长宽相等
    plt.show()

class CnnModel:
    def __init__(self):
        self.config = TCNNConfig()
        self.categories, self.cat_to_id = read_category()
        self.words, self.word_to_id = read_vocab(vocab_dir)
        self.config.vocab_size = len(self.words)
        self.model = TextCNN(self.config)

        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess=self.session, save_path=save_path)  # 读取保存的模型

    def predict(self, title, message):
        content = unicode(message)
        data = [self.word_to_id[x] for x in content if x in self.word_to_id]

        feed_dict = {
            self.model.input_x: kr.preprocessing.sequence.pad_sequences([data], self.config.seq_length),
            self.model.keep_prob: 1.0
        }

        result = self.categories[self.session.run(self.model.y_pred_cls, feed_dict=feed_dict)[0]]
        y_pred = [round(100*x, 2) for x in self.session.run(self.model.softmax, feed_dict=feed_dict)[0]]
        data = sorted([[self.categories[i], y_pred[i]] for i in range(len(self.categories))], key=lambda x:x[1], reverse=True)
        count = 0
        for i in range(len(data)):
            if data[count][1] < 1:
                data[0][1] = round(data[0][1]+data[count][1], 2)
                data.pop(count)
            else:
                count += 1
        print("data", data)
        piePlot(title, data, result)

if __name__ == '__main__':
    cnn_model = CnnModel()
    title = "浣溪沙·七夕"
    content = "遥望长风万里青，重山遮断雾回萦。何来乌鹊落轻盈。驿路云深歌碧月，高台风冷数繁星。梦见飞花梦见卿。"
    cnn_model.predict(title, content)
