# App.js Documentation

This document provides a detailed explanation of the `App.js` component in a React application. The `App.js` file is responsible for rendering the main structure of the application, managing user interactions, and communicating with a backend API to handle prompt submissions and fetch generated images.

## Dependencies

The following dependencies are imported:

- `React`: Core library for building user interfaces.
- `useState`, `useRef`: React hooks for managing state and references.
- `axios`: HTTP client for making API requests.
- `TbSend2`: Send icon from the `react-icons` library.
- `./App.css`: Custom CSS for styling the app.
- `Sidebar`: Custom component for the sidebar.
- `Message`: Custom component for displaying messages.

```javascript
import './App.css';
import Sidebar from './views/Sidebar';
import Message from './views/Message';

import { useState, useRef } from 'react';
import axios from 'axios';
import React from 'react';

import { TbSend2 } from "react-icons/tb";
```

## Main Component: App

The `App` component is the root component of the application. It handles the state, user interactions, and rendering of the main UI.

### State Variables

- `chatID`: Stores the ID of the current chat session.
- `isChatOpened`: Boolean indicating whether a chat session is open.
- `prompt`: The user's current input prompt.
- `promptHistory`: Array storing the history of prompts and responses.
- `intervalIdRef`: Reference to the interval ID used for polling the status of image generation.

```javascript
function App() {
  const [chatID, setChatID] = useState(null);
  const [isChatOpened, setIsChatOpened] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [promptHistory, setPromptHistory] = useState([]);
  const intervalIdRef = useRef(null);
```

### Event Handlers and Helper Functions

#### setUserPrompt

Handles the change event for the prompt input, updating the `prompt` state.

```javascript
const setUserPrompt = e => {
  setPrompt(e.target.value);
}
```

#### sendPrompt

Handles the submission of the prompt. It creates a new chat ID if necessary, sends the prompt to the backend API, and starts polling for the image generation status.

```javascript
const sendPrompt = e => {
  const timeId = new Date().getTime();
  
  if(chatID === null || !isChatOpened) {
    setChatID(timeId);
  }

  const userInput = {
    id: timeId,
    prompt: prompt,
    imgs: null
  }

  setPromptHistory([...promptHistory, userInput]);

  const data = {
    id: timeId,
    isChatOpened: isChatOpened,
    chat_id: !isChatOpened ? timeId : chatID,
    prompt: prompt,
    isEdit: false
  }
  
  axios.post('http://127.0.0.1:5000/api/generate', data)
    .then(response => {   
      console.log("Generate: ", response.data);
      
      const interv_id = setInterval(() => checkImagesLoadingStatus(timeId), 1000);
      intervalIdRef.current = interv_id;
    })
    .catch(error => {
      console.error('Error: ', error);
    });

  setPrompt('');
  setIsChatOpened(true);
}
```

#### checkImagesLoadingStatus

Polls the backend API to check the status of image generation and updates the prompt history when the images are ready.

```javascript
const checkImagesLoadingStatus = (prompt_id) => {
  const data = { id: prompt_id }

  axios.post('http://127.0.0.1:5000/api/checkStatus', data)
  .then(response => {
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
      setPromptHistory([...promptHistory, res]);
      clearInterval(intervalIdRef.current);
    }   
  })
  .catch(error => {
      console.error('Error: ', error);
  });
}
```

#### handleKeyPress

Handles the Enter key press event to submit the prompt.

```javascript
const handleKeyPress = e => {
  if(e.key === "Enter") {
    sendPrompt(e);
  }
}
```

#### loadChat

Loads a chat session from the given data, updating the chat ID and prompt history.

```javascript
const loadChat = (prompt_id, data) => {
  setChatID(prompt_id);
  setIsChatOpened(true);
  setPromptHistory(null);

  promptHistory.forEach((item) => {
    item.id = '';
    item.prompt = '';
    item.imgs = null;
  });

  let fetchedHistory = [];

  Object.keys(data.prompts).forEach(function(promptId, index) {
    const hist = {
      id: promptId,
      prompt: data.prompts[promptId]['prompt'],
      imgs: null
    }

    const bot = {
      id: promptId,
      prompt: "The following images were generated based on your prompt",
      imgs: data.prompts[promptId]['images']
    }

    fetchedHistory.push(hist);
    fetchedHistory.push(bot);
  });
  setPromptHistory(fetchedHistory);
}
```

#### clearChat

Clears the current chat session.

```javascript
const clearChat = (id) => {
  if(id !== null && id !== chatID) return;

  setChatID(null);
  setIsChatOpened(false);
  setPromptHistory([]);
}
```

#### updatePrompt

Updates a specific prompt in the prompt history.

```javascript
const updatePrompt = (res, index) => {
  promptHistory[index] = res;
  setPromptHistory([...promptHistory]);
}
```

### Render Method

Renders the main structure of the application, including the sidebar, chat display, and input box.

```javascript
return (
  <div className="App" data-testid="app">
    <main>
      <div className='app-sidebar' data-testid="app-sidebar">
        <Sidebar loadChat={loadChat} clearChat={clearChat} newChat={isChatOpened} />
      </div>
      <div className='dialog-screen' data-testid="dialog-screen">
        <div className='chat-display' id="message-list" data-testid="chat-display">
          {
            promptHistory.map((hist, index) => (
              <div key={`${hist.id}-${index}`}>
                <Message 
                  id={hist.id}
                  name={index % 2 === 0 ? "Alison" : "Bot"} 
                  text={hist.prompt} 
                  images={hist.imgs}
                  index={index}
                  isChatOpened={isChatOpened}
                  chat_id={chatID}
                  updatePrompt={updatePrompt}
                />
              </div>
            ))
          }
        </div>
        <div className='input-box' data-testid="input-box">
          <div>
            <div className='input-div' data-testid="input-div">
              <textarea 
                placeholder='Enter your prompt...'
                onChange={setUserPrompt}
                onKeyDown={handleKeyPress}
                value={prompt}
              />
            </div>
            <div className='send-button' onClick={sendPrompt} data-testid='send-button'>
              <TbSend2 />
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
);
}
```

### Export

Exports the `App` component as the default export of the module.

```javascript
export default App;
```

This documentation provides a comprehensive overview of the `App.js` component, including its state management, event handling, and rendering logic.
