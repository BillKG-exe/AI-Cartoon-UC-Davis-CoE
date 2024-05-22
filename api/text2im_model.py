import os
import datetime

import pickle

#@title Imports
from PIL import Image
from IPython.display import display
import torch as th
import torch.nn as nn

from glide_text2im.clip.model_creation import create_clip_model
from glide_text2im.download import load_checkpoint
from glide_text2im.model_creation import (
    create_model_and_diffusion,
    model_and_diffusion_defaults,
    model_and_diffusion_defaults_upsampler,
)

from glide_text2im.tokenizer.simple_tokenizer import SimpleTokenizer

class UpSamplerModel:
    def __init__(self, model_path, options, device, has_cuda, batch):
        self.batch_size = batch
        self.device = device


        self.options_up = model_and_diffusion_defaults_upsampler()
        self.options_up['use_fp16'] = has_cuda
        self.options_up['timestep_respacing'] = 'fast27' # use 27 diffusion steps for very fast sampling

        if len(model_path) > 0:
            assert os.path.exists(
                model_path
            ), f"Failed to resume from {model_path}, file does not exist."
            weights = th.load(model_path, map_location="cpu")
            self.model_up, self.diffusion_up = create_model_and_diffusion(**self.options_up)
            self.model_up.load_state_dict(weights)
            print(f"Resumed from {model_path} successfully.")
        else:
            self.model_up, self.diffusion_up = create_model_and_diffusion(**options)
            self.model_up.load_state_dict(load_checkpoint("upsample", device))

        if has_cuda:
            self.model_up.convert_to_fp16()
        self.model_up.to(device)

    def generate(self, samples, img_name, upsample_temp=1):
        tokens = self.model_up.tokenizer.encode('gunrock')
        tokens, mask = self.model_up.tokenizer.padded_tokens_and_mask(
            tokens, self.options_up['text_ctx']
        )

        # Create the model conditioning dict.
        model_kwargs = dict(
            # Low-res image to upsample.
            low_res=((samples+1)*127.5).round()/127.5 - 1,

            # Text tokens
            tokens=th.tensor(
                [tokens] * self.batch_size, device=self.device
            ),
            mask=th.tensor(
                [mask] * self.batch_size,
                dtype=th.bool,
                device=self.device,
            ),
        )

        # Sample from the base model.
        self.model_up.del_cache()
        up_shape = (self.batch_size, 3, self.options_up["image_size"], self.options_up["image_size"])
        up_samples = self.diffusion_up.plms_sample_loop(
            self.model_up,
            up_shape,
            noise=th.randn(up_shape, device=self.device) * upsample_temp,
            device=self.device,
            clip_denoised=True,
            progress=True,
            model_kwargs=model_kwargs,
            cond_fn=None,
        )[:self.batch_size]
        self.model_up.del_cache()

        self.download_images(up_samples, './Generated/', img_name)

    def download_images(self, batch: th.Tensor, directory: str, name: str):
        os.makedirs(directory, exist_ok=True)
        for i, image_tensor in enumerate(batch):
            scaled = ((image_tensor + 1) * 127.5).round().clamp(0, 255).to(th.uint8).cpu()
            reshaped = scaled.permute(1, 2, 0).numpy()

            filename = os.path.join(directory, f"{name}_{i}.jpg")
            Image.fromarray(reshaped).save(filename)


class BaseModel:
    def __init__(self, model_path, batch=4, guidance_scale=8):
        self.model_path = model_path
        self.options = model_and_diffusion_defaults()
        self.has_cuda = th.cuda.is_available()
        self.options['use_fp16'] = self.has_cuda
        self.device = th.device('cpu' if not self.has_cuda else 'cuda')
        self.batch_size = batch
        self.guidance_scale = guidance_scale

        self.base_timestep_respacing = '40'
        self.sr_timestep_respacing = 'fast27'

        # use 100 diffusion steps for fast sampling
        self.options['timestep_respacing'] = self.base_timestep_respacing 

        self.model, self.diffusion = create_model_and_diffusion(**self.options)

        if len(model_path) > 0:
            assert os.path.exists(
                model_path
            ), f"Failed to resume from {model_path}, file does not exist."
            weights = th.load(model_path, map_location="cpu")
            self.model, self.diffusion = create_model_and_diffusion(**self.options)
            self.model.load_state_dict(weights)
            print(f"Resumed from {model_path} successfully.")
        else:
            self.model, self.diffusion = create_model_and_diffusion(**self.options)
            self.model.load_state_dict(load_checkpoint("base", self.device))
        self.model.eval()
        if self.has_cuda:
            self.model.convert_to_fp16()
        self.model.to(self.device)
        print('total base parameters', sum(x.numel() for x in self.model.parameters()))

    def generate(self, prompt, task_result_queue, img_name):
        tokens = self.model.tokenizer.encode(prompt)

        tokens, mask = self.model.tokenizer.padded_tokens_and_mask(
            tokens, self.options["text_ctx"]
        )

        uncond_tokens, uncond_mask = self.model.tokenizer.padded_tokens_and_mask(
            [], self.options["text_ctx"]
        )

        model_kwargs = dict(
            tokens=th.tensor(
                [tokens] * self.batch_size + [uncond_tokens] * self.batch_size, device=self.device
            ),
            mask=th.tensor(
                [mask] * self.batch_size + [uncond_mask] * self.batch_size,
                dtype=th.bool,
                device=self.device,
            ),
        )

        def cfg_model_fn(x_t, ts, **kwargs):
            half = x_t[: len(x_t) // 2]
            combined = th.cat([half, half], dim=0)
            model_out = self.model(combined, ts, **kwargs)
            eps, rest = model_out[:, :3], model_out[:, 3:]
            cond_eps, uncond_eps = th.split(eps, len(eps) // 2, dim=0)
            half_eps = uncond_eps + self.guidance_scale * (cond_eps - uncond_eps)
            eps = th.cat([half_eps, half_eps], dim=0)
            return th.cat([eps, rest], dim=1)
        
        full_batch_size = self.batch_size * 2
        self.model.del_cache()

        samples = self.diffusion.plms_sample_loop(
            cfg_model_fn,
            (full_batch_size, 3, self.options["image_size"],self. options["image_size"]),
            device=self.device,
            clip_denoised=True,
            progress=True,
            model_kwargs=model_kwargs,
            cond_fn=None,
        )[:self.batch_size]

        # self.download_images(samples, './Generated/', img_name)
        # samples = samples.detach().cpu().numpy()
        # print("Putting samples into the queue...")

        upsampling_path = os.path.join(os.getcwd(), 'glide-finetuned-8.pt')
        upsampler_model = UpSamplerModel(upsampling_path, self.options, self.device, self.has_cuda, self.batch_size)
        upsampler_model.generate(samples=samples, img_name=img_name)

        task_result_queue.put('done... ')

        #(samples, self.options, self.device, self.has_cuda)') 
        # pickle.dump((samples, self.options, self.device, self.has_cuda), task_result_buffer)
        # task_result_queue.put((samples, self.options, self.device,
        # self.has_cuda)) 
        # print(samples.shape)
        # pickle.dump(samples, task_result_buffer)
        # pickle.dump(self.options, task_result_buffer)
        # pickle.dump(self.device, task_result_buffer)
        # pickle.dump(self.has_cuda, task_result_buffer)
        print("Samples put into the queue successfully.")


    def download_images(self, batch: th.Tensor, directory: str, name: str):
        os.makedirs(directory, exist_ok=True)
        for i, image_tensor in enumerate(batch):
            scaled = ((image_tensor + 1) * 127.5).round().clamp(0, 255).to(th.uint8).cpu()
            reshaped = scaled.permute(1, 2, 0).numpy()

            filename = os.path.join(directory, f"{name}_{i}.jpg")
            Image.fromarray(reshaped).save(filename)


if __name__ == "__main__":
    path = 'glide-finetuned-8.pt'
    
    model = BaseModel(model_path=path, batch=4)
    images_name = model.generate('Building')