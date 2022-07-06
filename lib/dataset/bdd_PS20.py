import numpy as np
import json
import os
import scipy.io as scio
from .AutoDriveDataset import AutoDriveDataset
from .AutoDriveDataset_PS20 import AutoDriveDataset_PS20
from PIL import Image,ImageDraw
from .convert import convert, id_dict, id_dict_single
from tqdm import tqdm

single_cls = True       # just detect vehicle

class BddDataset_PS20(AutoDriveDataset_PS20):
    def __init__(self, cfg, is_train, inputsize, transform=None):
        super().__init__(cfg, is_train, inputsize, transform)
        self.db = self._get_db()
        self.cfg = cfg

    def _get_db(self):
        """
        get database from the annotation file

        Inputs:

        Returns:
        gt_db: (list)database   [a,b,c,...]
                a: (dictionary){'image':, 'information':, ......}
        image: image path
        mask: path of the segmetation label
        label: [cls_id, center_x//256, center_y//256, w//256, h//256] 256=IMAGE_SIZE
        """
        print('building database...')
        gt_db = []
        height, width = self.shapes

        # img_name = os.listdir(self.img_root)
        bbox_size = self.cfg.DATASET.BOX_SIZE
        for path_name in tqdm(self.img_root):
            if self.cfg.DATASET.DATA_FORMAT not in str(path_name):
                continue
            # if(len(gt_db)>40):
            #     break
            path_name = str(path_name)
            img_path = path_name
            label_path = path_name.replace("{}".format(self.cfg.DATASET.DATA_FORMAT),"mat")
            
            data = scio.loadmat(label_path)
            img = Image.open(img_path)
            bbox_list = data["marks"].tolist()
            
            
            #bbox vis
            # bbox_h = self.cfg.DATASET.BOX_SIZE
            # draw = ImageDraw.Draw(img)
            # for bbox in bbox_list:
            #     x ,y = bbox
            #     draw.rectangle([x-bbox_h, y-bbox_h, x+bbox_h, y+bbox_h], outline=(255,255,0))
            # img.show()
            
            
            gt = np.zeros((len(bbox_list), 5))
            for idx ,bbox in enumerate(bbox_list):
                x, y = bbox
                x1 = x - bbox_size
                y1 = y - bbox_size
                x2 = x + bbox_size
                y2 = y + bbox_size
                box = convert((width, height), (x1, x2, y1, y2))
                if single_cls:
                    gt[idx][0] = 0
                gt[idx][1:] = list(box)

            rec = [{
                'image': img_path,
                'label': gt
            }]

            gt_db += rec
            # label_path = mask_path.replace(str(self.mask_root), str(self.label_root)).replace(".png", ".json")
            # image_path = mask_path.replace(str(self.mask_root), str(self.img_root)).replace(".png", ".jpg")
            # lane_path = mask_path.replace(str(self.mask_root), str(self.lane_root))
            # with open(label_path, 'r') as f:
            #     label = json.load(f)
            # data = label['frames'][0]['objects']
            # data = self.filter_data(data)
            # gt = np.zeros((len(data), 5))
            # for idx, obj in enumerate(data):
            #     category = obj['category']
            #     if category == "traffic light":
            #         color = obj['attributes']['trafficLightColor']
            #         category = "tl_" + color
            #     if category in id_dict.keys():
            #         x1 = float(obj['box2d']['x1'])
            #         y1 = float(obj['box2d']['y1'])
            #         x2 = float(obj['box2d']['x2'])
            #         y2 = float(obj['box2d']['y2'])
            #         cls_id = id_dict[category]
            #         if single_cls:
            #              cls_id=0
            #         gt[idx][0] = cls_id
            #         box = convert((width, height), (x1, x2, y1, y2))#缩放标签到[0,1]之间
            #         gt[idx][1:] = list(box)
            #
            #
            # rec = [{
            #     'image': image_path,
            #     'label': gt,
            #     'mask': mask_path,
            #     'lane': lane_path
            # }]
            #
            # gt_db += rec
        print('database build finish')
        return gt_db

    def filter_data(self, data):
        remain = []
        for obj in data:
            if 'box2d' in obj.keys():  # obj.has_key('box2d'):
                if single_cls:
                    if obj['category'] in id_dict_single.keys():
                        remain.append(obj)
                else:
                    remain.append(obj)
        return remain

    def evaluate(self, cfg, preds, output_dir, *args, **kwargs):
        """  
        """
        pass


if __name__ == '__main__':
    #todo 增加画2D框可视化
    pass