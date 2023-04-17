import psutil
from get_insta import *


def check_start():
    # 실행중인 디버깅 크롬 모두 종료
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
        except psutil.NoSuchProcess:
            pass
        else:
            if 'chrome' in pinfo['name'] and '--remote-debugging-port={}'.format(9222) in pinfo['cmdline']:
                proc.kill()

    # 디버거 크롬 재실행
    chrome = subprocess.Popen(
        r'C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 '
        r'--user-data-dir="C:\chrometemp"')

    check = InstaNoLogin()
    start_time, run_time = time.time(), 0

    while run_time < 43200:
        updates = check.check_post()

        for post in updates:
            check.get_post(post)

        story = check.check_story()
        if story is not None:
            check.get_story(story)

        now = time.strftime('%Y-%m-%d %H:%M:%S')
        print(now)
        if 3 <= int(now[11:13]) < 11:
            n = 300
        else:
            n = 100
        time.sleep(n)
        run_time = time.time() - start_time

    check.teardown()
    chrome.terminate()


while True:
    try:
        check_start()
    except Exception as ex:
        print(ex)
        requests.post(line_api_url, headers=line_headers, data={"message": f"에러발생 {ex}"})
        with open("./logs/log.txt", "a") as z:
            z.write(f"{ex}\n==============================================================\n")
        break
    print("==========restart==========")