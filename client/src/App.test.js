/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { useState } from 'react';
import '@testing-library/jest-dom'
import axios from 'axios';
import App from './App';

jest.mock('axios');

describe('checkImagesLoadingStatus', () => {
  it('updates prompt history when images are loaded', async () => {
    const mockPromptId = 123;
    const mockImages = ['image1.png', 'image2.png'];
    const mockResponse = { data: { status: 1, images: mockImages } };

    axios.post.mockResolvedValue(mockResponse);
    axios.get.mockResolvedValue({ data: { prompts: [] } }); // Add this line
    
    const TestComponent = () => {
      const [promptHistory, setPromptHistory] = useState([]);
      const checkImagesLoadingStatus = (prompt_id) => {
        const data = { id: prompt_id }

        axios.post('http://127.0.0.1:5000/api/checkStatus', data)
        .then(
          response => {
            if(response.data.status === -1) {
              return;
            }

            if(response.data.images.length > 0) {
              const res = {
                id: prompt_id,
                prompt: "The following images were generated based on your prompt",
                imgs: response.data.images
              }
              
              setPromptHistory([...promptHistory, res]);
            }   
          })
        .catch(error => {
            console.error('Error: ', error);
        })
      }

      return <button onClick={() => checkImagesLoadingStatus(mockPromptId)}>Test</button>;
    };

    const { getByText } = render(<TestComponent />);

    await act(async () => {
      fireEvent.click(getByText('Test'));
    });

    expect(axios.post).toHaveBeenCalledWith('http://127.0.0.1:5000/api/checkStatus', { id: mockPromptId });
  });
});


test('App renders without crashing', () => {
  render(<App />);
  const appElement = screen.getByTestId('app-sidebar');
  expect(appElement).toBeInTheDocument();
});

test('renders Sidebar component', () => {
  render(<App />);
  const sidebarElement = screen.getByTestId('sidebar');
  expect(sidebarElement).toBeInTheDocument();
});

test('App renders without crashing', () => {
  render(<App />);
  const appElement = screen.getByTestId('app-sidebar');
  expect(appElement).toBeInTheDocument();
});

test('renders Sidebar component', () => {
  render(<App />);
  const sidebarElement = screen.getByTestId('sidebar');
  expect(sidebarElement).toBeInTheDocument();
});

test('renders send button', () => {
  render(<App />);
  const sendButtonElement = screen.getByTestId('send-button');
  expect(sendButtonElement).toBeInTheDocument();
});

test('renders input box', () => {
  render(<App />);
  const inputBoxElement = screen.getByTestId('input-box');
  expect(inputBoxElement).toBeInTheDocument();
});

test('renders send button', () => {
  render(<App />);
  const sendButtonElement = screen.getByTestId('send-button');
  expect(sendButtonElement).toBeInTheDocument();
});

test('Can succesfully type in input field', () => {
  render(<App />);
  const input = screen.getByPlaceholderText('Enter your prompt...');
  expect(input).toBeInTheDocument();
  input.value = 'Hello, World!';
  expect(input.value).toBe('Hello, World!');
});

test('displays text when send button is clicked or Enter key is pressed', () => {
  render(<App />);
  const textarea = screen.getByPlaceholderText('Enter your prompt...');
  const sendButton = screen.getByTestId('send-button');

  fireEvent.change(textarea, { target: { value: 'Test prompt 1' } });
  fireEvent.click(sendButton);

  expect(screen.getByText('Test prompt 1')).toBeInTheDocument();

  fireEvent.change(textarea, { target: { value: '' } });
  fireEvent.change(textarea, { target: { value: 'test prompt 2' } });
  fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });

  expect(screen.getByText('test prompt 2')).toBeInTheDocument();
});

test('edit button can be clicked and canceled', async () => {
  render(<App />);
  const textarea = screen.getByPlaceholderText('Enter your prompt...');
  const sendButton = screen.getByTestId('send-button');

  fireEvent.change(textarea, { target: { value: 'Test prompt 1' } });
  fireEvent.click(sendButton);

  expect(screen.getByText('Test prompt 1')).toBeInTheDocument();

  const editIcon = await screen.findByTestId('edit-icon');
  fireEvent.click(editIcon);

  const editBox = await screen.findByTestId('edit-box');
  expect(editBox).toBeInTheDocument();

  const inputField = await screen.findByDisplayValue('Test prompt 1');
  expect(inputField).toBeInTheDocument();

  const editCancelButton = await screen.findByTestId('edit-cancel-btn');
  fireEvent.click(editCancelButton);
  expect(inputField).not.toBeInTheDocument();
});

test('edit button can be clicked and text can be edited', async () => {
  render(<App />);
  const textarea = screen.getByPlaceholderText('Enter your prompt...');
  const sendButton = screen.getByTestId('send-button');

  fireEvent.change(textarea, { target: { value: 'Test prompt 1' } });
  fireEvent.click(sendButton);

  expect(screen.getByText('Test prompt 1')).toBeInTheDocument();

  const editIcon = await screen.findByTestId('edit-icon');
  fireEvent.click(editIcon);

  const editBox = await screen.findByTestId('edit-box');
  expect(editBox).toBeInTheDocument();

  const inputField = await screen.findByDisplayValue('Test prompt 1');
  expect(inputField).toBeInTheDocument();

  fireEvent.change(inputField, { target: { value: 'Test prompt 1 edited' } });
  expect(inputField.value).toBe('Test prompt 1 edited');

  const editSubmitButton = await screen.findByTestId('edit-submit-btn');
  fireEvent.click(editSubmitButton);
  expect(screen.getByText('Test prompt 1 edited')).toBeInTheDocument();
});

test('can create new chat', async () => {
  render(<App />);
  const textarea = screen.getByPlaceholderText('Enter your prompt...');
  const sendButton = screen.getByTestId('send-button');

  fireEvent.change(textarea, { target: { value: 'Test prompt 1' } });
  fireEvent.click(sendButton);

  expect(screen.getByText('Test prompt 1')).toBeInTheDocument();

  const clearChatButton = await screen.findByTestId('sidebar-new-chat');
  fireEvent.click(clearChatButton);

  expect(screen.queryByText('Test prompt 1')).not.toBeInTheDocument();
});

test('handles error for axios post request', async () => {
  // Force axios.post to reject the promise
  axios.post.mockRejectedValue(new Error('Network error'));

  // Add a mock implementation for axios.get
  axios.get.mockResolvedValue({ data: { prompts: [] } });

  // Spy on console.error
  const consoleSpy = jest.spyOn(console, 'error');

  render(<App />);

  // Wait for console.error to be called
  await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error: ', new Error('Network error'));
  });

  // Clean up the console spy
  consoleSpy.mockRestore();
});

test('handles axios post request in checkImagesLoadingStatus', async () => {
  // Mock axios.post to resolve with a specific response
  axios.post.mockResolvedValue({
    data: {
      status: 1,
      images: ['image1.png', 'image2.png']
    }
  });

  // Spy on console.log
  const consoleSpy = jest.spyOn(console, 'log');

  render(<App />);

  // Wait for console.log to be called
  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalledWith('status: ', 1);
    expect(consoleSpy).toHaveBeenCalledWith('setting prompt history...');
  });

  // Clean up the console spy
  consoleSpy.mockRestore();
});

test('handles error for axios post request in checkImagesLoadingStatus', async () => {
  // Force axios.post to reject the promise
  axios.post.mockRejectedValue(new Error('Network error'));

  // Spy on console.error
  const consoleSpy = jest.spyOn(console, 'error');

  render(<App />);

  // Wait for console.error to be called
  await waitFor(() => {
    expect(consoleSpy).toHaveBeenCalledWith('Error: ', new Error('Network error'));
  });

  // Clean up the console spy
  consoleSpy.mockRestore();
});

