from filedetectsublib import *

def begin():
    imgdir = {}
    #返回文件名(包括后缀), 新图片名称
    old_dictimg, new_dictimg = loadimages(path, imgdir)
    dictimg = {**old_dictimg, **new_dictimg}
    sameimg = retrieval_mode(new_dictimg, old_dictimg)

    #判断是否存在相似图片
    if len(sameimg) == 0:
        print('未找到相似图片，感谢使用')
    else:
        print('相似的图片：' + str(sameimg))
        #判断是否查看相似图片
        show_img(path, sameimg)
        #判断是否删除相似图片
        img_del(sameimg, path, dictimg)
            
    if input('回车退出程序') == '':
        print('数据写入中...')
        np.save(path + '\\' + 'database.npy', dictimg)
    print('已全部写入database.npy')

if __name__ == "__main__":
    path  =  input("输入文件夹地址:")
    begin()
else:
    path = os.getcwd()
