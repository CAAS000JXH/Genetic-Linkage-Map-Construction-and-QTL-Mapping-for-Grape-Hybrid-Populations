import argparse
import pandas as pd
from scipy.stats import chi2

# 定义一个函数来计算ll、lm的个数
def count_genotypes(row, parent_type):
    if parent_type == 'male':
        nn_count = row.str.count('nn').sum()
        np_count = row.str.count('np').sum()
        return nn_count, np_count
    elif parent_type == 'female':
        ll_count = row.str.count('ll').sum()
        lm_count = row.str.count('lm').sum()
        return ll_count, lm_count
    return 0, 0

# 自由度为1的卡方检验函数
def chi_square_test_1(count1, count2):
    total = count1 + count2
    if total == 0:
        return None  # 当总数为0时，没有足够的数据进行测试
    exp1 = 0.5 * total
    exp2 = 0.5 * total

    chi2_statistic = (count1 - exp1)**2 / exp1 + (count2 - exp2)**2 / exp2
    p_value = 1 - chi2.cdf(chi2_statistic, df=1)

    return p_value

def process_data(input_file, output_file, parent_type, threshold):
    # 读取CSV文件，假设第一行是表头，所以不设置header=None
    df = pd.read_csv(input_file, sep=';')

    # 应用函数并添加新列
    counts = df.apply(lambda row: count_genotypes(row, parent_type), axis=1)
    df[['count1', 'count2']] = pd.DataFrame(counts.tolist(), index=df.index)
    df['dots_count'] = df.apply(lambda row: row.str.count('--').sum(), axis=1)

    # 过滤掉--个数大于等于阈值的行，并创建一个新的DataFrame的拷贝
    df_filtered = df[df['dots_count'] < threshold].copy()

    # 对剩余的行应用卡方检验，添加p-value列
    df_filtered['p_value'] = df_filtered.apply(lambda row: chi_square_test_1(row['count1'], row['count2']), axis=1)

    # 过滤出p-value > 0.01的行
    final_df = df_filtered[df_filtered['p_value'] > 0.01]

    # 输出到文件，保留表头
    final_df.to_csv(output_file, index=False, sep=';')

    print(f"染色体 {input_file} 处理完成，结果已保存至: {output_file}")

def process_chromosomes(chrom_ids_file, parent_type, offspring_count):
    with open(chrom_ids_file, mode='r') as infile:
        chrom_ids = [line.strip() for line in infile.readlines()]

    threshold = int(offspring_count * 0.25)

    for chrom_id in chrom_ids:
        input_file = f"{chrom_id}.MNP.genotype.{parent_type}.csv"
        output_file = f"{chrom_id}.MNP.genotype.filted.{parent_type}.csv"

        # 处理每个染色体的文件
        process_data(input_file, output_file, parent_type, threshold)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter CSV files based on genotype counts and chi-square test with p-value > 0.01.")
    parser.add_argument('chrom_ids_file', type=str, help="Path to the text file containing chromosome IDs.")
    parser.add_argument('parent_type', type=str, choices=['male', 'female'], help="Parent type: 'male' or 'female'.")
    parser.add_argument('offspring_count', type=int, help="The number of offspring.")

    args = parser.parse_args()
    process_chromosomes(args.chrom_ids_file, args.parent_type, args.offspring_count)
