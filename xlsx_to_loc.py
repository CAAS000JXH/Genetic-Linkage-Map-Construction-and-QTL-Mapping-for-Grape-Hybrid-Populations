import pandas as pd
import sys

def process_excel_to_loc(input_file, output_file):
    # 读取输入文件的所有工作表，并将所有列都读取为字符串类型
    excel_data = pd.read_excel(input_file, sheet_name=None, dtype=str, engine='openpyxl')
    
    # 初始化一个空的DataFrame，用于存储合并后的数据
    combined_data = pd.DataFrame()

    # 遍历每一个工作表
    for sheet_name, sheet_data in excel_data.items():
        # 取第1列以及从第3列到最后非空列
        selected_columns = sheet_data.iloc[:, [0] + list(range(2, sheet_data.shape[1]))]
        # 合并到总的DataFrame中
        combined_data = pd.concat([combined_data, selected_columns], ignore_index=True)

    # 统计非空的总行数
    nloc = combined_data.shape[0]
    
    # 重命名第1列
    combined_data.iloc[:, 0] = ['m' + str(i + 1) for i in range(nloc)]
    
    # 替换值
    combined_data = combined_data.replace({'nn': 'a', 'np': 'h'})
    
    # 统计非空的列数（去掉表头第一列后的其他所有列）
    nind = combined_data.shape[1] - 1  # 减去第一列
    
    # 生成.loc文件内容
    with open(output_file, 'w') as file:
        # 写入表头
        file.write(f"name = population\n")
        file.write(f"popt = BC1\n")
        file.write(f"nloc = {nloc}\n")
        file.write(f"nind = {nind}\n")
        
        # 写入数据
        for index, row in combined_data.iterrows():
            line = ' '.join(map(str, row.values))
            file.write(line + '\n')

    print(f"转换完成，生成的.loc文件已保存为{output_file}")

# 使用方式：process_excel_to_loc('input.xlsx', 'output.loc')
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file.xlsx> <output_file.loc>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        process_excel_to_loc(input_file, output_file)
