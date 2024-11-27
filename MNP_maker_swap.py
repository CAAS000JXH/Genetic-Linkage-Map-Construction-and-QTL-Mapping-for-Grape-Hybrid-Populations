import csv
import os

# 辅助函数：交换基因型
def swap_genotypes(row, parent_type):
    if parent_type == 'male':
        return ['nn' if val == 'np' else 'np' if val == 'nn' else val for val in row]
    elif parent_type == 'female':
        return ['lm' if val == 'll' else 'll' if val == 'lm' else val for val in row]
    return row

# 辅助函数：计算两行基因型的差异
def calculate_score(row1, row2):
    score = 0
    for a, b in zip(row1, row2):
        if a != b and a != '-' and b != '-':
            score += 1
    return score

# 第一步：相邻行逐行比较
def round1_process(data, parent_type):
    for i in range(1, len(data)):
        row_current = data[i][2:]  # 当前行
        row_previous = data[i - 1][2:]  # 前一行
        
        # 原始基因型和交换后的基因型
        original_row = row_current[:]
        swapped_row = swap_genotypes(row_current, parent_type)

        # 计算原始基因型与前一行的得分
        original_score = calculate_score(original_row, row_previous)
        swapped_score = calculate_score(swapped_row, row_previous)

        # 如果交换后的得分更低，使用交换后的基因型
        if swapped_score < original_score:
            data[i][2:] = swapped_row
    return data

# 第二步：三行一组进行比较
def round2_process(data, parent_type):
    for i in range(3, len(data), 3):
        if i + 3 > len(data):
            break
        
        block_current = data[i:i+3]  # 后三行
        block_previous = data[i-3:i]  # 前三行

        original_block = [row[2:] for row in block_current]  # 当前三行的原始值
        swapped_block = [swap_genotypes(row[2:], parent_type) for row in block_current]  # 当前三行的交换值

        # 计算原始值和交换值的得分
        original_score = sum(calculate_score(original_block[j], block_previous[j][2:]) for j in range(3))
        swapped_score = sum(calculate_score(swapped_block[j], block_previous[j][2:]) for j in range(3))

        # 如果交换得分更低，则使用交换值
        if swapped_score < original_score:
            for j in range(3):
                data[i+j][2:] = swapped_block[j]
    return data

# 主函数：处理文件的主要逻辑
def process_file(chrom_id, parent_type):
    input_file = f"{chrom_id}.MNP.genotype.filted.{parent_type}.csv"
    output_file = f"{chrom_id}.MNP.genotype.swap.{parent_type}.csv"

    if not os.path.exists(input_file):
        print(f"文件 {input_file} 不存在，跳过该染色体。")
        return

    with open(input_file, mode='r') as infile:
        reader = csv.reader(infile, delimiter=';')
        headers = next(reader)
        data = [row for row in reader]

    # 第一轮处理：相邻行的比较
    data = round1_process(data, parent_type)

    # 第二轮处理：三行一组的比较
    data = round2_process(data, parent_type)

    # 写入最终结果到输出文件
    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)

    print(f"处理完成，结果已保存至: {output_file}")

# 主函数：根据输入文件处理多个染色体
def main(chrom_id_file, parent_type):
    # 读取染色体ID
    with open(chrom_id_file, 'r') as f:
        chrom_ids = [line.strip() for line in f.readlines()]

    # 对每个染色体进行处理
    for chrom_id in chrom_ids:
        process_file(chrom_id, parent_type)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python swap.py <chrom_id_file> <parent_type>")
    else:
        chrom_id_file = sys.argv[1]
        parent_type = sys.argv[2]
        if parent_type not in ['male', 'female']:
            print("亲本类型应为 'male' 或 'female'")
        else:
            main(chrom_id_file, parent_type)
