import pandas as pd
import csv
import argparse

def filter_rows_by_type_ratio(df, start_col):
    df_copy = df.copy()
    
    ratios = []
    for index, row in df_copy.iterrows():
        type_counts = row[start_col:].value_counts()
        type_counts = type_counts.drop('..', errors='ignore')
        
        if len(type_counts) >= 2:
            max_count = type_counts.iloc[0]
            second_max_count = type_counts.iloc[1]
            ratio = max_count / second_max_count
            ratios.append(1 <= ratio <= 1.5)
        else:
            ratios.append(False)

    df_copy = df_copy[ratios]

    return df_copy

def count_dots_and_filter(input_file, start_col):
    # 读取CSV文件，不指定列名，直接使用位置索引
    df = pd.read_csv(input_file, sep=';', header=None, dtype=str)
    
    filtered_df = filter_rows_by_type_ratio(df, start_col)
    # 添加一列计算每行中包含'..'的数量
    filtered_df['dot_counts'] = filtered_df.iloc[:, start_col:].apply(lambda x: (x == '..').sum(), axis=1)
    return filtered_df

def sort_and_output(df, output_file):
    max_position = df.iloc[:, 1].astype(int).max()  # 使用索引1来代替列名'position'
    number_of_bins = (max_position - 5000) // 5000
    bins = [[] for _ in range(number_of_bins + 1)]
    
    for index, row in df.iterrows():
        position = int(row.iloc[1])  # 使用索引1来代替列名'position'
        dot_counts = int(row['dot_counts'])
        
        if 5000 <= position <= max_position:
            bin_index = (position - 5000) // 5000
            bins[bin_index].append((position, dot_counts, row))
    
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(df.columns)  # 写入表头
        for bin_data in bins:
            if len(bin_data) >= 5:
                bin_data.sort(key=lambda x: x[1])
                for data in bin_data[:5]:
                    writer.writerow(data[2].values)

def process_chromosomes(chromosome_file, parent_type):
    with open(chromosome_file, 'r') as file:
        chromosome_ids = file.read().splitlines()
    
    for chrom_id in chromosome_ids:
        input_file = f"{chrom_id}.merged.variant.{parent_type}.csv"
        output_file = f"{chrom_id}.MNP.range.{parent_type}.csv"

        print(f"Processing {input_file}...")

        filtered_df = count_dots_and_filter(input_file, start_col=6)
        sort_and_output(filtered_df, output_file)

        print(f"Output saved to {output_file}.")

def main():
    parser = argparse.ArgumentParser(description='Process chromosome data by type and filter criteria.')
    parser.add_argument('parent_type', type=str, choices=['male', 'female'], help='Parent type (male or female)')
    parser.add_argument('chromosome_file', type=str, help='Chromosome ID file (txt file with one chromosome ID per line)')
    
    args = parser.parse_args()

    process_chromosomes(args.chromosome_file, args.parent_type)

if __name__ == '__main__':
    main()
