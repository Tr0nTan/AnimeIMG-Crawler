import os
import cv2, re
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
from send2trash import send2trash

def loadimages(path, imgdir):
    print('准备图片加载')
    # 文件夹内所有文件名称
    filenames = os.listdir(path)
    # 检查存储已下载图片名称的txt文件是否存在
    if os.path.isfile('all_names.txt'): 
        filenames.remove('all_names.txt')
    else:
        pass
    # 数据库检查
    if os.path.isfile('database.npy'):
        dictimg = np.load(path + '\\database.npy', allow_pickle = True).item()
        filenames.remove('database.npy')
        # 若图片已经不存在了(人为删除)，将数据库中对应的数据也去除
        temp_del=[]
        for i in dictimg: 
            if i not in filenames:
                temp_del.append(i) 
        for i in temp_del: 
            dictimg.pop(i)
    else:
        dictimg = {}
    # 按照创建时间进行排序，添加到imgdir中
    new_image=[]
    same = True
    for name in filenames:
        if name not in dictimg:# 将所有存在的图片且没有被录入database的图片添加到new_image中
            time = os.path.getctime(path +'\\' + name)
            new_image.append((name,time))
            same = False
    new_image.sort(key = lambda x:x[1])
    if same:
            print('未发现任何新添加图片，数据写入中...')
            np.save(path + '\\' + 'database.npy', dictimg)
            print('已全部写入database.npy')
            sleep(5)
            quit()

    for i in new_image:
        imgdir[i[0]] = path +'\\' + i[0]
    # 将所有未添加到new_imgdict的图片按照创建时间添加
    temp_del=[]
    new_dictimg={}
    for name, path in imgdir.items():
        try:
            img = plt.imread(path)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            x = img.shape[1] * 0.1
            y = img.shape[0] * 0.1
            new_dictimg[name]=cv2.resize(img, (int(x),int(y)))
        except:# 将所有无法加载的图片添加到temp_del中，后续删除
            temp_del.append((name,path))
        show_load(list(imgdir.keys()).index(name)+1, len(imgdir))
    for pair in temp_del:
        send2trash(pair[1])
        imgdir.pop(pair[0])
    print('图片加载完成\n------------------')
    return (dictimg,new_dictimg)

def show_load(a,b):
    num = round((a/b)*100, 2)
    print(f'处理中: {num:.2f}%', end = '\r', flush=True)

def img_algo(name1, name2, dict1, dict2, temp_list):
    img1 = dict1[name1]
    img2 = dict2[name2]
    if img1.shape == img2.shape:#对比图片尺寸
        try:
            difference = cv2.absdiff(img1, img2)
            if cv2.countNonZero(difference) == 0:
                temp_list.append((name1, name2))
        except:
            difference = cv2.subtract(img1, img2, dtype=cv2.CV_64F)
            if cv2.countNonZero(np.abs(difference, out=difference)) == 0:
                temp_list.append((name1, name2))

def retrieval_mode(new_dictimg, old_dictimg):
    print('准备进行处理')
    sameimg1=[]
    sameimg2=[]
    if len(old_dictimg) != 0: # 非第一次运行
        #新之间的比较
        for i in range(0,len(new_dictimg)-1):
            for j in range(i+1, len(new_dictimg)):
                img_algo(list(new_dictimg)[i], list(new_dictimg)[j], new_dictimg, new_dictimg, sameimg2)
            show_load(i, len(new_dictimg)-1)
        # 新与旧的比较
        for i in new_dictimg:
            for j in old_dictimg:
                img_algo(i, j, new_dictimg, old_dictimg, sameimg1)
            show_load(list(new_dictimg.keys()).index(i), len(new_dictimg))
    else: # 第一次运行查重
        for i in range(0,len(new_dictimg)-1):
            for j in range(i+1, len(new_dictimg)):
                img_algo(list(new_dictimg)[i], list(new_dictimg)[j], new_dictimg, new_dictimg, sameimg2)
            show_load(i, len(new_dictimg)-1)
    sameimg = sameimg1 + sameimg2
    print('图片处理完成\n------------------')
    return sameimg
    
def img_del(sameimg, path, dictimg):
    imgdel = []
    delete = input('是否删除相似图片？是请回车')
    if delete == "":
        for i in sameimg:
            if bool(re.findall('[A-Za-z]', i[0][:-4])):
                if bool(re.findall('[A-Za-z]', i[1][:-4])):
                    if os.path.getctime(path +'\\' + i[0]) > os.path.getctime(path +'\\' + i[1]):
                        imgdel.append(i[0])
                    else:
                        imgdel.append(i[1])
                else:
                    imgdel.append(i[0])
            else:
                if bool(re.findall('[A-Za-z]', i[1][:-4])):
                    imgdel.append(i[1])
                else:
                    if int(i[0][:-4]) > int(i[1][:-4]):
                        imgdel.append(i[0])
                    else:
                        imgdel.append(i[1])
        imgdel = list(dict.fromkeys(imgdel)) #消除list中相同的元素
        for i in imgdel:
            send2trash(path + '\\' + i)
            dictimg.pop(i)
        print('已删除照片数量' + str(len(imgdel)))

def show_img(path, sameimg):
    ask = input('是否查看相似图片？是请回车')
    if ask == '':
        for i in range(len(sameimg)):
            img1 = cv2.imread(path + '//' + sameimg[i][0])
            img2 = cv2.imread(path + '//' + sameimg[i][1])
            if img1.shape[0] >= img1.shape[1]: #y轴大于等于x轴，水平展示相似图片
                coordinate = np.concatenate((img1,img2),axis=1)
                show_deter(coordinate)   
            else: #x轴大于y轴
                coordinate = np.concatenate((img1,img2),axis=0)
                show_deter(coordinate)

def compare_img(final):
    cv2.imshow('Images comparison', final)
    cv2.setWindowProperty('Images comparison', cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def hybrid_final(ratio, *, hybrid):
    if hybrid.shape[0] > 830:
        final = cv2.resize(hybrid, (int(830 / ratio),830))
    elif hybrid.shape[1] > 1440:
        final = cv2.resize(hybrid, (1440, int(1440 * ratio)))
    elif hybrid.shape[0] <= 830 and hybrid.shape[1] <= 1440:
        final = hybrid
    return final

def show_deter(coordinate):
    ratio = coordinate.shape[0]/coordinate.shape[1]
    if coordinate.shape[0] < 830 and coordinate.shape[1] < 1440:
        compare_img(coordinate)
    elif coordinate.shape[0] > coordinate.shape[1]: #合成后图片y轴仍大于x轴
        NewVerti = cv2.resize(coordinate, (int(830 / ratio),830))
        final = hybrid_final(ratio, hybrid = NewVerti)
        compare_img(final)
    elif coordinate.shape[0] < coordinate.shape[1]: #合成后图片x轴大于y轴
        NewVerti = cv2.resize(coordinate, (1440,int(1440 * ratio)))
        final = hybrid_final(ratio, hybrid = NewVerti)
        compare_img(final)
