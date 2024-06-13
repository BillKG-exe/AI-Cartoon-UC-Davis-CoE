# AI Cartoons Frontend

This is the frontend part of the AI Cartoons project, built using React. The frontend consists of several key components that work together to provide a user interface for interacting with the AI model.

## Table of Contents

- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Components](#components)
  - [App.js](#appjs)
  - [Message.js](#messagejs)
  - [Sidebar.js](#sidebarjs)
- [Styling](#styling)
- [Dependencies](#dependencies)

## Installation

Before running the project, ensure you have Node.js and npm (Node Package Manager) installed on your machine. You can download Node.js and npm from [here](https://nodejs.org/).

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/aicartoons-frontend.git
   cd aicartoons-frontend
   ```

2. Install the dependencies:

   ```bash
   npm install
   ```

## Running the Application

To run the application locally, use the following command:

```bash
npm start
```

This command will start the development server and open the application in your default web browser. The application will typically run at `http://localhost:3000`.

## Project Structure

The project structure is as follows:

```
aicartoons-frontend/
│
├── public/
│   ├── index.html
│   └── ...
├── src/
│   ├── components/
│   │   ├── App.js
│   │   ├── Message.js
│   │   └── Sidebar.js
│   ├── css/
│   │   ├── App.css
│   │   ├── message.css
│   │   └── sidebar.css
│   ├── index.js
│   └── ...
├── package.json
└── README.md
```

## Components

### App.js

#### Description

`App.js` is the main component of the application. It manages the overall state and functionality, including handling user prompts, updating prompt history, and communicating with the backend API.

#### Key Functions

- **setUserPrompt**: Updates the `prompt` state based on user input.
- **sendPrompt**: Sends the user prompt to the backend API and sets up an interval to check for image generation status.
- **checkImagesLoadingStatus**: Periodically checks the status of image generation and updates the prompt history once images are available.
- **handleKeyPress**: Sends the prompt when the Enter key is pressed.
- **loadChat**: Loads a specific chat history from the backend.
- **clearChat**: Clears the current chat and prompt history.
- **updatePrompt**: Updates the prompt history with new data.

#### Running

`App.js` is included in the main application bundle and is executed when you run `npm start`.

### Message.js

#### Description

`Message.js` is a component responsible for displaying individual messages and their associated images. It also handles editing of messages and downloading of images.

#### Key Functions

- **downloadImage**: Downloads an image when clicked.
- **handleEdit**: Handles the change in the edited text.
- **handleSend**: Sends the edited text to the backend API and checks for updated images.
- **checkImagesLoadingStatus**: Checks the status of image generation for the edited prompt.

#### Running

`Message.js` is used within `App.js` to render messages. It does not need to be run separately.

### Sidebar.js

#### Description

`Sidebar.js` is a component that displays the chat history and allows users to load or delete previous chats. It also provides an option to start a new chat.

#### Key Functions

- **handleChatLoad**: Loads a specific chat history from the backend.
- **handleDelete**: Deletes a specific chat from the backend.
- **useEffect**: Fetches the prompt history from the backend when the component mounts or when the chat changes.

#### Running

`Sidebar.js` is used within `App.js` to render the sidebar. It does not need to be run separately.

## Styling

The styling for the components is located in the `css` directory:

- `App.css`: Styles for the `App.js` component.
- `message.css`: Styles for the `Message.js` component.
- `sidebar.css`: Styles for the `Sidebar.js` component.

Ensure you import these CSS files in their respective components to apply the styles.

## Dependencies

The main dependencies for this project are:

- `react`: Library for building user interfaces.
- `axios`: Library for making HTTP requests.
- `react-icons`: Library for including icons in your React project.

You can find all the dependencies listed in the `package.json` file. Make sure to run `npm install` to install all the necessary packages.

## Conclusion

This documentation provides an overview of the frontend of the AI Cartoons project. If you have any questions or need further assistance, feel free to open an issue or contact the project maintainer.
