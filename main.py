import requests
from pydub import AudioSegment
import time
import eel
eel.init('web')


def separate(text):
    if len(text) > 5000:
        separated = []
        iterations = len(text) // 5000 + 1
        begin = 0
        end = 5000
        for i in range(iterations):
            for j in range(end - 200, end):
                if text[j] == '.':
                    end = j
                    separated.append(text[begin:end + 1])
                    begin = end + 1
                    end += 5000
                    if end > len(text):
                        end = len(text)
                    break
        separated[-1]+=text[begin:]
        return separated
    return [text]



def synthesize(folder_id, iam_token, text, voice):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {
        'Authorization': 'Bearer ' + iam_token,
    }

    data = {
        'text': text,
        'folderId': folder_id,
        'voice': voice
    }

    with requests.post(url, headers=headers, data=data, stream=True) as resp:
        if resp.status_code != 200:
            print("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

        for chunk in resp.iter_content(chunk_size=None):
            yield chunk


@eel.expose
def main(text_filename, token, folder_id, voice):
    text_filename = text_filename.split('\\')
    text_filename = text_filename[-1]
    text_file = open(text_filename, encoding='utf-8')
    text = text_file.read()
    text_ready_to_upload = separate(text)

    files = []
    for i in range(len(text_ready_to_upload)):
        file_name = f'output{i}.ogg'
        files.append(file_name)
        with open(file_name, "wb") as f:
            for audio_content in synthesize(folder_id, token, text_ready_to_upload[i], voice):
                f.write(audio_content)
            eel.output(file_name)
            print(file_name +' успешно сохранен!')

    data = []
    eel.merge('Склейка файлов....')
    for file in files:
        s = AudioSegment.from_file(file, format='ogg')
        data.append(s)
    file_handle = sum(data).export("output.ogg", format="ogg")
    print('output.ogg успешно сохранен!')


eel.start('index.html',size=(550,450))