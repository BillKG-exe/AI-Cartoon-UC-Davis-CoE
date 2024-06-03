import os
import pytest
import json
from unittest import mock
from server import app, tasks, prompt_task_id
from style_transfer.test import TransferStyle

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# def test_sendImage(client):
#     data = {
#         'chat_id': '123',
#         'id': 123,
#         'isChatOpened': True,
#         'prompt': 'Test prompt',
#         'isEdit': False
#     }
#     response = client.post('/api/generate', json=data)
#     assert response.status_code == 200
#     data = response.get_json()
#     assert data['success'] == 1

def test_checkImageGenerationStatus(client):
    data = {'id': 123}
    with mock.patch.dict(tasks, {123: {'process': mock.Mock(is_alive=mock.Mock(return_value=True))}}):
        with mock.patch.dict(prompt_task_id, {'123': 123}):
            response = client.post('/api/checkStatus', json=data)
            assert response.status_code == 200
            data = response.get_json()
            assert 'status' in data
            assert data['status'] == 1

# def test_sendImage_and_task_alive(client):
#     data = {
#         'chat_id': '1234',
#         'id': 1234,
#         'isChatOpened': True,
#         'prompt': 'Test prompt',
#         'isEdit': False
#     }

#     response = client.post('/api/generate', json=data)
#     assert response.status_code == 200
#     data = response.get_json()
#     assert data['success'] == 1

#     data = {'id': 1234}
#     with mock.patch.dict(tasks, {1234: {'process': mock.Mock(is_alive=mock.Mock(return_value=True))}}):
#         with mock.patch.dict(prompt_task_id, {'1234': 1234}):
#             response = client.post('/api/checkStatus', json=data)
#             assert response.status_code == 200
#             data = response.get_json()
#             assert data['status'] == 1

def test_sendPromptHistory(client):
    response = client.get('/api/promptHistory')
    assert response.status_code == 200
    data = response.get_json()
    assert 'prompts' in data

def test_loadChatId(client):
    data = {'id': '1'}
    with mock.patch('builtins.open', mock.mock_open(read_data=json.dumps({'1': {'images': ['image1.jpg']}}))):
        with mock.patch('cv2.imread', return_value=mock.Mock()):
            with mock.patch('cv2.imencode', return_value=(True, b'test')):
                response = client.post('/api/loadChatID', json=data)
                assert response.status_code == 200
                data = response.get_json()
                assert 'prompts' in data

def test_delete_chat(client):
    data = {'id': '1'}
    with mock.patch('os.listdir', return_value=['1.json']):
        with mock.patch('builtins.open', mock.mock_open(read_data=json.dumps({'1': {'images': ['image1.jpg']}}))):
            with mock.patch('os.remove') as mock_remove:
                response = client.post('/api/deleteChat', json=data)
                assert response.status_code == 200
                data = response.get_json()
                assert data['success'] == True
                mock_remove.assert_called()

# def test_delete_chat(client):
#     data = {'id': '1'}
#     response = client.post('/api/deleteChat', json=data)
#     assert response.status_code == 200
#     data = response.get_json()
#     assert  data['success'] == True

def test_delete_invalid_chat(client):
    data = {'id': '12'}
    response = client.post('/api/deleteChat', json=data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == False

# def test_generate_with_edit(client):
#     # Mock data for the initial generation
#     data = {
#         'chat_id': '123',
#         'id': 123,
#         'isChatOpened': True,
#         'prompt': 'Test prompt',
#         'isEdit': True
#     }

#     # Mock tasks and prompt_task_id
#     tasks[123] = {
#         'process': mock.Mock(),
#         'queue': mock.Mock(),
#         'prompt': 'Test prompt',
#         'imgs': ['image1.jpg'],
#         'chat_id': '123',
#         'batch_size': 1
#     }
#     prompt_task_id['123'] = 123

#     # Call the endpoint with edit flag
#     response = client.post('/api/generate', json=data)
#     assert response.status_code == 200
#     data = response.get_json()
#     assert data['success'] == 1
#     assert data['status'] == 'generating the images...'

def test_checkImageGenerationStatus_not_found(client):
    data = {'id': 999}
    response = client.post('/api/checkStatus', json=data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == -1

def test_loadChatId_not_found(client):
    data = {'id': '999'}
    with mock.patch('builtins.open', mock.mock_open(read_data=json.dumps({}))):
        response = client.post('/api/loadChatID', json=data)
        assert response.status_code == 200
        data = response.get_json()
        assert 'prompts' in data
        assert data['prompts'] == {}

def test_sendPromptHistory_empty(client):
    with mock.patch('os.listdir', return_value=[]):
        response = client.get('/api/promptHistory')
        assert response.status_code == 200
        data = response.get_json()
        assert 'prompts' in data
        assert len(data['prompts']) == 0

def test_delete_chat_file_not_found(client):
    data = {'id': '00000'}
    with mock.patch('os.listdir', return_value=[]):
        with mock.patch('os.remove') as mock_remove:
            response = client.post('/api/deleteChat', json=data)
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] == True
            assert mock_remove.call_count == 1


# Test for Check Status with Non-Existing Process ID
def test_check_status_non_existing_process(client):
    data = {'id': 999}
    response = client.post('/api/checkStatus', json=data)
    assert response.status_code == 200
    response_data = response.get_json()
    assert 'error' in response_data
    assert response_data['status'] == -1


def test_delete_chat_existing_id(client):
    data = {'id': 'test_chat'}
    history_files = ['test_chat.json']

    with mock.patch('os.listdir', return_value=history_files), \
         mock.patch('builtins.open', mock.mock_open(read_data='{}')), \
         mock.patch('os.remove') as mock_remove:
        response = client.post('/api/deleteChat', json=data)
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['success'] == True
        mock_remove.assert_called()

def test_style_transfer(client):
    data = {'id': 123}
    mock_task = {
        'process': mock.Mock(is_alive=mock.Mock(return_value=False)),
        'imgs': ['123_0.jpg'],
        'batch_size': 1,
        'prompt': 'sample prompt',
        'chat_id': 123
    }

    with mock.patch.dict(tasks, {123: mock_task}):
        with mock.patch.dict(prompt_task_id, {'123': 123}):
            with mock.patch.object(TransferStyle, 'transfer_style', return_value=None):
                response = client.post('/api/checkStatus', json=data)
                assert response.status_code == 200
                data = response.get_json()
                assert 'status' in data
                assert data['status'] == 0
                # assert 'images' in data
                # assert data['images'] == ['123_0.jpg']
