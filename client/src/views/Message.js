import React from 'react';
import './message.css';


function Message({ id, name, text, images }) {
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


  return (
    <div className='message-box'>
        <div className='message-box-name'>{name}</div>
        <div className='message-box-text'>{text}</div>
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