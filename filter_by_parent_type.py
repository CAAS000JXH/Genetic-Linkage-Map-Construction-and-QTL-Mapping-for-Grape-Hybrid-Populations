import pandas as pd
import sys
import argparse

def filter_data(input_file, parent_type):
    """
    Filter genetic data based on parent type.
    """
    # 读取 CSV 文件
    data = pd.read_csv(input_file, sep=';', header=None, dtype=str)  # 确保所有数据都作为字符串读取

    # 根据父本类型选择适当的列
    if parent_type == 'male':
        # 父本条件过滤
        condition = data.iloc[:, 4].str[0] == data.iloc[:, 4].str[2]
        output_file = 'merged.variant.nnxnp.csv'
    elif parent_type == 'female':
        # 母本条件过滤
        condition = data.iloc[:, 5].str[0] == data.iloc[:, 5].str[2]
        output_file = 'merged.variant.lmxll.csv'
    else:
        print("Error: Invalid parent type. Choose 'male' or 'female'.")
        sys.exit(1)

    # 过滤数据
    filtered_data = data[condition].copy()

    # 去除基因型分隔符 '/' 和 '|'
    filtered_data = filtered_data.replace({'/': '', '\|': ''}, regex=True)  # 使用 '\|' 以避免误解为正则表达式中的 '或' 操作符

    # 将处理后的数据保存到最终的 CSV 文件
    filtered_data.to_csv(output_file, sep=';', header=None, index=False)
    print(f"Final filtered data saved to {output_file}")

if __name__ == "__main__":
    # 创建解析器
    parser = argparse.ArgumentParser(description='Filter genetic data based on parent type.')
    
    # 添加参数
    parser.add_argument('input_file', type=str, help='Path to the input CSV file containing genetic data.')
    parser.add_argument('parent_type', type=str, choices=['male', 'female'], help="Type of parent for filtering ('male' or 'female').")
    
    # 解析参数
    args = parser.parse_args()

    # 处理数据
    filter_data(args.input_file, args.parent_type)
