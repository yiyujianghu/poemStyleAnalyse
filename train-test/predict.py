# coding: utf-8

from __future__ import print_function

import os
import tensorflow as tf
import tensorflow.contrib.keras as kr

from cnn_model import TCNNConfig, TextCNN
from data.cnews_loader import read_category, read_vocab

try:
    bool(type(unicode))
except NameError:
    unicode = str

base_dir = 'data/goodbad_content_555w'
vocab_dir = os.path.join(base_dir, 'cnews.vocab.txt')

save_dir = 'checkpoints/textcnn/goodbad_content_555w'  #模型文件的保存路径，建议多选备份模型
save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径


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

    def predict(self, message):
        # 支持不论在python2还是python3下训练的模型都可以在2或者3的环境下运行
        content = unicode(message)
        data = [self.word_to_id[x] for x in content if x in self.word_to_id]

        feed_dict = {
            self.model.input_x: kr.preprocessing.sequence.pad_sequences([data], self.config.seq_length),
            self.model.keep_prob: 1.0
        }

        y_pred_cls = self.session.run(self.model.y_pred_cls, feed_dict=feed_dict)
        y_pred = self.session.run(self.model.softmax, feed_dict=feed_dict)
        # return "情绪判断为 {0}：{1}， {2}：{3}，{4}：{5}".format(self.categories[0], y_pred[0][0],
        #                                        self.categories[1], y_pred[0][1],
        #                                        self.categories[2], y_pred[0][2]), self.categories[y_pred_cls[0]]
        return self.categories[y_pred_cls[0]]


if __name__ == '__main__':
    # cnn_model = CnnModel()
    # test_demo = ['12月26日,泰尔重工控股股东邰正彪与南京增材制造研究院发展有限公司(下称“增材院”)举办股权转让仪式,邰正彪设立的投资公司正式成为南京增材院的控股股东,其表示,要打造中国增材制造(3D打印)最强劲的研发基地。据悉,南京增材院由国内3D打印领军人物卢秉恒担任院长,2013年设立,注册资金1亿元,目前专职研发人员达80余人。邰正彪在仪式上表示,泰尔重工始终谋划战略转型,此次其本人控股南京增材院,将参照德国“弗劳恩霍夫应用技术研究院”的模式运营,开展“3D打印技术、装备及应用”的科学研究并进行相关产业化技术研究,力争建设成为中国增材制造领域最强的研究基地,并向社会持续不断地输送高质量的3D打印技术人才。据透露,除控股南京增材院,邰正彪还通过多个投资公司布局六臂机器人、外骨骼装甲等多项前沿技术。',
    #              '香港文汇报讯恒发洋参(0911)昨日宣布,於本月13日,公司与潜在投资者订立谅解备忘录。潜在投资者拟透过其控制之公司认购不少於280亿股认购股份,代价约为2.8亿元,每股认购股份0.01元。该股今日复牌。该股停牌前报0.074元,即是次配售价折让达86%。可能认购事项落实後,将导致潜在投资者持有公司经认购股份扩大之已发行股本约58.3%,因而令公司之控制权有所变更。潜在投资者根据谅解备忘录拟发行认购股份而导致收购守则第26.1条项下之强制性全面要约责任,向执行人员申请清洗豁免。根据谅解备忘录,潜在投资者已获授予自谅解备忘录日期起计90日的排他期。',
    #              '网易财经1月23日讯中国一重1月23日公告称,预计2016年度全年归属于中国一重股东的净利润亏损57.04亿元左右。网易财经查阅财报发现中国一重2015年净利润亏损17.95亿元,2016年亏损将比2015年大幅增加。中国一重股票将在中国一重2016年度报告披露后被实施退市风险警示(在中国一重股票简称前冠以“*ST”字样)公告披露本期业绩预亏的主要原因有以下四方面:一是受市场低迷的持续影响,前期中国一重订单不足,造成2016年产品销售收入大幅下滑。2015年新增订货52亿元、2016年上半年新增订货16.5亿元,2016年下半年中国一重采取切实有效措施加大市场开发力度,全年新增订货81.2亿元,但由于中国一重产品生产周期一般在一年半以上,新增订货未能在2016年形成产品销售收入。二是虽然中国一重应收账款大幅下降,但因受部分应收账款账龄增加影响,补提了部分坏账准备。三是中国一重实施扭亏脱困攻坚,开展瘦身健体工作,对低效、无效资产进行了集中清理,使中国一重资产得以夯实,同时依照《会计准则》,本年计提了资产减值。四是为加快货款清收,中国一重积极与用户协商,加快解决用户提出的质量异议,使得中国一重本年度产品三包和预计质量损失有所增加。']
    # for i in test_demo:
    #     print(cnn_model.predict(i))

    '''
    数据蒸馏算法: 先用整体数据做训练，得到模型后将所有的数据重新做训练，把分错的数据去掉，再扔进分类器里做训练
                尝试是否能提高测试的准确率，应采用爬虫爬到的较公平的数据集做训练
                后续可尝试打分蒸馏，将判定概率较大的数据保留，模棱两可的数据去掉
    '''
    cnn_model = CnnModel()
    base_dir = 'data/goodbad_content_555w'
    train_dir = os.path.join(base_dir, 'cnews.train.txt')
    test_dir = os.path.join(base_dir, 'cnews.test.txt')
    val_dir = os.path.join(base_dir, 'cnews.val.txt')
    vocab_dir = os.path.join(base_dir, 'cnews.vocab.txt')
    for path in [train_dir, val_dir, test_dir]:
        if "train" in path:
            data_type = "训练"
        elif "test" in path:
            data_type = "测试"
        elif "val" in path:
            data_type = "评估"
        else:
            data_type = "未知"
        print("<{}>数据集的清洗结果：".format(data_type))
        right_nums = 0
        wrong_nums = 0
        try:
            with open(path, 'r', encoding='utf-8') as f:
                new_path = path[:-4] + "_new.txt"
                f_test_new = open(new_path, 'w', encoding='utf-8')
                for line in f.readlines():
                    try:
                        label, content = line.strip().split('\t')
                    except:
                        continue                      
                    content_new = content * (1 + 1500//len(content))
                    pred = cnn_model.predict(content_new)
                    if label == pred:
                        f_test_new.write(line)
                        right_nums += 1
                    else:
                        wrong_nums += 1
                print("<{}>数据集，正确样本的数量是：{}，错误样本的数量是：{}，正确率为：{}".format(data_type,right_nums, wrong_nums, right_nums/(right_nums+wrong_nums)))
                f_test_new.close()
        except:
            print("目前错误在第{}行".format(right_nums+wrong_nums))
