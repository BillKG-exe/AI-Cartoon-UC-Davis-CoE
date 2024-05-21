import argparse
import os
#from util import util
import torch

class Options():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.initialized = False
        self.isTrain = False

    def initialize(self):
        self.parser.add_argument('--name', type=str, default='train', help='name of the experiment. It decides where to store samples and models')
        self.parser.add_argument('--checkpoints_dir', type=str, default=f'api/style_transfer/checkpoints', help='models are saved here')

        self.parser.add_argument('--dataroot', type=str, default='', help='path to images (should have subfolders train0, train1_stylename, train2_stylename, ..., edge1_stylename, edge2_stylename, ..., test)')
        self.parser.add_argument('--vgg_pretrained_mode', type=str, default='./vgg19.pth', help='path to the pretrained vgg model')
        self.parser.add_argument('--n_domains', type=int, default=3, help='Number of domains to transfer among generator')
        self.parser.add_argument('--d_domains', type=int, default=3, help='Number of domains to transfer among discriminator')

        self.parser.add_argument('--max_dataset_size', type=int, default=float("inf"), help='Maximum number of samples allowed per dataset. If the dataset directory contains more than max_dataset_size, only a subset is loaded.')
        self.parser.add_argument('--resize_or_crop', type=str, default='resize_and_crop', help='scaling and cropping of images at load time [resize|resize_and_crop|crop]')
        self.parser.add_argument('--no_flip', action='store_true',default=False, help='if specified, do not flip the images for data augmentation')   # false-->flip, true-->not flip

        self.parser.add_argument('--loadSize', type=int, default=256, help='scale images to this size') # initial loadSize=286
        self.parser.add_argument('--fineSize', type=int, default=256, help='then crop to this size')

        self.parser.add_argument('--batchSize', type=int, default=4, help='input batch size') 
        self.parser.add_argument('--input_nc', type=int, default=3, help='# of input image channels')
        self.parser.add_argument('--output_nc', type=int, default=3, help='# of output image channels')

        self.parser.add_argument('--ngf', type=int, default=64, help='# of gen filters in first conv layer')
        self.parser.add_argument('--ndf', type=int, default=32, help='# of discrim filters in first conv layer')
        self.parser.add_argument('--netG_n_blocks', type=int, default=9, help='number of residual blocks to use for netG')
        self.parser.add_argument('--netG_n_shared', type=int, default=0, help='number of blocks to use for netG shared center module')
        self.parser.add_argument('--netD_n_layers', type=int, default=4, help='number of layers to use for netD')
        self.parser.add_argument('--netG_framework', type=str, default='cartoon_generator', help='the framework design for netG')
        self.parser.add_argument('--netD_framework', type=str, default='cartoon_discriminator', help='the framework design for netD')
        self.parser.add_argument('--classifier_framework', type=str, default='conv4', help='the framework design for netD')

        self.parser.add_argument('--norm', type=str, default='instance', help='instance normalization or batch normalization') # use instance nromalization
        self.parser.add_argument('--use_dropout', action='store_true', default=False, help='insert dropout for the generator')

        self.parser.add_argument('--gpu_ids', type=str, default='-1', help='gpu ids: e.g. 0  0,1,2, 0,2. use -1 for CPU')
        self.parser.add_argument('--nThreads', default=1, type=int, help='# threads for loading data')

        self.parser.add_argument('--display_id', type=int, default=0, help='window id of the web display (set >1 to use visdom)') 
        self.parser.add_argument('--display_port', type=int, default=8097, help='visdom port of the web display')
        self.parser.add_argument('--display_winsize', type=int, default=256,  help='display window size')
        self.parser.add_argument('--display_single_pane_ncols', type=int, default=0, help='if positive, display all images in a single visdom web panel with certain number of images per row.')

        self.parser.add_argument('--results_dir', type=str, default='./results', help='saves results here.')
        self.parser.add_argument('--encoder_test', action='store_true', help='test the function of encoder part')
        self.parser.add_argument('--aspect_ratio', type=float, default=1.0, help='aspect ratio of result images')

        self.parser.add_argument('--which_epoch', type=int, default=145, help='which epoch to load for inference?')
        self.parser.add_argument('--phase', type=str, default='test', help='train, val, test, etc (determines name of folder to load from)')

        self.parser.add_argument('--how_many', type=int, default=751, help='how many test images to run (if serial_test not enabled)')
        self.parser.add_argument('--serial_test', action='store_true', help='read each image once from folders in sequential order')

        self.parser.add_argument('--autoencode', action='store_true', help='translate images back into its own domain')
        self.parser.add_argument('--reconstruct', action='store_true', help='do reconstructions of images during testing')

        self.parser.add_argument('--show_matrix', action='store_true', help='visualize images in a matrix format as well')

        self.initialized = True

    def parse(self):
        if not self.initialized:
            self.initialize()
        self.opt = self.parser.parse_args()
        self.opt.isTrain = self.isTrain   # train or test

        str_ids = self.opt.gpu_ids.split(',')  # split the GPU number
        self.opt.gpu_ids = []
        for str_id in str_ids:
            id = int(str_id)
            if id >= 0:
                self.opt.gpu_ids.append(id)

        # set gpu ids
        if len(self.opt.gpu_ids) > 0:
            torch.cuda.set_device(self.opt.gpu_ids[0])

        args = vars(self.opt)

        return self.opt
