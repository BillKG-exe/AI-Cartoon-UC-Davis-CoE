from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import base64
import cv2
import json

import os

from text2im_model import BaseModel, UpSamplerModel
from style_transfer.test import TransferStyle

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # This enables CORS for all routes in your app


SOURCE = f"api/generated"
DESTINATION = r"C:\Users\ouatt\Desktop\AI Cartoon\api\results"


@app.route('/api/generate', methods=['POST'])
def sendImage():
  
    chat_id = request.json['chat_id']
    prompt_id = request.json['id']
    isChatOpened = request.json['isChatOpened']
    prompt = request.json['prompt']

    print(f"Prompt ID: {prompt_id} prompt: {prompt} isChatOpened: {isChatOpened} and chat_id: {chat_id}")

    # Generating the images from glide
    glide_model_path = 'C:\\Users\\ouatt\\Desktop\\glide-finetuned-43.pt'
    
    batch_size = 5

    text2im_model = BaseModel(model_path=glide_model_path, batch=batch_size)
    samples, options, device, has_cuda = text2im_model.generate(prompt, str(prompt_id))

    upsampler_model = UpSamplerModel(f"C:\\Users\\ouatt\\Desktop\\glide-finetuned-8.pt", options, device, has_cuda, batch_size)
    upsampler_model.generate(samples=samples, img_name=str(prompt_id))


    # Generating data to write or append to corresponding history
    imgs = []

    # retreive the name of the genrated images and their styles
    for i in range(batch_size):
        imgs.append(f"{prompt_id}_{i}.jpg")

    # Applying style transfer
    style_transfer_model = TransferStyle()
    
    for img in imgs:
        style_transfer_model.transfer_style(145, f'{SOURCE}\\{img}', SOURCE)

        #style_transfer_model.transfer_ tyle(160, f'{SOURCE}\\{img}',
        #SOURCE)

    # Append the applied style filenames to the imgs array
    for i in range(batch_size):
        for j in range(3):
            imgs.append(f"{prompt_id}_{i}_fake_{j+1}.jpg")

    # Data to store in the history
    data = {
        'prompt': prompt,
        'images': imgs
    }

    # History structure to store into history file
    hist = {
        str(prompt_id): data
    }
    

    try:
        with open(f'./history/{chat_id}.json', "r") as json_file:
            existing_data = json.load(json_file)

        existing_data.update(hist)

        with open(f'./history/{chat_id}.json', "w") as json_file:
            json.dump(existing_data, json_file, indent=4) 
    except FileNotFoundError:
        with open(f'./history/{chat_id}.json', "w") as json_file:
            json.dump(hist, json_file, indent=4) 


    # Send the resulting image to the user
    generated_images = []

    for i in range(len(imgs)):
        image = cv2.imread(f'./generated/{imgs[i]}')

        # Encode image data to Base64 string
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        generated_images.append(f'data:image/jpeg;base64,{image_base64}')

    response = {'images': generated_images}
    
    return jsonify(response)



@app.route('/api/promptHistory', methods=['GET'])
def sendPromptHistory():

    history = os.listdir('./history')

    data = []

    for file in history:
        with open(f'./history/{file}', "r") as json_file:
            existing_data = json.load(json_file) 

            prompt_id = file.split('.')[0]

            hist = {
                'id': prompt_id,
                'prompt': existing_data[prompt_id]['prompt'], 
            }     

            data.append(hist)
    
    sorted_data = sorted(data, key=lambda x: int(x['id']), reverse=True)
    
    response = {'prompts': sorted_data}
    
    return jsonify(response)


@app.route('/api/loadChatID', methods=['POST'])
def loadChatId():
    prompt_id = request.json['id']

    with open(f'./history/{prompt_id}.json', "r") as json_file:
        existing_data = json.load(json_file) 


    for _, data in existing_data.items():
        imgs = data['images']

        for index, im in enumerate(imgs):
            image = cv2.imread(f'./generated/{im}')

            # Encode image data to Base64 string
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            # Update image data in existing_data
            data['images'][index] = f'data:image/jpeg;base64,{image_base64}'
        

    response = {'prompts': existing_data}
    return jsonify(response)




@app.route('/api/deleteChat', methods=['POST'])
def delete_chat():
    prompt_id = request.json['id']

    try:
        os.remove(f'./history/{prompt_id}.json')
        success = True
    except OSError:
        success = False

    response = {'success': success}
    
    return jsonify(response)



    # Feed in the image into GLIDE model
   

    # # Feed in the image into Style Transfer

    # # Set the image path

    # # Send the resulting image to the user
    # generated_images = []

    # for i in range(4):
    #     image = cv2.imread(f'./Generated/{images_name}_{i}.png')

    #     # Encode image data to Base64 string
    #     _, buffer = cv2.imencode('.jpg', image)
    #     image_base64 = base64.b64encode(buffer).decode('utf-8')

    #     generated_images.append(f'data:image/jpeg;base64,{image_base64}')

    # # Prepare response dictionary
    # response = {'images': generated_images}
    
    # return jsonify(response)




if __name__ == '__main__':
    app.run(debug=True)