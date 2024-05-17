import React from 'react';
import './message.css';

import { useState } from 'react';

import { FaEdit } from "react-icons/fa";

function Message({ id, name, text, images }) {
    const [mustEdit, setMustEdit] = useState(false);
    const [editedText, setEditedText] = useState(text);

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

        // Do an edit send request to stop current thread and run the new one
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