# WolframAlpha integration in VK.
# Authour: Kirill Zhosul (@kirill Zhosul)

# Importing modules.

# VK API Modules.
import vk_api.longpoll, vk_api.utils, vk_api.exceptions

# WolframAlpha modules.
import wolframalpha

# Default modules (Parsing, etc.)
import json
import requests
import os


def message_send(_peer_id: int, _message: str, _attachments: str=None) -> None:
    # Function that sends message.

    # Sending message.
    _api_vk.method("messages.send", {
        "random_id": vk_api.utils.get_random_id(),
        "peer_id": _peer_id, 
        "message": _response_prefix + _message, 
        "attachment": _attachments
    })

def upload_attachment_image(_path: str) -> str:
    # Method that uploads attachment image in vk.

    # Getting uploader.
    _uploader = vk_api.upload.VkUpload(_api_vk)

    # Getting photo uploaded.
    _photo = _uploader.photo_messages(_path)
    _photo = _photo[0]

    if "owner_id" in _photo and "id" in _photo and "access_key" in _photo:
        # If valid photo.

        # Getting data.
        _owner_id = _photo["owner_id"]
        _photo_id = _photo["id"]
        _access_key = _photo["access_key"]

        # Retunring photo.
        return f"photo{_owner_id}_{_photo_id}_{_access_key}"

    # If not valid photo.
    return ""

def download_image(_link: str, _path: str) -> None:
    # Function that downloads image from link.

    # Getting image.
    _image = requests.get(_link)

    # Saving.
    with open(_path, 'wb') as _file:
        _file.write(_image.content)

def process_query(_query: str) -> None:
    # Function that makes query and sends response.

    # Getting WolframAlpha query.
    _wa_query = _api_wa.query(_query)

    # How much response already.
    _response_amount = 0

    for _wa_pod in _wa_query.pods:
        # For every pod in query pods.

        # Getting title, and subpod.
        _wa_pod_title = _wa_pod["@title"]
        _wa_pod_subpod = _wa_pod["subpod"]

        # Continue if subpod is other list.
        if type(_wa_pod_subpod) == list:
            #for _wa_pod in _wa_query.pods:
            #   for _wa_subpod in _wa_pod.subpods:
            #       print(_wa_subpod.plaintext)
            continue
        
        # Getting image from subpod.
        _wa_subpod_image = _wa_pod_subpod["img"]["@src"]

        if "image/gif" in _wa_subpod_image:
            # If this is gif.

            # Image path.
            _path = "./Image.gif"

            # Getting image.
            download_image(_wa_subpod_image, _path)

            # Sending image.
            message_send(_event.peer_id, _wa_pod_title, upload_attachment_image(_path))

            # Check for response limit.
            _response_amount += 1
            if _response_limit is not None and _response_limit == _response_limit:
                return
        else:
            # If not image.

            # Sending text?.
            message_send(_event.peer_id, json.dumps(_wa_pod_subpod, sort_keys=True, indent=4), None)

            
# Connecting to the APIs.
_api_vk = vk_api.VkApi(token=os.getenv("VK_USER_TOKEN") or "YOUR_TOKEN_HERE")
_api_wa = wolframalpha.Client(os.getenv("WOLFRAMALPHA_API_KEY") or "YOUR_APPID_HERE")

# Prefixes.
_query_prefix = "?"
_response_prefix = "[WorframAlpha]: "

# Block response after this amount of response.
_response_limit = None # This is BROKEN! DONT CHANGE OR FIX BEFORE USING.

# Print.
print(_response_prefix + "Launched OK!")

for _event in vk_api.longpoll.VkLongPoll(_api_vk).listen():
    # For event in vk longpoll.

    # Continue if not new message.
    if _event.type != vk_api.longpoll.VkEventType.MESSAGE_NEW:
        continue

    # If not valid prefix.
    if not _event.message.startswith(_query_prefix):
        continue

    print(_response_prefix + f"Got new query {_event.message}")
    try:
        # Trying process query.

        # Processing.
        process_query(_event.message[len(_query_prefix)::])
    except Exception as _exception:
        # if any error.

        # Send error message.
        message_send(_event.peer_id, f"Нет ответа на ваш запрос, или ошибка! Отладка: {_exception}")