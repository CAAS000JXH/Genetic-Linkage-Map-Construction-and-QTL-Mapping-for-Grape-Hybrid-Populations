import pysam
import sys
import os

def process_vcf(vcf_in_path, vcf_out_path, dp_threshold):
    # 判断输入文件是否是压缩文件，如果是则生成索引
    if vcf_in_path.endswith('.gz'):
        if not os.path.exists(vcf_in_path + '.tbi'):
            pysam.tabix_index(vcf_in_path, preset="vcf")

    # 打开输入VCF文件进行读取
    vcf_in = pysam.VariantFile(vcf_in_path, 'r')

    # 检查输出文件名，如果以'.gz'结尾，去除'.gz'后缀
    if vcf_out_path.endswith('.gz'):
        vcf_out_path = vcf_out_path[:-3]

    # 准备输出VCF文件
    vcf_out = pysam.VariantFile(vcf_out_path, 'w', header=vcf_in.header)

    # 遍历输入文件中的每个变异
    for record in vcf_in.fetch():
        for sample in record.samples:
            # 获取DP值
            dp = record.samples[sample]['DP']
            # 如果DP小于指定阈值，设置GT为缺失
            if dp is not None and dp < dp_threshold:
                record.samples[sample]['GT'] = (None, None)
        vcf_out.write(record)

    # 关闭VCF文件
    vcf_in.close()
    vcf_out.close()

if __name__ == "__main__":
    # 从命令行获取参数
    vcf_in_path = sys.argv[1]
    vcf_out_path = sys.argv[2]
    dp_threshold = int(sys.argv[3])

    # 处理VCF文件
    process_vcf(vcf_in_path, vcf_out_path, dp_threshold)
