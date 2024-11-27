#!/usr/bin/env python3

import argparse
import pysam
import os

def filter_vcf(vcf_in_path, vcf_out_path, male_id, female_id, DP):
    # 检查输入文件是否已经索引
    if vcf_in_path.endswith('.gz'):
        index_path = vcf_in_path + '.tbi'
        if not os.path.exists(index_path):
            pysam.tabix_index(vcf_in_path, preset='vcf', force=True)

    # 打开输入VCF文件
    vcf_in = pysam.VariantFile(vcf_in_path)

    # 如果输出路径以 '.gz' 结尾，将其替换为未压缩的文件名
    if vcf_out_path.endswith('.gz'):
        vcf_out_path = vcf_out_path[:-3]

    # 打开输出VCF文件，确保输出的是未压缩文件
    vcf_out = pysam.VariantFile(vcf_out_path, 'w', header=vcf_in.header)

    for rec in vcf_in.fetch():
        male_gt = rec.samples[male_id]['GT']
        male_dp = rec.samples[male_id].get('DP', -1)
        female_gt = rec.samples[female_id]['GT']
        female_dp = rec.samples[female_id].get('DP', -1)

        # 过滤掉带 '*' 的变异以及GT为缺失的样本
        if '*' in rec.alts or male_gt == (None, None) or female_gt == (None, None):
            continue

        # 过滤DP值低于阈值的样本
        if male_dp < DP or female_dp < DP:
            continue

        # 过滤掉父母都是同源合子的情况
        if male_gt in [(0,0), (1,1), (2,2)] and female_gt in [(0,0), (1,1), (2,2)]:
            continue

        vcf_out.write(rec)

    # 关闭输入输出VCF文件
    vcf_in.close()
    vcf_out.close()

def main():
    parser = argparse.ArgumentParser(description='Filter a VCF file based on certain criteria.')
    parser.add_argument('vcf_in', help='The input VCF file (can be compressed).')
    parser.add_argument('vcf_out', help='The output VCF file (will be uncompressed).')
    parser.add_argument('male_id', help='The ID of the male sample.')
    parser.add_argument('female_id', help='The ID of the female sample.')
    parser.add_argument('DP', type=int, help='The coverage depth threshold.')
    args = parser.parse_args()

    filter_vcf(args.vcf_in, args.vcf_out, args.male_id, args.female_id, args.DP)

if __name__ == '__main__':
    main()
