import os
from .options import Options
from .cartoongan_model import CartoonGANModel
import ntpath
from PIL import Image
from torchvision import transforms

# Define the Visualizer class
class TransferStyle:

    def save_image(self, image_numpy, image_path):
        image_pil = Image.fromarray(image_numpy)
        image_pil.save(image_path)

    # Define the save_images method
    def save_images(self, save_dir, visuals, image_path):
        short_path = ntpath.basename(image_path)
        name = os.path.splitext(short_path)[0]
      
        for label, image_numpy in visuals.items():
            image_name = f"{name}_{label}.jpg"
            save_path = os.path.join(save_dir, image_name)
            self.save_image(image_numpy, save_path)
  
    def transfer_style(self, model, image_path, save_path):
        opt = Options().parse()
        opt.nThreads = 1   # test code only supports nThreads = 1
        opt.batchSize = 1  # test code only supports batchSize = 1
        opt.which_epoch = model

        model = CartoonGANModel(opt)

        # save_path = r"results"
        # image_path = r"dataset\test0\2014-08-27_00-00-08_UTC.jpg"
        load_image = Image.open(image_path).convert('RGB')

        transform = transforms.ToTensor()

        input_real = transform(load_image).unsqueeze(0)

        data = {
            'real': input_real,
            'path_real': image_path,
        }

        model.set_input(data)
        model.test()

        visuals = model.get_current_visuals(testing=True)
        #print('process image... %s' % image_path)
        self.save_images(save_path, visuals, image_path)
