import re
from datetime import datetime
import pandas as pd
from solders.pubkey import Pubkey
import os
import glob

# 正则表达式用于匹配可能的Solana和ETH钱包地址
solana_address_pattern = r'[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{32,44}'
eth_address_pattern = r'0x[a-fA-F0-9]{40}'

# Solana地址验证函数
def validate_solana_address(address):
    try:
        Pubkey.from_string(address)
        return True
    except ValueError:
        return False

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 使用glob查找所有以.json结尾的文件
json_files = glob.glob(os.path.join(script_dir, '*.json'))

# 获取当前的年月日时分用于文件名
current_time = datetime.now().strftime('%Y%m%d%H%M')

# 创建“提取地址”文件夹的路径
extracted_folder = '提取地址'
if not os.path.exists(extracted_folder):
    os.makedirs(extracted_folder)

# 所有提取的地址和备注将添加到此列表
all_addresses = []

# 循环处理每个JSON文件
for file_path in json_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # 使用正则表达式找到所有可能的Solana钱包地址
        possible_solana_addresses = re.findall(solana_address_pattern, text)

        # 验证并提取有效的Solana钱包地址
        valid_solana_addresses = [
            addr for addr in possible_solana_addresses if validate_solana_address(addr)
        ]

        # 使用正则表达式找到所有匹配的ETH钱包地址
        eth_addresses = re.findall(eth_address_pattern, text)

        # 将提取的地址添加到总列表中
        all_addresses.extend(
            [{'Wallet Address': addr, 'Remarks': 'Solana'} for addr in valid_solana_addresses]
        )
        all_addresses.extend(
            [{'Wallet Address': addr, 'Remarks': 'Ethereum'} for addr in eth_addresses]
        )

    except FileNotFoundError:
        print(f"错误：文件未找到：{file_path}")
    except Exception as e:
        print(f"处理文件 {file_path} 时出错：{e}")

# 创建一个DataFrame
df = pd.DataFrame(all_addresses)

# 输出文件的名称，格式为原文件名+时间，并确保保存在“提取地址”文件夹中
output_file = os.path.join(extracted_folder, f'all_addresses_{current_time}.xlsx')

# 保存到Excel文件
df.to_excel(output_file, index=False)

print(f'所有提取的钱包地址已保存到 {output_file}')