import json
from functions import *
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# 로그인 필요해서 request로 못가져옴 -> 셀레니움 이용해서 json 얻기
class GetDataChrome:
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

        self.driver.get(main_page)
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

    # json 로딩 : json 모듈
    def get_json(self, link):

        self.driver.get(link)
        self.wait_for('//pre', "link 타임아웃")
        # pre 태그 안에 있는 json 코드 가져오기
        pre = self.driver.find_elements(By.XPATH, '//pre')
        string = pre[0].get_attribute("textContent")

        # dash_manifest 때문에 json 코드 로딩이 안될때 처리
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