import csv
import argparse
from collections import Counter, defaultdict
import ast

def process_step1(input_file, output_file):
    """Step 1: 处理CSV文件，重新结构化数据"""
    with open(input_file, mode='r', newline='') as infile, \
         open(output_file, mode='w', newline='') as outfile:

        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')

        headers = next(reader)
        columns_range = range(6, len(headers) - 1)

        new_headers = [headers[0], headers[1]] + headers[6:-1]
        writer.writerow(new_headers)

        group = []
        for row in reader:
            group.append(row)
            if len(group) == 5:
                first_column = set(r[0] for r in group).pop()
                second_column = min(int(r[1]) for r in group)
                remaining_columns = [','.join(r[i] for r in group) for i in columns_range]
                writer.writerow([first_column, second_column] + remaining_columns)
                group = []

        if group:
            first_column = set(r[0] for r in group).pop()
            second_column = min(int(r[1]) for r in group)
            remaining_columns = [','.join(r[i] for r in group) for i in columns_range]
            writer.writerow([first_column, second_column] + remaining_columns)

def process_step2(input_file, output_file):
    """Step 2: 统计每种类型的个数"""
    with open(input_file, mode='r', newline='') as infile, \
         open(output_file, mode='w', newline='') as outfile:

        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')

        headers = next(reader)
        writer.writerow(headers[:2] + ['Types'])

        for row in reader:
            data_columns = row[2:]
            types_counter = Counter(data_columns)
            types_str = ';'.join([f"{t}:{c}" for t, c in types_counter.items()])
            writer.writerow(row[:2] + [types_str])

def valid_types(type1, type2):
    """检查两种类型在相同位置上的数字是否都不同"""
    type1_points = type1.split(',')
    type2_points = type2.split(',')
    return all(p1 != p2 for p1, p2 in zip(type1_points, type2_points))

def process_step3(input_file, output_file, parent_type, offspring_count):
    """Step 3: 生成字典并根据条件写入输出文件"""
    threshold = offspring_count / 2  # 计算阈值为子代个数的一半

    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')

        headers = next(reader)
        writer.writerow(headers[:2] + ['Dictionary'])

        for row in reader:
            type_counts = row[2].split(';')
            count_dict = defaultdict(int)

            for type_count in type_counts:
                type, count = type_count.split(':')
                if '..' not in type:
                    count_dict[type] = int(count)

            sorted_types = sorted(count_dict, key=count_dict.get, reverse=True)
            top_types = []

            for i, type1 in enumerate(sorted_types):
                if len(top_types) == 2:
                    break
                for type2 in sorted_types[i+1:]:
                    if valid_types(type1, type2):
                        top_types.append(type1)
                        top_types.append(type2)
                        break

            if len(top_types) == 2:
                top_two_sum = sum(count_dict[typ] for typ in top_types)
                if top_two_sum > threshold:
                    if parent_type == 'male':
                        type_dict = {top_types[0]: 'nn', top_types[1]: 'np'}
                    else:
                        type_dict = {top_types[0]: 'lm', top_types[1]: 'll'}
                    writer.writerow(row[:2] + [str(type_dict)])

def fuzzy_match(s, pattern):
    """模糊匹配函数"""
    mismatches = sum(1 for a, b in zip(s, pattern) if a != b)
    return mismatches <= 2

def process_step4(input_file1, input_file2, output_file):
    """Step 4: 根据匹配条件生成最终输出文件"""
    output_rows = []

    pattern_dict = {}
    with open(input_file2, mode='r') as pattern_file:
        pattern_reader = csv.reader(pattern_file, delimiter=';')
        next(pattern_reader)
        for pattern_row in pattern_reader:
            key = pattern_row[1]
            pattern_dict[key] = ast.literal_eval(pattern_row[-1])

    with open(input_file1, mode='r') as input_file:
        input_reader = csv.reader(input_file, delimiter=';')
        input_headers = next(input_reader)
        output_headers = input_headers[:2] + input_headers[2:]
        output_rows.append(output_headers)

        for input_row in input_reader:
            key = input_row[1]
            if key in pattern_dict:
                output_row = input_row[:2]
                current_pattern_dict = pattern_dict[key]
                for value in input_row[2:]:
                    value_list = value.split(',')
                    found_match = False
                    for pattern, match in current_pattern_dict.items():
                        pattern_list = pattern.split(',')
                        if fuzzy_match(value_list, pattern_list):
                            output_row.append(match)
                            found_match = True
                            break
                    if not found_match:
                        output_row.append('--')
                output_rows.append(output_row)

    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerows(output_rows)

def process_chromosomes(chrom_ids_file, parent_type, offspring_count):
    with open(chrom_ids_file, mode='r') as infile:
        chrom_ids = [line.strip() for line in infile.readlines()]

    for chrom_id in chrom_ids:
        input_file1 = f"{chrom_id}.MNP.range.{parent_type}.csv"
        step1_output = f"{chrom_id}.step1.csv"
        step2_output = f"{chrom_id}.step2.csv"
        step3_output = f"{chrom_id}.step3.csv"
        final_output = f"{chrom_id}.MNP.genotype.{parent_type}.csv"

        # Step 1
        process_step1(input_file1, step1_output)

        # Step 2
        process_step2(step1_output, step2_output)

        # Step 3
        process_step3(step2_output, step3_output, parent_type, offspring_count)

        # Step 4
        process_step4(step1_output, step3_output, final_output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process chromosome data files for MNP genotype.")
    parser.add_argument('chrom_ids_file', type=str, help="Path to the text file containing chromosome IDs.")
    parser.add_argument('parent_type', type=str, choices=['male', 'female'], help="Parent type: 'male' or 'female'.")
    parser.add_argument('offspring_count', type=int, help="The number of offspring.")

    args = parser.parse_args()
    process_chromosomes(args.chrom_ids_file, args.parent_type, args.offspring_count)
