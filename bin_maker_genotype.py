import argparse
import os
import pandas as pd
import numpy as np

def process_intervals(input_file, output_file, step_size, max_interval, parent_type):
    # 1. 读取输入文件，使用 `;` 作为分隔符
    data = pd.read_csv(input_file, sep=';')

    # 2. 建立区间
    intervals = list(range(0, max_interval + step_size, step_size))

    # 这里我们创建一个列表来保存结果
    results = []

    # 3. 遍历区间，处理数据
    for i in range(len(intervals) - 1):
        start = intervals[i]
        end = intervals[i + 1]
        
        # 选择在当前区间内的行
        mask = (data.iloc[:, 1] >= start) & (data.iloc[:, 1] < end)
        segment = data[mask]
        
        # 如果区间内没有数据，跳过该区间
        if segment.empty:
            continue
        
        # 初始化计数器
        count_1 = np.zeros(segment.shape[1] - 2)
        count_2 = np.zeros(segment.shape[1] - 2)
        
        # 4. 统计 nn 和 np 或 ll 和 lm 的个数
        for col in range(2, segment.shape[1]):
            if parent_type == 'male':
                count_1[col - 2] = (segment.iloc[:, col] == 'nn').sum()
                count_2[col - 2] = (segment.iloc[:, col] == 'np').sum()
            elif parent_type == 'female':
                count_1[col - 2] = (segment.iloc[:, col] == 'll').sum()
                count_2[col - 2] = (segment.iloc[:, col] == 'lm').sum()
        
        # 计算比例
        total_count = count_1 + count_2
        with np.errstate(divide='ignore', invalid='ignore'):
            ratio_1 = np.where(total_count != 0, count_1 / total_count, 0)
            ratio_2 = np.where(total_count != 0, count_2 / total_count, 0)
        
        # 5. 根据比例判断结果
        conditions = [
            ratio_1 >= 0.51,
            ratio_2 >= 0.51
        ]
        choices = ['nn' if parent_type == 'male' else 'll', 
                   'np' if parent_type == 'male' else 'lm']
        result = np.select(conditions, choices, default="--")
        
        # 将区间起始数值作为新的第一元素并加入结果
        interval_results = [start] + result.tolist()
        results.append(interval_results)

    # 6. 写入结果到 CSV 文件
    max_cols = max(len(r) for r in results)
    columns = ['Interval_Start'] + [f'Result_{i}' for i in range(1, max_cols)]
    result_df = pd.DataFrame(results, columns=columns)
    result_df.to_csv(output_file, index=False, sep=';')

    print(f'Results written to {output_file}')

def process_chromosomes(chrom_ids_file, parent_type, bin_size):
    with open(chrom_ids_file, mode='r') as infile:
        chrom_ids = [line.strip() for line in infile.readlines()]

    for chrom_id in chrom_ids:
        input_file = f"{chrom_id}.MNP.genotype.swap.{parent_type}.csv"
        output_file = f"{chrom_id}.bins.genotype.{parent_type}.csv"

        if not os.path.exists(input_file):
            print(f"文件 {input_file} 不存在，跳过该染色体。")
            continue

        # 读取数据文件获取最大区间
        data = pd.read_csv(input_file, sep=';')
        max_interval = data.iloc[:, 1].max()

        # 调用处理函数
        process_intervals(input_file, output_file, bin_size, max_interval, parent_type)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process genotype intervals from a CSV file and output results.")
    parser.add_argument('chrom_ids_file', type=str, help="Path to the text file containing chromosome IDs.")
    parser.add_argument('parent_type', type=str, choices=['male', 'female'], help="The parent type, either 'male' or 'female'.")
    parser.add_argument('bin_size', type=int, help="The bin size for interval processing.")
    
    args = parser.parse_args()
    process_chromosomes(args.chrom_ids_file, args.parent_type, args.bin_size)
