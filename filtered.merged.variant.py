import pandas as pd
import sys

def filter_csv(input_file, output_file, missing_threshold):
    # 读取 CSV 文件
    data = pd.read_csv(input_file, sep=',', dtype=str)

    # 根据条件删除行，计算每行第6列之后的缺失值个数，并与阈值进行比较
    data = data[~data.iloc[:, 6:].apply(lambda x: (x == './.').sum(), axis=1).gt(missing_threshold)]

    # 将结果保存到新的 CSV 文件
    data.to_csv(output_file, sep=',', index=False, header=False)

if __name__ == "__main__":
    # 从命令行获取参数
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    missing_threshold = int(sys.argv[3])

    # 过滤 CSV 文件
    filter_csv(input_file, output_file, missing_threshold)
