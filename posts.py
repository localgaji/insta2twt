from functions import *
from datetime import datetime


# 최근 포스트 체크
def check_post():
    response = requests.get(main_page + end_link)
    data = response.json()

    # PC에 저장된 게시물 리스트 불러오기
    with open("./logs/posts.txt", "r") as f:
        last_posts = [i.strip() for i in f.readlines()]

    # 가장 최근 게시물 3개의 업데이트 확인
    posts = data["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
    updated = []
    for i in range(3):
        post_link = "instagram.com/p/" + posts[i]["node"]["shortcode"] + "/"
        if post_link not in last_posts:
            latest_time = posts[i]["node"]["taken_at_timestamp"]
            # 새 게시물 링크를 파일에 추가
            with open("./logs/posts.txt", "a") as g:
                g.write("\n" + post_link)
            updated.append([post_link, latest_time])

    if not updated:
        print("no new post")
    return updated


# 새 게시물의 미디어를 다운로드하고 알림 전송
def get_post(post):
    latest_link, upload_time = post[0], post[1]

    response = requests.get("https://www." + latest_link + end_link)
    data = response.json()["items"][0]

    media_list = []

    # 게시물에 미디어가 여러개일 때
    if "carousel_media" in data.keys():
        count = data["carousel_media_count"]
        for i in range(count):
            media = data["carousel_media"][i]
            if 'video_versions' in media:  # 동영상일때
                media_url = media['video_versions'][0]["url"]
            else:  # 이미지일때
                media_url = media['image_versions2']["candidates"][0]["url"]
            media_list.append(media_url)

    # 게시물에 미디어가 1개일 때
    else:
        media = data
        if 'video_versions' in media:  # 동영상일때
            media_url = media['video_versions'][0]["url"]
        else:  # 이미지일때
            media_url = media['image_versions2']["candidates"][0]["url"]
        media_list.append(media_url)

    # 미디어 다운로드하기, 업로드 시간 알림 전송
    str_time = datetime.fromtimestamp(upload_time).strftime('%y%m%d_%H_%M_%S')
    save(media_list, str_time)

    if time.time() - upload_time < 1000:
        alarm(f"\n{str_time[0:6]} {twitter_text}", latest_link, media_list)
        twitter(str_time, latest_link)
    else:
        alarm(f"예전 포스트 {str_time}", latest_link, media_list)