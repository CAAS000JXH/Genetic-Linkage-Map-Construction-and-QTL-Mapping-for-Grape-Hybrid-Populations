import pandas as pd
import sys

def process_excel_to_qua(input_file, output_file, nind, ntrt):
    # 读取Excel文件
    df = pd.read_excel(input_file, engine='openpyxl')

    # 打开一个新文件，用于写入.qua文件内容
    with open(output_file, 'w') as file:
        # 写入表头信息
        file.write(f"nind= {nind}\n")
        file.write(f"ntrt= {ntrt}\n")
        file.write(f"miss=   *\n")
        
        # 获取并组合表头（从第二列开始直到最后一列）
        headers = df.columns[1:]  # 从第二列开始直到最后一列
        header_str = 'NR ' + ' '.join(headers)
        
        # 写入列名到文件
        file.write(header_str + '\n')
        
        # 遍历DataFrame的每一行
        for index, row in df.iterrows():
            # 获取样品ID
            sample_id = row['NR']
            
            # 获取所有表型数据列（从第二列开始）
            phenotype_data = row.iloc[1:]  # 从第二列开始直到最后一列
            
            # 将所有表型数据组合成一个字符串，用空格分隔
            phenotype_str = ' '.join(map(str, phenotype_data.values))
            
            # 组合.qua文件的一行内容
            qua_line = f"{sample_id} {phenotype_str}\n"
            
            # 写入文件
            file.write(qua_line)

    print(f"转换完成，生成的.qua文件已保存为{output_file}")

# 使用方式：process_excel_to_qua('input.xlsx', 'output.qua', 100, 10)
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <input_file.xlsx> <output_file.qua> <nind> <ntrt>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        nind = int(sys.argv[3])
        ntrt = int(sys.argv[4])
        process_excel_to_qua(input_file, output_file, nind, ntrt)

