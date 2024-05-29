/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom'
import axios from 'axios';
import App from './App';

test('App renders without crashing', () => {
  render(<App />);
  const appElement = screen.getByTestId('app');
  expect(appElement).toBeInTheDocument();
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