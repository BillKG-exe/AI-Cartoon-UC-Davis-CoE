import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { act } from 'react-dom/test-utils';
import axios from 'axios';
import Sidebar from './views/Sidebar.js';
import '@testing-library/jest-dom';

jest.mock('axios');

describe('Sidebar Component', () => {
  beforeEach(() => {
    axios.get.mockResolvedValue({ data: { prompts: [] } }); // Default mock for axios.get
    jest.clearAllMocks(); // Clear mocks between tests
  });

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
    const prompts = [{ id: '1', prompt: 'Prompt 1' }, { id: '2', prompt: 'Prompt 2' }];
    axios.get.mockResolvedValueOnce({ data: { prompts } });
    render(<Sidebar />);
    const promptElements = await screen.findAllByRole('button', { name: /Prompt .*/i });
    expect(promptElements).toHaveLength(prompts.length);
  });

  test('Chat is loaded when history item is clicked', async () => {
    const loadChat = jest.fn();
    const prompts = [{ id: '1', prompt: 'Prompt 1' }, { id: '2', prompt: 'Prompt 2' }];
    axios.get.mockResolvedValueOnce({ data: { prompts } });
    axios.post.mockResolvedValueOnce({ data: 'Chat 1' });

    render(<Sidebar loadChat={loadChat} />);
    const promptElement = await screen.findByRole('button', { name: 'Prompt 1' });
    fireEvent.click(promptElement);
    await waitFor(() => expect(loadChat).toHaveBeenCalledWith('1', 'Chat 1'));
  });

  test('Chat is deleted when delete icon is clicked', async () => {
    const clearChat = jest.fn();
    const prompts = [{ id: '1', prompt: 'Prompt 1' }, { id: '2', prompt: 'Prompt 2' }];
    axios.get.mockResolvedValueOnce({ data: { prompts } });
    axios.post.mockResolvedValueOnce({ data: { success: true } });

    render(<Sidebar clearChat={clearChat} />);
    const deleteButtons = await screen.findAllByLabelText('delete icon');
    fireEvent.click(deleteButtons[0]);
    await waitFor(() => expect(clearChat).toHaveBeenCalledWith('1'));
  });

  test('console.error is called when an error occurs', async () => {
    const error = new Error('Test error');
    axios.get.mockRejectedValueOnce(error);
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    await act(async () => {
        render(<Sidebar />);
    });

    expect(consoleSpy).toHaveBeenCalledWith('Error: ', error);
    consoleSpy.mockRestore();
  });

  test('console.error is called when an error occurs in handleChatLoad', async () => {
    const error = new Error('Test error');
    axios.post.mockRejectedValueOnce(error);
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    const prompts = [{ id: '1', prompt: 'Prompt 1' }];
    axios.get.mockResolvedValueOnce({ data: { prompts } });

    render(<Sidebar />);
    const button = await screen.findByRole('button', { name: 'Prompt 1' });
    fireEvent.click(button);

    await waitFor(() => expect(consoleSpy).toHaveBeenCalledWith('Error: ', error));
    consoleSpy.mockRestore();
  });

  test('console.error is called when an error occurs in handleDelete', async () => {
    const error = new Error('Test error');
    axios.post.mockRejectedValueOnce(error);
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    const prompts = [{ id: '1', prompt: 'Prompt 1' }];
    axios.get.mockResolvedValueOnce({ data: { prompts } });

    render(<Sidebar />);
    const deleteButtons = await screen.findAllByLabelText('delete icon');
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => expect(consoleSpy).toHaveBeenCalledWith('Error: ', error));
    consoleSpy.mockRestore();
  });
});
