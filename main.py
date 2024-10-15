
import json
import time
import argparse
import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


from utils import reserve, get_user_credentials
get_current_time = lambda action: time.strftime("%H:%M:%S", time.localtime(time.time() + 8*3600)) if action else time.strftime("%H:%M:%S", time.localtime(time.time()))
get_current_dayofweek = lambda action: time.strftime("%A", time.localtime(time.time() + 8*3600)) if action else time.strftime("%A", time.localtime(time.time()))


SLEEPTIME = 0.0 # 每次抢座的间隔
ENDTIME = "15:40:00" # 根据学校的预约座位时间+1min即可

ENABLE_SLIDER = False # 是否有滑块验证
MAX_ATTEMPT = 100 # 最大尝试次数
RESERVE_NEXT_DAY = False # 预约明天而不是今天的

                
def main(users, action=False):
    current_time = get_current_time(action)
    logging.info(f"start time {current_time}, action {'on' if action else 'off'}")
    attempt_times = 0
    username, password = None, None
    if action:
        username, password = get_user_credentials(action)
    else:
        username, password = users["username"], users["password"]
    current_dayofweek = get_current_dayofweek(action)
    if current_dayofweek not in users["daysofweek"]:
        logging.info("Today not set to reserve")
        return
    success = False
    s = reserve(sleep_time=SLEEPTIME, max_attempt=MAX_ATTEMPT, enable_slider=ENABLE_SLIDER, reserve_next_day=RESERVE_NEXT_DAY)
    s.get_login_status()
    s.login(username, password)
    while current_time < ENDTIME:
        _, _, times, roomid, seatid, _ = users.values()
        s.requests.headers.update({'Host': 'office.chaoxing.com'})
        reserve_res = s.submit(times, roomid, seatid, action)
        success = reserve_res
        print(f"attempt time {attempt_times}, time now {current_time}, success {success}")
        current_time = get_current_time(action)
        if success:
            break
    if success:
        print(f"success reserve.")  
    else:
        print(f"out of reserve time.")

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    parser = argparse.ArgumentParser(prog='Chao Xing seat auto reserve')
    parser.add_argument('-u','--user', default=config_path, help='user config file')
    parser.add_argument('-m','--method', default="reserve" ,choices=["reserve", "debug", "room"], help='for debug')
    parser.add_argument('-a','--action', action="store_true",help='use --action to enable in github action')
    args = parser.parse_args()
    func_dict = {"reserve": main}
    with open(args.user, "r+") as data:
        usersdata = json.load(data)["reserve"][0]
    func_dict[args.method](usersdata, args.action)
