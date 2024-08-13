import requests, re, os, json
from bs4 import BeautifulSoup
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from myhash import imghash

# v1.2 解决了下载数量与输入数量不符的问题，原因为先收集100条url后才删除重复
# v1.3 1. 更换了multiprocessing至concurrent.futures 2. 添加进度条
# v1.4 1. 根据图片数字ID进行下载查重，解决特定情况下重复图片被下载的问题
# v1.5 1. 优化了路径，更改all_names.txt 至history.txt 2. 使用myhash算法替换brutal duplication checker， 进一步优化了数据库大小以及查重时间（Note: similar pics share the same hash code）

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
            name_id = [re.search('\d+', name).group(0) for name in names] # looking for digits only
            if re.search('\d+', filename).group(0) in name_id:
                continue
            else:
                img_urls.append(url)
                filenames.append(filename)
                names.append(filename)
                    
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

def listunpack(yourlist):
    listsdic = {}
    lists = list(zip(*yourlist))
    for i in range(len(lists)):
        list_name = f'list{i}'
        listsdic[list_name] = list(lists[i])
    return listsdic

def combine(new, old):
    for key in new:
        if key in old:
            old[key].extend(new[key])
        else:
            old[key]=new[key]
    return old

if __name__=='__main__':
    saved_path = r'D:\AnimePic\Yande'
    os.chdir(saved_path)
    # first time setting
    if not os.path.exists('temp'): 
        os.makedirs('temp')
    if not os.path.exists('images'):
        os.makedirs('images')
    if os.path.exists('history.txt'):
        f = open('history.txt','r', encoding="utf-8")
        names = f.read().splitlines()
        # 消除重复
        names = [*set(names)]
        # names = list(dict(zip(names, [None]*len(names))).keys())
        f.close()
    else:
        f = open('history.txt','w', encoding= 'utf-8')
        names=[]
        f.close()

    # 将Yande文件夹中未添加的图片名称添加到names集合中，方便最后重新载入history.txt（针对因下载错误导致的程序中断）
    all_names = os.listdir('images')
    if len(all_names) != 0:
        for i in all_names:
            if i not in names:
                names.append(i)

    # Crawling part
    # num_cores = os.cpu_count()
    # num_threads = num_cores * 1
    urls_names = geturls(names)
    multi = input('是否使用多线程进行爬取？是请回车')
    if multi == '':
        with tqdm(total = len(urls_names), desc='Images downlaoding (multithreading)') as pbar:
            with ThreadPoolExecutor(max_workers = 8) as executor:
                futures=[executor.submit(download, *param) for param in urls_names]
                for future in as_completed(futures):
                    result = future.result()
                    pbar.update(1)
    else:
        for pair in tqdm(urls_names, desc='Images downlaoding'):
            download(url=pair[0], filename=pair[1])

    # 将原有图片名称及新下载的图片名称写入history.txt
    f = open('history.txt','w', encoding= 'utf-8')
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

    # 哈希库
    if do:
        hasher = imghash(os.path.join(saved_path, 'temp'))
        hasher.start()
        if not os.path.exists('database.json'):
            database = hasher.result
        else:
            with open('database.json', 'r', encoding = 'utf-8') as f:
                database = json.load(f)
                f.close()
            database = combine(hasher.result, database)
        
        for key in database:
            if len(database[key]) > 1:
                print(key)
        
        with open('database.json', 'w', encoding = 'utf-8') as f:
            json.dump(database, f, indent=4)
            f.close()
        
        # 将临时文件夹图片添加至images文件夹中
        filename = os.listdir('temp')
        for i in filename:
            os.rename(f'temp\\{i}', f'images\\{i}')
        
        ######### more processes are needed on identical images