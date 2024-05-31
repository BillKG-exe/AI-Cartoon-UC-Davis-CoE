import './App.css';
import Sidebar from './views/Sidebar';
import Message from './views/Message';

import { useState, useRef } from 'react';
import axios from 'axios';
import React from 'react';

import { TbSend2 } from "react-icons/tb";



function App() {
  const [chatID, setChatID] = useState(null)
  const [isChatOpened, setIsChatOpened] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [promptHistory, setPromptHistory] = useState([]);
  //const [intervalId, setIntervalId] = useState(null)
  const intervalIdRef = useRef(null);

  const setUserPrompt = e => {
    setPrompt(e.target.value);
  }

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

    setPromptHistory([...promptHistory, userInput])

    const data = {
      id: timeId,
      isChatOpened: isChatOpened,
      chat_id: !isChatOpened? timeId : chatID,
      prompt: prompt,
      isEdit: false
    }
    
    axios.post('http://127.0.0.1:5000/api/generate', data)
      .then(
        response => {   
          console.log("Generate: ", response.data)
          
          const interv_id = setInterval(() => checkImagesLoadingStatus(timeId), 1000);
          //setIntervalId(interv_id);
          intervalIdRef.current = interv_id;
        })
      .catch(error => {
          console.error('Error: ', error);
      })

    const dialogScreen = document.querySelector('.dialog-screen');

    setPrompt('');
    setIsChatOpened(true);
  }

  const checkImagesLoadingStatus = (prompt_id) => {
    const data = { id: prompt_id }

    axios.post('http://127.0.0.1:5000/api/checkStatus', data)
    .then(
      response => {
        console.log("status: ", response.data.status);
        // console.log("images: ", response.data.images);
      
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
    })
  }

  const handleKeyPress = e => {
    if(e.key === "Enter") {
      sendPrompt(e);
    }
  }

  const loadChat = (prompt_id, data) => {
    setChatID(prompt_id);
    setIsChatOpened(true);
    setPromptHistory(null)

    promptHistory.forEach((item) => {
      item.id = '';
      item.prompt = '';
      item.imgs = null;
    });

    let fetchedHistory = []

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

      fetchedHistory.push(hist)
      fetchedHistory.push(bot)
    });
    setPromptHistory(fetchedHistory)
  }

  const clearChat = (id) => {
    if(id !== null && id !== chatID) return;

    setChatID(null);
    setIsChatOpened(false);
    setPromptHistory([])
  }

  const updatePrompt = (res, index) => {
    promptHistory[index] = res;
    setPromptHistory([...promptHistory]);
  }

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
                    name={index % 2 === 0? "Alison" : "Bot"} 
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

export default App;