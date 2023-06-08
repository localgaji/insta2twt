from datetime import datetime
from login import *


# reel json 페이지 확인
def check_story():
    full = GetDataChrome().get_json(story_graph)

    # 24시간 내 스토리가 없을 때
    if not full["data"]["reels_media"]:
        print("no story today")
        return None
    else:
        story_list = full["data"]["reels_media"][0]["items"]  # 스토리 모음 리스트

        # PC에 저장된 스토리 id 리스트 불러오기
        with open("./logs/stories.txt", "r") as f:
            last_stories = [i.strip() for i in f.readlines()]

        # 새 스토리 발견 시 정보 return
        if story_list[-1]["id"] not in last_stories:
            return [story_list, last_stories]
        else:
            print("no new story")
            return None


def get_story(got_story):
    story_list, last_stories = got_story[0], got_story[1]

    for item in story_list:
        story_url = item["id"]

        if story_url not in last_stories:
            upload_time = item["taken_at_timestamp"]

            with open("./logs/stories.txt", "a") as g:
                g.write("\n" + story_url)

            if item["is_video"]:
                media = item["video_resources"][0]["src"]
            else:
                media = item["display_url"]

            str_time = datetime.fromtimestamp(upload_time).strftime('%y%m%d_%H_%M_%S')
            save(media, str_time)

            if time.time() - upload_time < 3600:
                alarm(f"\n{str_time[0:6]} {twitter_text} 스토리", f"instagram.com/stories/{account}/{story_url}", [media])
            else:
                alarm(f"예전 스토리 {str_time}", f"instagram.com/stories/{account}/{story_url}", [media])



