﻿# poemStyleAnalyse
### 一个神经网络的分类器，用来区分诗词的写作风格
* 采用爬虫爬取了10个tag的诗集作为风格的基准：['先秦', '汉魏', '六朝', '李白', '杜甫', '晚唐', '花间', '宋诗', '稼轩', '晚清']
* 总样本为1000，训练集占80%~90%左右，剩余都归到测试集与评估集中，对数据shuffle打乱的效果要好一些
* 最终准确率与召回率为71%左右，其中相邻时代的作品较容易混淆，年代久远的作品间区分度比较明显
* 测试了自己的几首诗作，感觉有些还挺合我意的，仅供参考娱乐：）