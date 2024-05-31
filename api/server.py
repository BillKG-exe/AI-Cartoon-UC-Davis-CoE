from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import base64
import cv2
import json

import io
import pickle

import os
import torch as th
import torch.multiprocessing as multiprocessing

from text2im_model import BaseModel, UpSamplerModel
from style_transfer.test import TransferStyle

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # This enables CORS for all routes in your app

tasks = {}
prompt_task_id = {}

# Set the start method to 'spawn'
multiprocessing.set_start_method('spawn', force=True)

SOURCE = f"api/generated"
DESTINATION = r"api/results"

GENERATED_PATH = os.path.join(os.getcwd(), 'generated')
HISTORY_PATH = os.path.join(os.getcwd(), 'history') 


@app.route('/api/generate', methods=['POST'])
def sendImage():
  
    chat_id = request.json['chat_id']
    prompt_id = request.json['id']
    isChatOpened = request.json['isChatOpened']
    prompt = request.json['prompt']
    isEdit = request.json['isEdit']

    print(f"Prompt ID: {prompt_id} prompt: {prompt} isChatOpened: {isChatOpened} and chat_id: {chat_id}")

    if isEdit:
        pid = prompt_task_id.get(str(prompt_id))

        if pid:
            task = tasks.get(pid)

            if not task:
                return jsonify({ 'success': 0, 'status': 'was not able to generate the images...' })


            task['process'].terminate()
            task['process'].join()

            del tasks[pid]
            del prompt_task_id[f"{str(prompt_id)}"]

    # Generating the images from glide
    glide_model_path = os.path.join(os.getcwd(), 'glide-finetuned-170.pt')
    
    batch_size = 1      

    text2im_model = BaseModel(model_path=glide_model_path, batch=batch_size)

    task_result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=text2im_model.generate, args=(prompt, task_result_queue, str(prompt_id)))
    process.start()

    prompt_task_id[f"{str(prompt_id)}"] = process.pid

    imgs = []

    for i in range(batch_size):
        imgs.append(f"{prompt_id}_{i}.jpg")

    tasks[process.pid] = {
        'process': process,
        'queue': task_result_queue,
        'prompt': prompt,
        'imgs': imgs,
        'chat_id': chat_id,
        'batch_size': batch_size
    }

    return jsonify({ 'success': 1, 'status': 'generating the images...' })


@app.route('/api/checkStatus', methods=['POST'])
def checkImageGenerationStatus():
    prompt_id = request.json['id']

    pid = prompt_task_id.get(str(prompt_id))

    if not pid:
        return jsonify({'error': 'could not find process id', 'status': -1})

    task = tasks.get(pid)

    if not task:
        return jsonify({'error': 'could not find process id', 'status': -1})

    if task['process'].is_alive():
        return jsonify({ 'status': 1, 'images': [] })

    # Applying style transfer
    imgs = task['imgs']

    style_transfer_model = TransferStyle()
    
    for img in imgs:
        path_to_img = os.path.join(GENERATED_PATH, img)
        style_transfer_model.transfer_style(145, path_to_img, GENERATED_PATH)

    # Append the applied style filenames to the imgs array
    for i in range(task['batch_size']):
        for j in range(3):
            imgs.append(f"{prompt_id}_{i}_fake_{j+1}.jpg")

    # Data to store in the history
    data = {
        'prompt': task['prompt'],
        'images': imgs
    }

    # History structure to store into history file
    hist = {
        str(prompt_id): data
    }
    
    chat_path = os.path.join(HISTORY_PATH, f"{task['chat_id']}.json")

    try:
        with open(chat_path, "r") as json_file:
            existing_data = json.load(json_file)

        existing_data.update(hist)

        with open(chat_path, "w") as json_file:
            json.dump(existing_data, json_file, indent=4) 
    except FileNotFoundError:
        with open(chat_path, "w") as json_file:
            json.dump(hist, json_file, indent=4) 


    try:
        del tasks[pid]
        del prompt_task_id[f"{str(prompt_id)}"]
    except:
        print("No tasks found for pid: ", pid)
        return jsonify({'status': 0, 'images': []})

    # Send the resulting image to the user
    generated_images = []

    for i in range(len(imgs)):
        generated_img_path = os.path.join(GENERATED_PATH, imgs[i])
        
        try:
            image = cv2.imread(generated_img_path)

            # Encode image data to Base64 string
            _, buffer = cv2.imencode('.jpg', image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            generated_images.append(f'data:image/jpeg;base64,{image_base64}')
        except:
            print("Checking validity")

    # status: 0 -> done, -1 -> death or does not exist, 1 -> running
    response = {'status': 0, 'images': generated_images}
    
    return jsonify(response)    


@app.route('/api/promptHistory', methods=['GET'])
def sendPromptHistory():

    history = os.listdir(HISTORY_PATH)

    data = []

    for file in history:
        chat_hist_path = os.path.join(HISTORY_PATH, file)

        with open(chat_hist_path, "r") as json_file:
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

    prompt_hist_path = os.path.join(HISTORY_PATH, f'{prompt_id}.json')

    with open(prompt_hist_path, "r") as json_file:
        existing_data = json.load(json_file) 


    for _, data in existing_data.items():
        imgs = data['images']

        for index, im in enumerate(imgs):
            generated_img_path = os.path.join(GENERATED_PATH, im)
            
            try:
                image = cv2.imread(generated_img_path)

                # Encode image data to Base64 string
                _, buffer = cv2.imencode('.jpg', image)
                image_base64 = base64.b64encode(buffer).decode('utf-8')

                # Update image data in existing_data
                data['images'][index] = f'data:image/jpeg;base64,{image_base64}'
            except:
                return jsonify({ 'status': 'Failed', 'prompts': None })
        

    response = {'prompts': existing_data}
    return jsonify(response)




@app.route('/api/deleteChat', methods=['POST'])
def delete_chat():
    chatID = request.json['id']

    history = os.listdir(HISTORY_PATH)

    try:
        for file in history:
            if file.split('.')[0] == chatID:
                path_to_json = os.path.join(HISTORY_PATH, file)

                with open(path_to_json, "r") as json_file:
                    existing_data = json.load(json_file) 
                    
                    for _, data in existing_data.items():
                        imgs = data['images']

                        for img in imgs:
                            path_img_to_del = os.path.join(GENERATED_PATH, img)
                            os.remove(path_img_to_del)

        path_to_json = os.path.join(HISTORY_PATH, f"{chatID}.json")
        os.remove(path_to_json)
        success = True
    except OSError:
        print("exception here")
        success = False

    response = {'success': success}

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)