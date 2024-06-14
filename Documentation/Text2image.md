## GLIDE Model
For the purpose of our project, we have finetuned openAI's text to image
model(also known as GLIDE) on UC Davis data. Below, will be provided a
step-by-step guide on how the model was finetuned. `GLIDE` is a state of the
art text to image model that uses stable diffusion to generate images. The
pre-trained model was trained on about 67 million text-image pairs. 

## GLIDE Finetuning Repo
We use the finetuning repo of GLIDE from [Clay
Mullis](https://github.com/afiaka87). The following repo:
[glide-ucdavis](https://github.com/BillKG-exe/gilde-ucdavis), contains
information
on the parameters used to do the training. It also contains the commands to
run to start the training.

## How was the training conduct?
To trained the model, we first had to gather data from UC Davis. The data had
to have the format of image and caption. Next, we have to start the training
and load the model for inference.

### Data Collection
 We were able
to obtained some data from Instagram using a webscrapper. We obtained about
3500 images. We also obtained images from the school album which was about 4000
images. One of our concern was not having enough data to produce a good
performing model, so to mitigate that issue, we did data augmentation by
flipping the image and changing the brightness. With data augmentation, our
dataset increased from about 7500 images to 22484 images.

With the images we obtained, we did not have caption for it. To generate
caption, we used a model `instructBlip` which provides the description of an
image given the image as input. The colab we used for that purpose is: [image
captioning](https://colab.research.google.com/drive/1fwM4UhN7_3M7eUXIxmZUD6r8WNObyY1n?usp=sharing).

After captioning the data the next step was to start the finetuning.

### Finetuning GLIDE
To finetune GLIDE, we use the following colab:
[glide](https://colab.research.google.com/drive/1wbmPc_fZb59SbQ1FV9pwa3cvxZi5Pi-N?usp=sharing).
We used wandb to monitor the loss during training. To train the model we use
the following command:
```python
!python '/content/gilde-ucdavis/train_glide.py' \
  --data_dir '/content/data' \
  --epochs 10 \
  --use_captions \
  --momentum .89 \
  --adam_weight_decay 0.0125 \
  --log_frequency 1000 \
  --resume_ckpt '/content/drive/My Drive/glide_finetuning/checkpoints_base/0010/glide-finetuned-13.pt'\
  --project_name 'finetune_base_1.1' \
  --batch_size 4 \
  --learning_rate 2e-05 \
  --side_x 64 \
  --side_y 64 \
  --resize_ratio 1.0 \
  --uncond_p 0.2 \
  --checkpoints_dir '/content/drive/My Drive/glide_finetuning/checkpoints_base'
```


We used a momemtum of .89 because the model was getting stuck on a local
minima. The model seemed to perform well with batch size of 4. For every
epochs, the model is saved in the checkpints directory.

### Model Inference
To test the model, we used the following colab:
[glide-text](https://colab.research.google.com/drive/1JUI4KemE2_UdVQcThqVzcmn3dCPXxO43?usp=sharing)
whih perfoms inference on the different saved models.


