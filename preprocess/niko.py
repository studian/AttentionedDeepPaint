"""
Preprocess niko dataset and generate pair image
"""
import os
import glob

from . import scale, black2white

from PIL import Image

from torchvision import transforms
from torch.utils.data import Dataset


class NikoPairedDataset(Dataset):
    """
    Niko Manga Paired Dataset
    Composed of
    (colorized image, sketch image)
    """

    def __init__(self,
                 root='./data/pair_niko',
                 mode='train',
                 transform=None,
                 size=512):
        """
        @param root: data root
        @param mode: set mode (train, test, val)
        @param transform: Image Processing
        @param size: image crop (or resize) size
        """
        if mode not in {'train', 'val', 'test'}:
            raise ValueError('Invalid Dataset. Pick among (train, val, test)')

        root = os.path.join(root, mode)

        self.is_train = (mode == 'train')
        self.transform = transform
        self.image_files = glob.glob(os.path.join(root, '*.png'))
        self.size = size

        if len(self.image_files) == 0:
            # no png file, use jpg
            self.image_files = glob.glob(os.path.join(root, '*.jpg'))

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, index):
        """
        Niko Dataset Get Item
        @param index: index
        Returns:
            tuple: (imageA == original, imageB == sketch)
        """

        image = Image.open(self.image_files[index])
        image_width, image_height = image.size
        imageA = image.crop((0, 0, image_width // 2, image_height))
        imageB = image.crop((image_width // 2, 0, image_width, image_height))

        # default transforms, pad if needed and center crop 512
        width_pad = self.size - image_width // 2
        if width_pad < 0:
            # do not pad
            width_pad = 0

        height_pad = self.size - image_height
        if height_pad < 0:
            height_pad = 0

        # padding as black
        padding = transforms.Pad((width_pad // 2, height_pad // 2 + 1,
                                  width_pad // 2 + 1, height_pad // 2),
                                 (255, 255, 255))

        # use center crop
        crop = transforms.CenterCrop(self.size)

        imageA = padding(imageA)
        imageA = crop(imageA)

        imageB = padding(imageB)
        imageB = crop(imageB)

        # convert black padding to white padding
        imageA = black2white(imageA)
        imageB = black2white(imageB)

        if self.transform is not None:
            imageA = self.transform(imageA)
            imageB = self.transform(imageB)

        # scale image into range [-1, 1]
        imageA = scale(imageA)
        imageB = scale(imageB)
        return imageA, imageB
