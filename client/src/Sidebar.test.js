import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import axios from 'axios';
import Sidebar from './views/Sidebar.js';

jest.mock('axios');

test('Sidebar renders without crashing', () => {
    render(<Sidebar />);
    const sidebarElement = screen.getByTestId('sidebar');
    expect(sidebarElement).toBeInTheDocument();
});

test('New Chat button works correctly', () => {
    const clearChat = jest.fn();
    render(<Sidebar clearChat={clearChat} />);
    const newChatButton = screen.getByTestId('sidebar-new-chat');
    fireEvent.click(newChatButton);
    expect(clearChat).toHaveBeenCalledWith(null);
});

test('Chat history is fetched and displayed', async () => {
    const prompts = ['Prompt 1', 'Prompt 2'];
    axios.get.mockResolvedValueOnce({ data: { prompts } });
    render(<Sidebar />);
    const promptElements = await screen.findAllByRole('button', { name: /Prompt \d/i });
    expect(promptElements).toHaveLength(prompts.length);
});

test('Chat is loaded when history item is clicked', async () => {
    const loadChat = jest.fn();
    const prompts = [{ id: '1', prompt: 'Prompt 1' }, { id: '2', prompt: 'Prompt 2' }];
    axios.get.mockResolvedValueOnce({ data: { prompts } });
    axios.post.mockResolvedValueOnce({ data: { chat: 'Chat 1' } });
    render(<Sidebar loadChat={loadChat} />);
    const promptElement = await screen.findByRole('button', { name: 'Prompt 1' });
    fireEvent.click(promptElement);
    await waitFor(() => expect(loadChat).toHaveBeenCalledWith('1', { chat: 'Chat 1' }));
});

test('Chat is deleted when delete icon is clicked', async () => {
    const clearChat = jest.fn();
    const prompts = [{ id: '1', prompt: 'Prompt 1' }, { id: '2', prompt: 'Prompt 2' }];
    axios.get.mockResolvedValueOnce({ data: { prompts } });
    axios.post.mockResolvedValueOnce({ data: { success: true } });
    render(<Sidebar clearChat={clearChat} />);
    const deleteIcon = await screen.findByRole('button', { name: /delete icon/i });
    fireEvent.click(deleteIcon);
    expect(clearChat).toHaveBeenCalledWith('1');
});