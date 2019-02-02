#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import time
from datetime import timedelta

import numpy as np
import tensorflow as tf
from sklearn import metrics

from cnn_model import TCNNConfig, TextCNN
from data.cnews_loader import read_vocab, read_category, batch_iter, process_file, build_vocab

base_dir = 'data/poemdata'

train_dir = os.path.join(base_dir, 'poems.train.txt')
test_dir = os.path.join(base_dir, 'poems.test.txt')
val_dir = os.path.join(base_dir, 'poems.val.txt')
vocab_dir = os.path.join(base_dir, 'poems.vocab.txt')


save_dir = 'checkpoints'           #模型文件的保存路径，建议多选备份模型
save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径


def get_time_dif(start_time):
    """获取已使用时间"""
    end_time = time.time()
    time_dif = end_time - start_time
    return timedelta(seconds=int(round(time_dif)))


def feed_data(x_batch, y_batch, keep_prob):
    feed_dict = {
        model.input_x: x_batch,
        model.input_y: y_batch,
        model.keep_prob: keep_prob
    }
    return feed_dict


def evaluate(sess, x_, y_):
    """评估在某一数据上的准确率和损失"""
    data_len = len(x_)
    batch_eval = batch_iter(x_, y_, 128)
    total_loss = 0.0
    total_acc = 0.0
    for x_batch, y_batch in batch_eval:
        batch_len = len(x_batch)
        feed_dict = feed_data(x_batch, y_batch, 1.0)
        loss, acc = sess.run([model.loss, model.acc], feed_dict=feed_dict)
        total_loss += loss * batch_len
        total_acc += acc * batch_len

    return total_loss / data_len, total_acc / data_len


def train():
    print("Configuring TensorBoard and Saver...")

    # 配置 Saver
    saver = tf.train.Saver()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print("Loading training and validation data...")
    # 载入训练集与验证集
    start_time = time.time()
    x_train, y_train = process_file(train_dir, word_to_id, cat_to_id, config.seq_length)
    x_val, y_val = process_file(val_dir, word_to_id, cat_to_id, config.seq_length)
    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)

    # 创建session
    session = tf.Session()
    session.run(tf.global_variables_initializer())
    # writer.add_graph(session.graph)

    print('Training and evaluating...')
    start_time = time.time()
    total_batch = 0  # 总批次
    best_acc_val = 0.0  # 最佳验证集准确率
    last_improved = 0  # 记录上一次提升批次
    require_improvement = 1500  # 如果超过1000轮未提升，提前结束训练

    flag = False
    for epoch in range(config.num_epochs):
        print('Epoch:', epoch + 1)
        batch_train = batch_iter(x_train, y_train, config.batch_size)
        for x_batch, y_batch in batch_train:
            feed_dict = feed_data(x_batch, y_batch, config.dropout_keep_prob)

            if total_batch % config.print_per_batch == 0:
                # 每多少轮次输出在训练集和验证集上的性能
                feed_dict[model.keep_prob] = 1.0
                loss_train, acc_train = session.run([model.loss, model.acc], feed_dict=feed_dict)
                loss_val, acc_val = evaluate(session, x_val, y_val)  # todo

                if acc_val > best_acc_val:
                    # 保存最好结果
                    best_acc_val = acc_val
                    last_improved = total_batch
                    saver.save(sess=session, save_path=save_path)
                    improved_str = '*'
                else:
                    improved_str = ''

                time_dif = get_time_dif(start_time)
                msg = 'Iter: {0:>6}, Train Loss: {1:>6.2}, Train Acc: {2:>7.2%},' \
                      + ' Val Loss: {3:>6.2}, Val Acc: {4:>7.2%}, Time: {5} {6}'
                print(msg.format(total_batch, loss_train, acc_train, loss_val, acc_val, time_dif, improved_str))

            session.run(model.optim, feed_dict=feed_dict)  # 运行优化
            total_batch += 1

            if total_batch - last_improved > require_improvement:
                # 验证集正确率长期不提升，提前结束训练
                print("No optimization for a long time, auto-stopping...")
                flag = True
                break  # 跳出循环
        if flag:  # 同上
            break


def test():
    print("Loading test data...")
    start_time = time.time()
    x_test, y_test = process_file(test_dir, word_to_id, cat_to_id, config.seq_length)

    session = tf.Session()
    session.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    saver.restore(sess=session, save_path=save_path)  # 读取保存的模型

    print('Testing...')
    loss_test, acc_test = evaluate(session, x_test, y_test)
    msg = 'Test Loss: {0:>6.2}, Test Acc: {1:>7.2%}'
    print(msg.format(loss_test, acc_test))

    batch_size = 128
    data_len = len(x_test)
    num_batch = int((data_len - 1) / batch_size) + 1

    y_test_cls = np.argmax(y_test, 1)
    y_pred_cls = np.zeros(shape=len(x_test), dtype=np.int32)  # 保存预测结果
    for i in range(num_batch):  # 逐批次处理
        start_id = i * batch_size
        end_id = min((i + 1) * batch_size, data_len)
        feed_dict = {
            model.input_x: x_test[start_id:end_id],
            model.keep_prob: 1.0
        }
        y_pred_cls[start_id:end_id] = session.run(model.y_pred_cls, feed_dict=feed_dict)

    # 评估
    print("Precision, Recall and F1-Score...")
    print(metrics.classification_report(y_test_cls, y_pred_cls, target_names=categories))

    # 混淆矩阵
    print("Confusion Matrix...")
    cm = metrics.confusion_matrix(y_test_cls, y_pred_cls)
    print(cm)

    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)

def Filter():
    pathList = [train_dir, val_dir]

    for path in pathList:
        x_test, y_test = process_file(path, word_to_id, cat_to_id, config.seq_length)

        session = tf.Session()
        session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess=session, save_path=save_path)  # 读取保存的模型

        print('Filtering...')
        loss_test, acc_test = evaluate(session, x_test, y_test)
        msg = 'Test Loss: {0:>6.2}, Test Acc: {1:>7.2%}'
        print(msg.format(loss_test, acc_test))

        batch_size = 128
        data_len = len(x_test)
        num_batch = int((data_len - 1) / batch_size) + 1

        y_test_cls = np.argmax(y_test, 1)
        y_pred_cls = np.zeros(shape=len(x_test), dtype=np.int32)  # 保存预测结果
        for i in range(num_batch):  # 逐批次处理
            start_id = i * batch_size
            end_id = min((i + 1) * batch_size, data_len)
            feed_dict = {
                model.input_x: x_test[start_id:end_id],
                model.keep_prob: 1.0
            }
            y_pred_cls[start_id:end_id] = session.run(model.y_pred_cls, feed_dict=feed_dict)
        nums = 0
        right_nums = 0
        path_new = path[:-4] + "_filter.txt"
        f_new = open(path_new, 'w', encoding='utf-8')
        with open(path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                try:
                    if y_test_cls[nums] == y_pred_cls[nums]:
                        f_new.write(line)
                        right_nums += 1
                    nums += 1
                except:
                    continue
        f_new.close()
        print("The numbers of all labels is: {}, The numbers of right labels is: {}".format(nums, right_nums))


def checkout():
    path = test_dir
    categories = ['先秦', '汉魏', '六朝', '李白', '杜甫', '晚唐', '花间', '宋诗', '稼轩', '晚清']

    x_test, y_test = process_file(path, word_to_id, cat_to_id, config.seq_length)

    session = tf.Session()
    session.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    saver.restore(sess=session, save_path=save_path)  # 读取保存的模型

    print('Filtering...')
    loss_test, acc_test = evaluate(session, x_test, y_test)
    msg = 'Test Loss: {0:>6.2}, Test Acc: {1:>7.2%}'
    print(msg.format(loss_test, acc_test))

    batch_size = 128
    data_len = len(x_test)
    num_batch = int((data_len - 1) / batch_size) + 1

    y_test_cls = np.argmax(y_test, 1)
    y_pred_cls = np.zeros(shape=len(x_test), dtype=np.int32)  # 保存预测结果
    for i in range(num_batch):  # 逐批次处理
        start_id = i * batch_size
        end_id = min((i + 1) * batch_size, data_len)
        feed_dict = {
            model.input_x: x_test[start_id:end_id],
            model.keep_prob: 1.0
        }
        y_pred_cls[start_id:end_id] = session.run(model.y_pred_cls, feed_dict=feed_dict)
    nums = 0
    wrong_nums = 0
    path_new = path[:-4] + "_checkout.txt"
    f_new = open(path_new, 'w', encoding='utf-8')
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            try:
                if y_test_cls[nums] != y_pred_cls[nums]:
                    line = line[:-2] + "\t" + "实际的标签是：{}  预测的标签是：{} \n".\
                        format(categories[y_test_cls[nums]], categories[y_pred_cls[nums]])
                    f_new.write(line)
                    wrong_nums += 1
                nums += 1
            except:
                continue
    f_new.close()
    print("The numbers of all labels is: {}, The numbers of wrong labels is: {}".format(nums, wrong_nums))


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ['train', 'test', 'filter', 'checkout']:
        raise ValueError("""usage: python run_cnn.py [train / test / Filter / checkout]""")

    print('Configuring CNN model...')
    config = TCNNConfig()
    if not os.path.exists(vocab_dir):  # 如果不存在词汇表，重建
        build_vocab(train_dir, vocab_dir, config.vocab_size)
    categories, cat_to_id = read_category()
    words, word_to_id = read_vocab(vocab_dir)
    config.vocab_size = len(words)
    model = TextCNN(config)

    if sys.argv[1] == 'train':
        train()
    elif sys.argv[1] == 'test':
        test()
    elif sys.argv[1] == 'filter':
        Filter()
    elif sys.argv[1] == 'checkout':
        checkout()
