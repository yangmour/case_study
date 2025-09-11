import csv
import os
import requests
import urllib.parse
import hashlib


# 创建存储下载文件的目录
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# 从 URL 下载文件
def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"下载成功: {save_path}")
        else:
            print(f"下载失败: {url} (状态码: {response.status_code})")
    except Exception as e:
        print(f"下载 {url} 时出错: {str(e)}")


# 提取 URL 中的路径部分并构造本地路径，保留大小写
def get_path_from_url(url, base_dir):
    parsed_url = urllib.parse.urlparse(url)
    # 提取路径并移除文件名，保留原始大小写
    path = os.path.dirname(parsed_url.path).lstrip('/')
    # 计算路径的哈希值，用于区分大小写不同的路径
    path_hash = hashlib.md5(path.encode('utf-8')).hexdigest()[:8]
    # 构造本地目录，添加哈希值作为标识
    local_path = os.path.join(base_dir, path + f"_hash_{path_hash}")
    # 获取文件名
    filename = os.path.basename(parsed_url.path)
    if not filename:
        # 如果没有文件名，生成默认文件名
        filename = f"file_{hash(url) % 1000000}"
        # 尝试从 Content-Disposition 获取文件名
        try:
            response = requests.head(url, allow_redirects=True)
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                import re
                fname = re.findall('filename="(.+)"', content_disposition)
                if fname:
                    filename = fname[0]
        except:
            pass

    # 确保文件名安全
    safe_filename = urllib.parse.quote(filename, safe='')
    # 构造完整的本地保存路径
    save_path = os.path.join(local_path, safe_filename)
    return local_path, save_path


# 主函数：读取 CSV 并下载文件
def download_with_url_path_from_csv(csv_file_path, url_column_name, download_dir='downloaded_files'):
    create_directory(download_dir)

    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # 验证指定列是否存在
        if url_column_name not in reader.fieldnames:
            print(f"错误: CSV文件中未找到列 '{url_column_name}'")
            return

        for row in reader:
            url = row[url_column_name]
            if url:
                # 提取路径并构造本地保存路径
                local_dir, save_path = get_path_from_url(url, download_dir)
                # 创建本地目录
                create_directory(local_dir)
                # 下载文件
                download_file(url, save_path)
            else:
                print(f"跳过空 URL: {url}")


# 示例用法
if __name__ == "__main__":
    # 替换为你的 CSV 文件路径和列名
    csv_file = "export_urls.csv"
    url_column = "url"
    download_directory = "downloaded_files"

    download_with_url_path_from_csv(csv_file, url_column, download_directory)