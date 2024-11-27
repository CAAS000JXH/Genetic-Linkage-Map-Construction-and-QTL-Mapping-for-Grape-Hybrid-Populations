import pandas as pd
import sys

def process_excel_to_map(input_file, output_file):
    # 读取输入文件的所有工作表，并将所有列都读取为字符串类型
    excel_data = pd.read_excel(input_file, sheet_name=None, dtype=str, engine='openpyxl')
    
    marker_count = 1

    with open(output_file, 'w') as file:
        # 遍历每一个工作表
        for sheet_name, sheet_data in excel_data.items():
            # 提取Locus和Position列
            if 'Locus' not in sheet_data.columns or 'Position' not in sheet_data.columns:
                print(f"工作表 '{sheet_name}' 缺少 'Locus' 或 'Position' 列。跳过该工作表。")
                continue
            
            # 写入组信息
            file.write(f"group {sheet_name}\n")
            
            # 只保留Locus和Position列，并去掉表头
            selected_data = sheet_data[['Locus', 'Position']].dropna()
            
            # 重命名第1列
            selected_data['Locus'] = [f"m{marker_count + i}" for i in range(len(selected_data))]
            marker_count += len(selected_data)
            
            # 按照Position列数值从小到大排序
            selected_data = selected_data.sort_values(by='Position', key=pd.to_numeric)
            
            # 将数据写入文件
            for index, row in selected_data.iterrows():
                file.write(f"{row['Locus']} {row['Position']}\n")

    print(f"转换完成，生成的.map文件已保存为{output_file}")

# 使用方式：process_excel_to_map('input.xlsx', 'output.map')
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python xlsx_to_map.py <input_file.xlsx> <output_file.map>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        process_excel_to_map(input_file, output_file)
