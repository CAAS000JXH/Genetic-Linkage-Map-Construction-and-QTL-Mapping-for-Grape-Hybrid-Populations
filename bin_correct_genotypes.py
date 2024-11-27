import csv
import sys
from collections import Counter

# 辅助函数：执行一轮校正
def perform_correction(data, window_size, max_differences, genotype_types):
    num_columns = len(data[0])  # 样品数
    corrected_data = [data[0]]  # 保留表头

    for row_index in range(1, len(data)):
        corrected_row = data[row_index][:2]  # 保留样本ID和位点ID
        for col_index in range(2, num_columns):
            genotype = data[row_index][col_index]
            # 仅对指定的基因型进行校正
            if genotype in genotype_types:
                # 选取当前样品的当前列
                group = [data[i][col_index] for i in range(max(0, row_index - window_size + 1), min(len(data), row_index + 1))]
                
                # 过滤掉缺失值（--）
                non_missing_genotypes = [g for g in group if g != '--']
                
                if len(non_missing_genotypes) > 0:
                    first_genotype = non_missing_genotypes[0]
                    last_genotype = non_missing_genotypes[-1]

                    # 仅当首尾基因型一致时才继续校正
                    if first_genotype == last_genotype:
                        # 统计每个基因型的出现次数
                        genotype_counts = Counter(non_missing_genotypes)
                        most_common_genotype, most_common_count = genotype_counts.most_common(1)[0]

                        # 如果不同基因型或缺失值数量小于等于max_differences，则进行校正
                        if len(non_missing_genotypes) - most_common_count <= max_differences:
                            corrected_row.append(most_common_genotype)
                        else:
                            corrected_row.append(data[row_index][col_index])
                    else:
                        corrected_row.append(data[row_index][col_index])
                else:
                    corrected_row.append('--')
            else:
                corrected_row.append(data[row_index][col_index])

        corrected_data.append(corrected_row)
    
    return corrected_data

# 主函数：处理所有染色体文件
def main(chromosome_file, parent_type):
    with open(chromosome_file, 'r') as chrom_file:
        chromosome_ids = chrom_file.read().splitlines()

    if parent_type == 'male':
        genotype_types = ['nn', 'np']
    elif parent_type == 'female':
        genotype_types = ['lm', 'll']
    else:
        raise ValueError("亲本类型只能是 'male' 或 'female'")

    for chrom_id in chromosome_ids:
        input_file = f'{chrom_id}.bins.genotype.{parent_type}.csv'
        output_file = f'{chrom_id}.bins.genotype.{parent_type}.correction.csv'

        # 读取输入文件
        with open(input_file, mode='r') as infile:
            reader = csv.reader(infile, delimiter=';')
            data = [row for row in reader]

        # 执行六轮校正
        for round_num, (window_size, max_differences) in enumerate([(5, 1), (7, 2), (9, 3), (11, 4), (13, 5), (15, 5)], start=1):
            data = perform_correction(data, window_size, max_differences, genotype_types)
            if round_num == 6:  # 仅在第六轮校正后输出结果
                with open(output_file, mode='w', newline='') as outfile:
                    writer = csv.writer(outfile, delimiter=';')
                    writer.writerows(data)
                print(f"第六轮校正完成，结果已保存至: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python correct_genotypes.py <chromosome_file> <parent_type>")
    else:
        chromosome_file = sys.argv[1]
        parent_type = sys.argv[2]
        main(chromosome_file, parent_type)
