# coding: utf-8
# @author  : lin
# @time    : 19-3-6


batch_size = 50  # 一次训练的批次大小
train_begin = 0  # 训练数据起始位置
train_end = 1000  # 训练数据结束位置
test_begin = 900  # 测试数据起始位置
test_end = 1310  # 测试数据结束位置
many_days = 10  # 滚动预测天数
time_step = 100  # lstm日数
bp_input_size = 100  # 输入一百个变量
bp_train_times = 501
lstm_rnn_unit1 = 100  # lstm网络隐藏第一层神经元个数
lstm_rnn_unit2 = 30  # lstm网络隐藏第二层神经元个数
lstm_input_size = 1  # 输入一个变量，即前一天的价格
lstm_train_times = 301  # 训练次数
output_size = 1  # 输出一个变量


bp_model_save_path = "model_predict/net_predict/network_save_predict/bp_net/"
lstm_model_save_path = "model_predict/net_predict/network_save_predict/lstm_net/"
save_file_name = '/veg'
