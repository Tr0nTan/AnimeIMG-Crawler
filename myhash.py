import cv2, os, re, sys
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
from tqdm import *
import numpy as np
from sklearn.cluster import KMeans

# 输入图片路径集，输出20位字符
class imghash:
    def __init__(self, path):
        self.path_imgs = tuple(os.path.join(path, i) for i in os.listdir(path))
        self.image_suffix = ['png', 'jpg', 'webp', 'gif']
        self.kmeans = KMeans(n_clusters = 3, n_init=3, random_state=123) # 3 clusters (colours)
    
    def first(self, path):
        image_suffix = re.split('[.]', path)[-1]
        if image_suffix in self.image_suffix:
            return str(self.image_suffix.index(image_suffix))
        else:
            print(f'Suffix not considered, {path}')
    
    def second(self):
        y, x = self.image.shape[:2]
        if y > x:
            return str(1)
        elif y < x:
            return str(0)
        elif y == x:
            return str(2)

    def segmentation(self):
        try:
            self.kmeans.fit(self.dim1)
            segmented_img = self.kmeans.cluster_centers_[self.kmeans.labels_]
            uniques = np.unique((segmented_img*255).astype('uint8'), axis=0) 
            result=[]
            for r in uniques:
                temp = tuple(r.tolist())
                result.append('%02x%02x%02x' % temp)
            return ''.join(result)
        except:
            cv2.imwrite(r'C:\Users\aa\Desktop\fucked_up.png', self.image.shape)
            pass

    def hashing(self, path):
        try:
            self.image = plt.imread(path)
            # first digit
            first_digit = self.first(path)
            # second digit
            second_digit = self.second()
            # hex part
            self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR) 
            self.image = cv2.resize(self.image, (128,128))
            self.dim1 = self.image.reshape(-1, 3) # turn into 1-D array
            hexdigits = self.segmentation()
            return [path, first_digit + second_digit + hexdigits]
        except Exception as e:
            print(e)
            sys.exit()
                            
    def start(self, multi=True):
        self.result={}
        if multi:
            with ProcessPoolExecutor(max_workers=8) as executor:
                max_ = len(self.path_imgs)
                with tqdm(total=max_, desc="Images loading") as pbar:
                    for result in executor.map(self.hashing, self.path_imgs):
                        if result[1] not in self.result:
                            self.result[result[1]] = [result[0]]
                        else:
                            self.result[result[1]].append(result[0])
                        pbar.update()
        else:
            for i in tqdm(self.path_imgs):
                result = self.hashing(i)
                if result[1] not in self.result:
                    self.result[result[1]] = [result[0]]
                else:
                    self.result[result[1]].append(result[0])

# test
if __name__=='__main__':
    import json
    direction = input('Paste path here: ')
    myhash = imghash(direction)
    # load all image under path
    myhash.start(multi=True) 
    with open(r'C:\Users\aa\Desktop\data.json', 'w', encoding= 'utf-8') as f:
        json.dump(myhash.result, f, indent=4)
        

    
    


