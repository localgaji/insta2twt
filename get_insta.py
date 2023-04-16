import json
from functions import *
from datetime import datetime
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class InstaNoLogin:
    def __init__(self):
        self.options = Options()
        self.options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--ignore-ssl-errors")
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--enable-javascript')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument(
            "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, "
            "like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25")
        # self.options.add_argument('--headless')
        # self.options.add_argument("--start-maximized")
        # self.options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.main_page = "https://www.instagram.com/" + account

    # 드라이버 종료
    def teardown(self):
        self.driver.quit()

    # 요소 나타날 때까지 기다리기
    def wait_for(self, path, error_massage):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, path)))
            time.sleep(1)
        except TimeoutException:
            alarm("error", error_massage, [])

    # 로그인 여부 체크 : 셀레니움
    def login_check(self):

        self.driver.get(self.main_page)
        self.wait_for('//*[text() = "' + account + '"]', "main page time out")

        login = self.driver.find_elements(By.XPATH, '//*[text() = "가입하기"]')
        if not login:
            return True
        return False

    # 로그인 : 셀레니움
    def login(self):

        self.driver.get("https://www.instagram.com/accounts/login/")
        self.wait_for('//input[@aria-label="비밀번호"]', "login loading error")

        input_id = self.driver.find_elements(By.TAG_NAME, 'input')[0]
        input_pw = self.driver.find_elements(By.TAG_NAME, 'input')[1]

        input_id.click()
        input_id.send_keys(insta_id)
        input_pw.click()
        input_pw.send_keys(insta_pw)
        input_pw.send_keys(Keys.ENTER)

        self.wait_for('//*[contains (text(), "프로필")]', "login 전송 오류")

        if self.driver.find_elements(By.XPATH, '//*[text() = "나중에 하기"]'):
            self.driver.find_element(By.XPATH, '//*[text() = "나중에 하기"]').click()

    # json 로딩 : json 모듈 (requests로 가져오면 차단당할것 같음)
    def get_json(self, link):

        self.driver.get(link)
        self.wait_for('//pre', "link 타임아웃")
        # pre 태그 안에 있는 json 코드 가져오기
        pre = self.driver.find_elements(By.XPATH, '//pre')
        string = pre[0].get_attribute("textContent")

        # dash_manifest 때문에 json 코드 로딩이 안됨
        if "MPD" in string:
            string_ = string.replace('\\n', "").replace(',"video_dash_manifest":', '</MPD>"')
            if "dash_manifest" in string_ and '"dash_manifest":null' not in string_:
                string_ = string_.replace(',"dash_manifest":', '</MPD>"')

            a = string_.split('</MPD>"')
            string = ""
            for i in a:
                if "<" not in i:
                    string += i

        if "invalid" not in string or "error" not in string:
            return json.loads(string)

        # 쿼리 해시 잘못되었을 때
        else:
            alarm("error", "hash invalid", [])
            os.system("pause")

    # 포스트 체크
    def check_post(self):

        data = self.get_json(self.main_page + end_link)

        # 로그인 풀려있을 때"
        if "edge_related_profiles" in data["graphql"]["user"]:
            alarm("error", "No login", [])
            os.system("pause")

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
    def get_post(self, post):
        latest_link, upload_time = post[0], post[1]
        data = self.get_json("https://www." + latest_link + end_link)["items"][0]
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

    # reel json 페이지 확인
    def check_story(self):
        full = self.get_json(story_graph)

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

    def get_story(self, got_story):
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



