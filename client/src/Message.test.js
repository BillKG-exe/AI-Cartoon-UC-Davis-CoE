import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import React from 'react';
import { act } from 'react-dom/test-utils';
import axios from 'axios';
import '@testing-library/jest-dom';
import Message from './views//Message.js';
import App from './App';

jest.mock('axios');

// Set defaultProps for Message component
Message.defaultProps = {
  images: ['api/generated/123.jpg'],
};


// test('edits a message', () => {
//   render(<Message id="1" name="Test" text="Test message" />);
//   fireEvent.click(screen.getByTestId('edit-icon'));
//   expect(screen.getByTestId('edit-box')).toBeInTheDocument();
//   fireEvent.change(screen.getByTestId('edit-input'), { target: { value: 'Updated message' } });
//   fireEvent.click(screen.getByTestId('edit-submit-btn'));
//   expect(axios.post).toHaveBeenCalledWith('http://127.0.0.1:5000/api/generate', expect.anything());
// });

test('renders Message component', () => {
  render(<Message id="1" name="Test" text="Test message" />);
  expect(screen.getByTestId('message-box')).toBeInTheDocument();
  expect(screen.getByTestId('message-box-name')).toHaveTextContent('Test');
  expect(screen.getByTestId('message-box-text')).toHaveTextContent('Test message');
});

test('displays images', () => {
  const images = ['image1.jpg', 'image2.jpg'];
  render(<Message id="1" name="Test" text="Test message" images={images} />);
  expect(screen.getByTestId('image-list')).toBeInTheDocument();
  images.forEach((imgPath, index) => {
    expect(screen.getByTestId(`image-${index}`)).toBeInTheDocument();
  });
});