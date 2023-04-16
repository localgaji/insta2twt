import os
import time
import requests
import subprocess
from login import *


def ffmpeg(folder, filename):
    video_file_path = f'./media/{folder}/{filename}'
    encoded_file_path = f'./media/{folder}/f{filename}'
    subprocess.call(
        ['ffmpeg', '-i', video_file_path, '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', '-c:a', 'aac', '-b:a',
         '128k', encoded_file_path])
    return encoded_file_path


def twitter(folder, link):
    filelist = os.listdir(f'./media/{folder}')
    id_list = []
    last_id = None

    for filename in filelist:
        path = f'./media/{folder}/{filename}'
        if "mp4" in filename:
            ffmpeg(folder, filename)
            path = f'./media/{folder}/f{filename}'

        media = api.media_upload(path)
        id_list.append(str(media.media_id))
        time.sleep(3)

        if "mp4" in filename:
            time.sleep(10)

    print(id_list)
    with open("./logs/ids.txt", "a") as f:
        f.write("\n" + " ".join(id_list))

    for i in range(0, len(filelist), 4):
        time.sleep(8)

        media_list = id_list[i:i + 4]
        if i + 4 > len(filelist):
            media_list = id_list[i:len(filelist)]

        if i == 0:
            response = client.create_tweet(text=f"{folder[0:6]} {twitter_text}\n\n{link}", media_ids=media_list)

        else:
            response = client.create_tweet(media_ids=media_list, in_reply_to_tweet_id=last_id)

        last_id = response[0]["id"]
        print(f'tweet : https://twitter.com/{upload_acc}/status/{response[0]["id"]}')
        alarm("트위터", f'twitter.com/{upload_acc}/status/{response[0]["id"]}', [])


def save(down, strnow):
    if type(down) == list:
        folder_name = f"./media/{strnow}"
        down_list = down
    else:
        folder_name = "./media/stories"
        down_list = [down]

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for index, image in enumerate(down_list):

        if "jpg" in image or "png" in image:
            extension = "jpg"
        else:
            extension = "mp4"

        # 저장 경로 설정
        if type(down) == list:
            image_path = os.path.join(folder_name, f"{index}.{extension}")
        else:
            image_path = os.path.join(folder_name, f"{strnow}.{extension}")

        # 이미지 다운로드 및 저장
        with open(image_path, "wb") as f:
            f.write(requests.get(image).content)

        if extension == "mp4":
            time.sleep(10)

    print(f"{len(down_list)}개 다운로드")
    time.sleep(3)


def alarm(ty: str, post_link: str, media_link: list):
    print(f"{ty}\n{post_link}")
    data_ = {'message': f"{ty}\n\n{post_link}"}

    requests.post(line_api_url, headers=line_headers, data=data_)

    for i in media_link:
        if "jpg" in i or "png" in i:  # 사진
            image = {
                'message': "-",
                'imageThumbnail': f"{i}",
                'imageFullsize': f"{i}"
            }
            requests.post(line_api_url, headers=line_headers, data=image)
        else:  # 동영상
            requests.post(line_api_url, headers=line_headers, data={'message': i})
