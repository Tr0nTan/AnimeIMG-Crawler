import requests, re, os
from bs4 import BeautifulSoup
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# v1.2 解决了下载数量与输入数量不符的问题，原因为先收集100条url后才删除重复
# v1.3 1. 更换了multiprocessing至threading 2. 添加进度条

def geturls(names):
    mainurl = 'https://yande.re/post'
    next_url = ''
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'}
    filenames = []
    img_urls = []
    num = int(input('input how many pics need to save: '))
    while True:
        response = requests.get(mainurl+next_url[5:], headers = headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        tags = str(soup('script'))

        for url in re.findall('"file_url":"(.*?)"',tags): # iterate over all images' url in one page
            url = url.replace('\\/','/')
            a = unquote(url)
            filename = a[a.rindex('/')+1:]
            symbols = ['<','>',':','"','/','\\','|','?','*']
            for symbol in symbols:
                filename = filename.replace(symbol, ' ')

            if filename in names:
                continue
            else:
                img_urls.append(url)
                filenames.append(filename)
                    
        if len(img_urls) < int(num):
            next_url = soup.find_all('a', class_ = 'next_page', href=True)[0]['href']
            continue
        else:
            img_urls = img_urls[:int(num)]
            break

    return list(zip(img_urls, filenames))

def download(url, filename):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'}
        response = requests.get(url, headers = headers)
        open(f'temp\\{filename}', 'wb').write(response.content)
    except:
        print(f'Failed to download {url}')

if __name__=='__main__':
    saved_path = r'D:\AnimePic'
    os.chdir(saved_path)
    # 检查临时文件夹（由于图片越来越多，加载速度变慢因此创建该文件夹用于人工筛选）
    if not os.path.exists('temp'): 
        os.makedirs('temp')
    # all_names.txt用于存储所有爬取下来的图片名称
    if os.path.exists('Yande\\all_names.txt'):
        f = open('Yande\\all_names.txt','r')
        names = f.read().splitlines()
        # 消除重复
        names = [*set(names)]
        # names = list(dict(zip(names, [None]*len(names))).keys())
        f.close()
    else:
        f = open('Yande\\all_names.txt','w')
        names=[]
        f.close()

    # 将Yande文件夹中未添加的图片名称添加到names集合中，方便最后重新载入all_names.txt（针对因下载错误导致的程序中断）
    all_names = os.listdir(f'Yande')
    if 'all_names.txt' in all_names:
        all_names.remove('all_names.txt')
    if 'database.npy' in all_names:
        all_names.remove('database.npy')
    for i in all_names:
        if i not in names:
            names.append(i)

    urls_names = geturls(names)
    # Crawling part
    # num_cores = os.cpu_count()
    # num_threads = num_cores * 2
    with tqdm(total = len(urls_names)) as pbar:
        with ThreadPoolExecutor(max_workers = 8) as executor:
            futures=[executor.submit(download, *param) for param in urls_names]
            
            for future in as_completed(futures):
                result = future.result()
                pbar.update(1)

    # 将原有图片名称及新下载的图片名称写入all_names.txt
    f = open('Yande\\all_names.txt','w')
    for name in names:
        f.write(name+'\n')
    f.close()

    # 打开temp窗口
    os.startfile('temp')
    if input('完成人工筛选请回车进行查重：') == '':
        do = True
    else:
        print('程序退出')
        do = False

    # 将临时文件夹图片添加至Yande中
    filename = os.listdir('temp')
    for i in filename:
        os.rename(f'temp\\{i}', f'Yande\\{i}')

    # 查重
    if do:
        os.chdir('Yande')
        import image_duplicate_checking
        image_duplicate_checking.begin()
