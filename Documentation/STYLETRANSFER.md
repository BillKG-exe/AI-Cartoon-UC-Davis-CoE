# Style Transfer 

Style transfer is a technique that involves applying the visual style of one image to another image.

## Multi-Style Photo Cartoonization Model

Multi-style generative adversarial network (GAN) architecture, which can transform photos into multiple cartoon styles.

Pytorch implementation by Yezhi Shu, Ran Yi, Mengfei Xia, Zipeng Ye, Wang Zhao, Yang Chen, Yu-Kun Lai, Yong-Jin Liu. GAN-based Multi-Style Photo Cartoonization. IEEE Transactions on Visualization and Computer Graphics, DOI (identifier) 10.1109/TVCG.2021.3067201, 2021.

For details about its implementation please visit [IEEE Xplore](https://ieeexplore.ieee.org/document/9382902), and for access to the source code, please visit [Multi-Style Photo Cartoonization](https://github.com/syz825211943/Multi-Style-Photo-Cartoonization/tree/main).

### Framework

![MS-CartoonGAN][1]

[1]: architecture.png

## Set up

### Locally 

Clone the repo by calling `git clone https://github.com/syz825211943/Multi-Style-Photo-Cartoonization.git` from your terminal. Refer to the imported `requirements.txt` for dependencies.

### Using Cloud Computing Services - Google Colab

Google colab has most of the preinstalled libraries needed for training MS-CartoonGAN, refer to [CartoonGAN Colab](https://colab.research.google.com/drive/16WhKhN73rzsgmMWB0YignK5aA5zsYs3Z?usp=sharing) for an usage example and for the few additional libraries that need to be imported.

## Data Collection

There are some suggestions regarding the selection and collection of images for training:

* **Prevent overfitting to backgrounds:** Datasets with uniform backgrounds have been observed to cause issues in training the model by adding some bias, cause inadvertently change in colors, and struggle to properly blend the style in the generated images.

* **Increase Image Variety:** When extracting frames from video files, avoid extracting sequential frames. Sequential frames often lack variety in both content and style. Instead, consider extracting frames at intervals such as every 30th or 40th frame to ensure a diverse representation of content.

* **Data Balance:** Ensure the dataset includes various scenarios with diverse content and colors. This diversity helps the model generalize and perform well across different inputs.

Collect 3 or more cartoon styles for training the model. For our project, we collected between 3000 and 4000 images per cartoon style. If time and resources allow, it is advised to train the model with 6000 images for robustness.

Furthermore, you also need similar number of real images for training purposes.

## Data preprocessing

Before training the model, we need to have the original Cartoon images and the preprocessed cartoon images. To preprocess the cartoon images, follow the next steps:

* Detect edge pixels using a standard Canny edge detector.

* Dilate the edge regions.

* Apply Gaussian smoothing in the dilated edge regions.

## Train 

Once you have collected and preprocessed the data, you need to create the following file structure within your MS-CartoonGAN repo.

```
datasets/
└── dataset name/
    ├── edge1_[style1name]
    ├── edge2_[style2name]
    ├── edge3_[style3name]
    ├── test0
    ├── train0
    ├── train1_[style1name]
    ├── train2_[style2name]
    └── train3_[style3name]
```
The train0 folder contains real images, the train1, train2, and train3 folders contain the cartoon images while the edge1, edge2, and edge3 their corresponding preprocessed images for which the edges have been smoothed out. Finally, the images contained within the test0 subfolders are used for testing purposes once the model has been trained.

Download the vgg19.pth file from [vgg19](https://drive.google.com/drive/folders/1jOSl_sBpGzm1wAvLgU5vDJOV9tg2PzIc?usp=sharing) and place it within your MS-CartoonGAN repo.

Please, check the `options` subfolder within you MS MS-CartoonGAN repo for training and testing options and hyperparameter finetuning. For training with default values, do:

`python train.py --init --name train --dataroot [your dataset path]`

and for testing:

`python test.py --name train --serial_test --dataroot [your dataset path] --which_epoch 145`


