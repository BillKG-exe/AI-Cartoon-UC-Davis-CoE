import numpy as np
import torch
import os
from collections import OrderedDict
# from .base_model import BaseModel
from .networks import define_G
import copy
import torch.nn as nn


class BaseModel():
    def name(self):
        return 'BaseModel'

    def __init__(self, opt):
        self.opt = opt
        self.gpu_ids = opt.gpu_ids
        self.isTrain = opt.isTrain
        self.Tensor = torch.cuda.FloatTensor if self.gpu_ids else torch.Tensor
        self.save_dir = opt.checkpoints_dir

    def set_input(self, input):
        self.input = input

    def forward(self):
        pass

    # used in test time, no backprop
    def test(self):
        pass

    def get_image_paths(self):
        pass

    def optimize_parameters(self):
        pass

    def get_current_visuals(self):
        return self.input

    def get_current_errors(self):
        return {}

    def save(self, label):
        pass

    # helper saving function that can be used by subclasses
    def save_network(self, network, network_label, epoch, gpu_ids):
        save_filename = '%d_net_%s' % (epoch, network_label)
        save_path = os.path.join(self.save_dir, save_filename)
        network.save(save_path)
        if gpu_ids and torch.cuda.is_available():
            network.cuda(gpu_ids[0])

    # helper loading function that can be used by subclasses
    def load_network(self, network, network_label, epoch):
        save_filename = '%d_net_%s' % (epoch, network_label)
        save_path = os.path.join(self.save_dir, save_filename)
        network.load(save_path)

    # load_part_network (only encoder part, part = 0)
    def load_part_network(self, network, network_label, epoch, part):
        save_filename = '%d_net_%s' % (epoch, network_label)
        save_path = os.path.join(self.save_dir, save_filename)
        network.load_part(save_path, part)

    def update_learning_rate():
        pass


class CartoonGANModel(BaseModel):
    def name(self):
        return 'CartoonGANModel'
        

    def __init__(self, opt):
	# raise problems using super(),so use BaseModel.__init__(self.opt) instead
        # super(ComboGANModel, self).__init__(opt) 
        BaseModel.__init__(self, opt)
        self.n_domains = opt.n_domains
        self.d_domains = opt.d_domains
        self.batchSize = opt.batchSize
        self.DA, self.DB, self.DC = None, None, None  # classify the domains

        self.real = self.Tensor(opt.batchSize, opt.input_nc, opt.fineSize, opt.fineSize)
        self.real_A = self.Tensor(opt.batchSize, opt.input_nc, opt.fineSize, opt.fineSize)  # images in style 1
        self.real_B = self.Tensor(opt.batchSize, opt.input_nc, opt.fineSize, opt.fineSize)  # images in style 2
        self.real_C = self.Tensor(opt.batchSize, opt.input_nc, opt.fineSize, opt.fineSize)  # images in style 3
      
        # load/define networks
        self.netG = define_G(opt.netG_framework, opt.input_nc, opt.output_nc, opt.ngf,
                    opt.netG_n_blocks, opt.netG_n_shared,
                    self.n_domains, opt.norm, opt.use_dropout, self.gpu_ids)
       
        # load model weights
        if not self.isTrain or opt.continue_train:
            which_epoch = opt.which_epoch
            self.load_network(self.netG, 'G', which_epoch)
            if self.isTrain and not opt.init:
                self.load_network(self.netD, 'D', which_epoch)
                self.load_network(self.classifier, 'A', which_epoch)

        # test the function of encoder part
        if opt.encoder_test:
            which_epoch = opt.which_epoch
            self.load_part_network(self.netG, 'G', which_epoch, 0)
            print("load weights of encoder successfully")


    def set_input(self, input): # input is a dictionary recording images
        input_real = input['real']
        self.real.resize_(input_real.size()).copy_(input_real)
        self.image_paths = input['path_real']

    def test(self):
        with torch.no_grad():
            # self.visuals = [self.real]
            # self.labels = ['real']
            self.visuals = []
            self.labels = []
            encoded = self.netG.encode(self.real, 0)
            #print(self.real.size())
            for d in range(self.n_domains):
                if d == self.DA and not self.opt.autoencode:
                    continue
                fake = self.netG.decode(encoded, d)
                self.visuals.append( fake )
                self.labels.append( 'fake_%d' % (d+1) )
                if self.opt.reconstruct:
                    rec = self.netG.forward(fake, d, self.DA)
                    self.visuals.append( rec )
                    self.labels.append( 'rec_%d' % d )

    def get_image_paths(self):
        return self.image_paths

    def tensor2im(image_tensor, imtype=np.uint8):
        image_numpy = image_tensor[0].cpu().float().numpy()
        image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0
        return image_numpy.astype(imtype)
    
    def get_current_visuals(self, testing=False):
        if not testing:
            # self.visuals = [self.fake_A, self.fake_B, self.fake_C]
            # self.labels = ['fake' + str(self.DA), 'fake' + str(self.DB), 'fake'+str(self.DC)]
            self.visuals = [self.real, self.fake_A, self.fake_B, self.fake_C]
            self.labels = ['real', 'fake' + str(self.DA), 'fake' + str(self.DB), 'fake'+str(self.DC)]    
        images = [CartoonGANModel.tensor2im(v.data) for v in self.visuals]
        return OrderedDict(zip(self.labels, images))

