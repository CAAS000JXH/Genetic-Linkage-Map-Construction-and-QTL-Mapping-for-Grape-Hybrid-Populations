import csv
import argparse

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Split variant files based on chromosome prefixes.')
    parser.add_argument('parent_type', choices=['male', 'female'], help='Specify the parent type: "male" or "female".')
    args = parser.parse_args()

    # 读取染色体前缀
    with open('chromosome_ids.txt', 'r') as prefix_file:
        prefixes = [line.strip() for line in prefix_file if line.strip()]

    # 根据亲本类型决定输入文件和输出文件名
    input_filename = 'merged.variant.nnxnp.csv' if args.parent_type == 'male' else 'merged.variant.lmxll.csv'

    # 打开输入文件并读取数据行
    with open(input_filename, 'r') as input_file:
        # 读取数据行（假设没有表头）
        data_rows = input_file.readlines()

    # 遍历前缀列表，为每个前缀创建一个输出文件
    for prefix in prefixes:
        output_filename = f"{prefix}.merged.variant.{args.parent_type}.csv"
        with open(output_filename, 'w') as output_file:
            # 遍历数据行，写入以当前前缀开头的行
            for row in data_rows:
                if row.startswith(prefix):
                    output_file.write(row)

if __name__ == '__main__':
    main()
