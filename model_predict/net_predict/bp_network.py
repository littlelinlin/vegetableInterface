# coding: utf-8
# @author  : lin
# @time    : 19-3-11

import tensorflow as tf
import os
import time
import numpy as np
from config.network_config import bp_model_save_path, save_file_name, batch_size, \
    train_begin, train_end, test_begin, test_end, many_days, bp_train_times, output_size, bp_input_size

tf.reset_default_graph()
bp_graph = tf.Graph()


def mkdir(path):
    """
    创建文件夹
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def bp_network(x, keep_prob):
    """
    定义神经网络的结构
    :param x:
    :param keep_prob: 每次参与的神经元百分比
    :return:
    """
    with lstm_graph.as_default():
        w = tf.Variable(tf.truncated_normal([bp_input_size, 500], stddev=0.1))
        b = tf.Variable(tf.zeros([500]) + 0.1)
        re = tf.matmul(x, w) + b
        l1 = tf.nn.elu(re)  # 激活函数
        l1_drop = tf.nn.dropout(l1, keep_prob)  # keep_prob设为1则百分百的神经元工作,L1作为神经元的输出传入
        w2 = tf.Variable(tf.truncated_normal([500, 30], stddev=0.1))
        b2 = tf.Variable(tf.zeros([30]) + 0.1)
        re2 = tf.matmul(l1_drop, w2) + b2
        l2 = tf.nn.elu(re2)  # 激活函数
        l2_drop = tf.nn.dropout(l2, keep_prob)
        # w3 = tf.Variable(tf.truncated_normal([300, 30], stddev=0.1))
        # b3 = tf.Variable(tf.zeros([30]) + 0.1)
        # re3 = tf.matmul(l2_drop, w3) + b3
        # l3 = tf.nn.elu(re3)  # 激活函数
        # l3_drop = tf.nn.dropout(l3, keep_prob)
        w4 = tf.Variable(tf.random_normal([30, output_size], stddev=0.1))
        b4 = tf.Variable(tf.zeros([output_size]) + 0.1)
        prediction = tf.matmul(l2_drop, w4) + b4
        return prediction


def get_train_test_data(price_list):
    """
    得到训练和测试的数据
    :param price_list: 价格数组
    :return:
    """
    # 获取训练数据
    data_train = price_list[train_begin:train_end]
    train_x, train_y = [], []
    for i in range(len(data_train) - bp_input_size):
        x = data_train[i: i + bp_input_size]
        y = data_train[i + bp_input_size]
        train_x.append(x)
        train_y.append([y])
    n_batch = len(train_x) // batch_size  # 整除批次大小
    return n_batch, train_x, train_y


def train_process(price_list, path):
    """
    开始训练网络
    :param price_list: 价格数组
    :param path: 保存网络的路径
    :return:
    """
    x = tf.placeholder(tf.float32, [None, bp_input_size])
    y = tf.placeholder(tf.float32, [None, output_size])
    keep_prob = tf.placeholder(tf.float32)
    lf = tf.Variable(0.01, dtype=tf.float32)  # 学习率定义
    prediction = bp_network(x, keep_prob)  # 建立网络
    n_batch, train_x, train_y = get_train_test_data(price_list)
    # 交叉熵
    loss = tf.reduce_mean(tf.square(y - prediction))
    # 梯度下降法
    train_op = tf.train.AdamOptimizer(lf).minimize(loss)
    saver = tf.train.Saver()
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for epoch in range(bp_train_times):  # 迭代周期
            i = 0
            sess.run(tf.assign(lf, 0.01 * 0.95 ** epoch))  # 修改学习率，越来越小
            # 分批次出来，batch_xs和batch_ys为每次投入训练的数据
            for batch in range(n_batch):
                batch_xs = train_x[i: i + batch_size]
                batch_ys = train_y[i: i + batch_size]
                i = i + batch_size
                loss_, _ = sess.run([loss, train_op], feed_dict={x: batch_xs, y: batch_ys, keep_prob: 1})
            if epoch % 100 == 0:
                print(epoch, loss_)
        saver.save(sess, path)


def bp_train(price_list, veg_name):
    start_time = time.time()
    path = bp_model_save_path + veg_name
    mkdir(path)
    path += save_file_name
    train_process(price_list, path)
    end_time = time.time()
    print(veg_name + ' wastes time ', end_time - start_time, ' s')


def predict_process(price_list, path):
    """
    预测
    :param price_list: 价格数组
    :param path: 存放路径
    :return:
    """
    with lstm_graph.as_default():
        x = tf.placeholder(tf.float32, [None, bp_input_size])
        y = tf.placeholder(tf.float32, [None, output_size])
        keep_prob = tf.placeholder(tf.float32)
        lf = tf.Variable(0.01, dtype=tf.float32)  # 学习率定义
        prediction = bp_network(x, keep_prob)  # 建立网络
        saver = tf.train.Saver()
        predict_price = []
        # 交叉熵
        loss = tf.reduce_mean(tf.square(y - prediction))
        # 梯度下降法
        train_op = tf.train.AdamOptimizer(lf).minimize(loss)
        x_in = price_list
        with tf.Session() as sess:
            tf.get_variable_scope().reuse_variables()
            saver.restore(sess, path)
            for j in range(many_days):
                predict_y = sess.run(prediction, feed_dict={x: [x_in], keep_prob: 1})  # 要三维
                predict_price.append(round(float(predict_y[0][0]), 2))
                x_in = np.append(x_in[1:], predict_y[0][0])
        return predict_price
    

def bp_predict(price_list, veg_name):
    start_time = time.time()
    path = bp_model_save_path + veg_name + save_file_name
    predict_price = predict_process(price_list, path)
    end_time = time.time()
    print(veg_name + ' wastes time ', end_time - start_time, ' s')
    return predict_price


def get_test_data(price_list):
    """
    得到测试的数据
    :param price_list: 价格数组
    :return:
    """
    # 获取测试数据
    data_test = price_list[test_begin:test_end]
    test_x, test_y = [], []
    for i in range(len(data_test) - bp_input_size):
        if len(test_x) < len(data_test) - bp_input_size - many_days:
            x = data_test[i: i + bp_input_size]
            test_x.append(x)
        y = data_test[i + bp_input_size]
        test_y.append([y])
    return test_x, test_y


def get_accuracy_process(price_list, path):
    """
    得到准确率
    :param price_list: 价格数组
    :param path: 保存网络的路径
    :return:
    """
    x = tf.placeholder(tf.float32, [None, bp_input_size])
    y = tf.placeholder(tf.float32, [None, output_size])
    keep_prob = tf.placeholder(tf.float32)
    lf = tf.Variable(0.01, dtype=tf.float32)  # 学习率定义
    prediction = bp_network(x, keep_prob)  # 建立网络
    test_x, test_y = get_test_data(price_list)
    # 交叉熵
    loss = tf.reduce_mean(tf.square(y - prediction))
    # 梯度下降法
    train_op = tf.train.AdamOptimizer(lf).minimize(loss)
    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, path)
        bool_list_1 = []
        bool_list_5 = []
        bool_list_10 = []
        for step in range(len(test_x)):
            x_in = test_x[step]
            for j in range(many_days):
                predict_y = sess.run(prediction, feed_dict={x: [x_in], keep_prob: 1})  # 要三维
                predict_y = predict_y[0]
                origin_y = test_y[step + j]
                if j == many_days - 1:
                    # 获取其准确率
                    bool_list_1.append((abs(predict_y - origin_y) / origin_y < 0.01)[0])
                    bool_list_5.append((abs(predict_y - origin_y) / origin_y < 0.05)[0])
                    bool_list_10.append((abs(predict_y - origin_y) / origin_y < 0.1)[0])
                x_in = np.append(x_in[1:], predict_y)  # 将计算值添加进去
                # x = [[num] for num in x]
        # 误差小于1%的准确率
        # cast函数将其转换为float形式
        num_list = (tf.cast(bool_list_1, tf.float32))
        # reduce_mean取平均值，此时True为1，False为0，平均值其实就是准确率
        accuracy = tf.reduce_mean(num_list)
        acc_1 = sess.run(accuracy)
        num_list = (tf.cast(bool_list_5, tf.float32))
        accuracy = tf.reduce_mean(num_list)
        acc_5 = sess.run(accuracy)
        num_list = (tf.cast(bool_list_10, tf.float32))
        accuracy = tf.reduce_mean(num_list)
        acc_10 = sess.run(accuracy)
    print(acc_1, acc_5, acc_10)
    return acc_1, acc_5, acc_10


def bp_get_accuracy(price_list, veg_name):
    start_time = time.time()
    path = bp_model_save_path + veg_name
    mkdir(path)
    path += save_file_name
    acc_1, acc_5, acc_10 = get_accuracy_process(price_list, path)
    acc_data = {'acc_1': round(float(acc_1), 3), 'acc_5': round(float(acc_5), 3), 'acc_10': round(float(acc_10), 3)}
    end_time = time.time()
    print(veg_name + ' wastes time ', end_time - start_time, ' s')
    return {"data": acc_data}
