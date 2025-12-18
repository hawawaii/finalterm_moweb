import os
import cv2
import pathlib
import requests
from datetime import datetime

class ChangeDetection:
    HOST = 'http://127.0.0.1:8000'
    username = 'admin'
    password = 'password'
    token = ''
    
    TARGET_CLASS = 'potted plant'

    last_state = -1 

    def __init__(self, names):
        self.result_prev = [0 for i in range(len(names))]
        try:
            res = requests.post(self.HOST + '/api-token-auth/', {
                'username': self.username,
                'password': self.password,
            })
            res.raise_for_status()
            self.token = res.json()['token']
        except Exception:
            pass

    def add(self, names, detected_current, save_dir, image):
        target_index = -1
        if isinstance(names, dict):
            for key, value in names.items():
                if value == self.TARGET_CLASS:
                    target_index = key
                    break
        elif isinstance(names, list):
            try:
                target_index = names.index(self.TARGET_CLASS)
            except ValueError:
                target_index = -1

        if target_index == -1:
            return

        detected_count = detected_current[target_index]
        current_state = 1 if detected_count > 0 else 0
        
        now = datetime.now()

        if current_state != self.last_state:
            
            if current_state == 1:
                msg = "Plant O"
            else:
                msg = "Plant X"
                
            print(f"[{now}] 상태 변화! ({self.last_state} -> {current_state}) : {msg}")
            
            self.last_state = current_state
            
            title = now.strftime("%Y_%m_%d_%H_%M")
            text = msg
            self.send(save_dir, image, title, text)

    def send(self, save_dir, image, title, text):
        try:
            now = datetime.now()
            today = datetime.now()
            
            save_path = os.getcwd() + "/" + str(save_dir) + '/plants/' + str(today.year) + "/" + str(today.month) + "/" + str(today.day)
            pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)
            
            full_path = save_path + '/{0}-{1}-{2}.jpg'.format(today.hour, today.minute, today.second)
            
            dst = cv2.resize(image, dsize=(640, 480), interpolation=cv2.INTER_AREA)
            cv2.imwrite(full_path, dst)
            
            headers = { 'Authorization': 'JWT ' + self.token, 'Accept': 'application/json' }
            
            data = {
                'author': 1,
                'title': title,
                'text': text,
                'created_date': now,
                'published_date': now
            }
            
            file = {'image': open(full_path, 'rb')}
            requests.post(self.HOST + '/api_root/Post/', data=data, files=file, headers=headers)
            print("업로드 성공")
            
        except Exception as e:
            print(f"업로드 실패: {e}")