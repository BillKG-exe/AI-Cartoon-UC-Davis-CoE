import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import React from 'react';
import { act } from 'react-dom/test-utils';
import axios from 'axios';
import '@testing-library/jest-dom';
import Message from './views//Message.js';

jest.mock('axios');

test('renders message box', () => {
    render(<Message id="1" name="Test" text="Test message" />);
    const messageBox = screen.getByTestId('message-box');
    expect(messageBox).toBeInTheDocument();
  });
  
  test('renders message box name', () => {
    render(<Message id="1" name="Test" text="Test message" />);
    const messageBoxName = screen.getByTestId('message-box-name');
    expect(messageBoxName).toBeInTheDocument();
  });
  
  test('renders message box text', () => {
    render(<Message id="1" name="Test" text="Test message" />);
    const messageBoxText = screen.getByTestId('message-box-text');
    expect(messageBoxText).toBeInTheDocument();
  });
  
  test('renders edit box when edit icon is clicked', () => {
    render(<Message id="1" name="Test" text="Test message" />);
    const editIcon = screen.getByTestId('edit-icon');
    fireEvent.click(editIcon);
    const editBox = screen.getByTestId('edit-box');
    expect(editBox).toBeInTheDocument();
  });
  
  test('renders images display', () => {
    render(<Message id="1" name="Test" text="Test message" images={['image1.jpg', 'image2.jpg']} />);
    const imagesDisplay = screen.getByTestId('images-display');
    expect(imagesDisplay).toBeInTheDocument();
  });
  
  test('renders image list when images are provided', () => {
    render(<Message id="1" name="Test" text="Test message" images={['image1.jpg', 'image2.jpg']} />);
    const imageList = screen.getByTestId('image-list');
    expect(imageList).toBeInTheDocument();
  });