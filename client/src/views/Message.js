import React from 'react';
import './message.css';

import { useState, useRef } from 'react';
import { FaEdit } from "react-icons/fa";

import axios from 'axios';


function Message({ id, name, text, images, index, isChatOpened, chat_id, updatePrompt }) {
    const [mustEdit, setMustEdit] = useState(false);
    const [editedText, setEditedText] = useState(text);
    const intervalIdRef = useRef(null);


    const downloadImage = (imageUrl, fileName) => {
        // Create an anchor element
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = fileName; // Set the filename for the download
      
        // Append the anchor element to the body
        document.body.appendChild(link);
      
        // Programmatically click on the anchor element
        link.click();
      
        document.body.removeChild(link);
      };

    const handleEdit = e => {
        setEditedText(e.target.value);
    }

    const handleSend = e => {
        setMustEdit(false);

        const data = {
            id: id,
            isChatOpened: isChatOpened,
            chat_id: !isChatOpened? id : chat_id,
            prompt: editedText,
            isEdit: true
        }

        console.log(data)
        
        // Do an edit send request to stop current thread and run the new one
        axios.post('http://127.0.0.1:5000/api/generate', data)
        .then(
            response => {   
                console.log("Edited prompt: ", response.data)
          
                const interv_id = setInterval(() => checkImagesLoadingStatus(id), 1000);
                intervalIdRef.current = interv_id;
            })
        .catch(error => {
            console.error('Error: ', error);
        })
    }

    const checkImagesLoadingStatus = (prompt_id) => {
        const data = { id: prompt_id }
    
        axios.post('http://127.0.0.1:5000/api/checkStatus', data)
        .then(
          response => {
            console.log("status: ", response.data.status);

            if(response.data.status === -1) {
                clearInterval(intervalIdRef.current);
                return;
            }
    
            if(response.data.images.length > 0) {
              const res = {
                id: prompt_id,
                prompt: "The following images were generated based on your prompt",
                imgs: response.data.images
              }
              
              console.log("setting prompt history...");
              updatePrompt(res, index)
              clearInterval(intervalIdRef.current);
            }   
          })
        .catch(error => {
            console.error('Error: ', error);
        })
      }

  return (
    <div className='message-box'>
        <div className='message-box-name'>{name}</div>
        {
            !mustEdit? (
                <div className='message-box-text'>{editedText}</div>
            ) : (
                <div className='edit-box'>
                    <input type="text" data-testid='edit-box' onChange={handleEdit} value={editedText}/>
                    <div className='edit-buttons'>
                        <div className='edit-cancel-btn' data-testid='edit-cancel-btn' onClick={handleSend}>cancel</div>
                        <div className='edit-submit-btn' data-testid='edit-submit-btn' onClick={handleSend}>Send</div>
                    </div>
                </div>
            )
        }
        {
            (!images && !mustEdit) && (
                <div className='message-box-edit'>
                    <FaEdit data-testid='edit-icon' onClick={() => setMustEdit(true)} />
                </div>
            ) 
        }
        <div className='images-display'>
            {
                images !== null && (
                    <div className='image-list'>
                        { images.map((imgPath, index) => (
                           <div key={imgPath}>
                                <img src={imgPath} alt='Generated Image' onClick={() => downloadImage(imgPath, id)}/>
                           </div> 
                        )) }
                    </div>
                )
            }
        </div>
    </div>
  )
}

export default Message