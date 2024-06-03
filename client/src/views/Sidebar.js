import React from 'react';
import './sidebar.css';
import { FiEdit } from "react-icons/fi";
import { FaTrashAlt } from "react-icons/fa";

import { useEffect, useState } from 'react';

import axios from 'axios';

function Sidebar({ loadChat, clearChat, newChat }) {
    const [changeCount, setChangeCount] = useState(0)
    const [promptHistory, setPromptHistory] = useState([])

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/api/promptHistory')
            .then(
                response => {
                    setPromptHistory(response.data.prompts)
                })
            .catch(error => {
                console.error('Error: ', error);
            })
    }, [changeCount, newChat])

    const handleChatLoad = e => {
        const data = { id: e.target.id }

        axios.post('http://127.0.0.1:5000/api/loadChatID', data)
            .then(
                response => {
                    loadChat(e.target.id, response.data)
                })
            .catch(error => {
                console.error('Error: ', error);
            })
    }

    const handleDelete = id => {
        const data = { id: id }
        axios.post('http://127.0.0.1:5000/api/deleteChat', data)
            .then(
                response => {
                    if (response.data.success) {
                        console.log('Deleting chat with id:', id);
                        setChangeCount(changeCount + 1)
                        clearChat(id)
                    }
                })
            .catch(error => {
                console.error('Error: ', error);
            })
    }

    return (
        <div className='sidebar' data-testid="sidebar">
            <div className='sidebar-header'>
                <div className='sidebar-title'>AI Test Cartoons</div>
                <div className='sidebar-new-chat' data-testid='sidebar-new-chat' button role="button" onClick={() => clearChat(null)}>
                    <div className='sidebar-new-chat-text'>New Chat</div>
                    <div className='sidebar-new-chat-icon'>
                        <FiEdit />
                    </div>
                </div>
            </div>
            <div className='side-history'>
                {
                    promptHistory.map((hist, index) => (
                        <div key={hist.id} className='history-text'>
                            <div className='history-prompt' id={hist.id} button role="button" onClick={handleChatLoad} aria-label={`Prompt ${hist.id}`}>
                                {hist.prompt}
                            </div>
                            <button aria-label="delete icon" onClick={() => handleDelete(hist.id)}>
                                <FaTrashAlt />
                            </button>
                        </div>
                    ))
                }
            </div>
        </div>
    )
}

export default Sidebar

/* <div className='history-text'>
                <div className='history-prompt'>This came from yesterday actually because blabla</div>
                <div className='prompt-del-icon'>
                    <FaTrashAlt />
                </div>
            </div>
            <div className='history-text'>
                <div className='history-prompt'>I like having a lot of prompt yairyariyara</div>
                <div className='prompt-del-icon'>
                    <FaTrashAlt />
                </div>
            </div> */