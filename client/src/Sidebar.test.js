import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import React from 'react';
import { act } from 'react-dom/test-utils';
import axios from 'axios';
import Sidebar from './views/Sidebar.js';
import '@testing-library/jest-dom';

jest.mock('axios');

test('Sidebar renders without crashing', () => {
    axios.get.mockResolvedValue({ data: { prompts: [] } }); // Mock the axios.get call
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
    const promptElements = await screen.findAllByRole('button', { name: /Prompt .*/i });
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
    const deleteButtons = await screen.findAllByRole('button', { name: /delete icon/i });
    fireEvent.click(deleteButtons[0]);
    await waitFor(() => expect(clearChat).toHaveBeenCalled());
    console.log('clearChat mock calls:', clearChat.mock.calls);
});

test('console.error is called when an error occurs', async () => {
    const error = new Error('Test error');
    axios.get.mockRejectedValue(error);
    const consoleSpy = jest.spyOn(console, 'error');

    await act(async () => {
        render(<Sidebar />);
    });

    expect(consoleSpy).toHaveBeenCalledWith('Error: ', error);
});

test('console.error is called when an error occurs in handleChatLoad', async () => {
    const error = new Error('Test error');
    axios.post.mockRejectedValue(error);
    const consoleSpy = jest.spyOn(console, 'error');

    const { findByRole } = render(<Sidebar />);
    const button = await findByRole('button', { name: /Prompt .*/i });
    fireEvent.click(button);

    await waitFor(() => expect(consoleSpy).toHaveBeenCalledWith('Error: ', error));
});

test('console.error is called when an error occurs in handleDelete', async () => {
    const error = new Error('Test error');
    axios.post.mockRejectedValue(error);
    const consoleSpy = jest.spyOn(console, 'error');

    render(<Sidebar />);
    const deleteButtons = await screen.findAllByRole('button', { name: /delete icon/i }, { timeout: 5000 });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => expect(consoleSpy).toHaveBeenCalledWith('Error: ', error));
});