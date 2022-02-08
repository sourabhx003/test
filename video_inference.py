import cv2
import os
import boto3
# import concurrent.futures
import threading
import time
import requests
from collections import Counter
from datetime import datetime

RTSP_URL = "rtsp://ai1.sstlive.com:1935/live/6J07E0CPAZ4A8AE"
ACCESS_KEY = "sfj"
SECRET_KEY = 'hfsj'
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
model = 'arn:aws:rekognition:ap-south-1:666009661528:project/PersonEvmCoombined06feb/version/PersonEvmCoombined06feb.2022-02-06T13.00.42/1644132640501'


def get_people_and_alert(model,photo, min_confidence):
    client=boto3.client('rekognition',region_name='ap-south-1',aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,)

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'Bytes': photo},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)
#     print(response['CustomLabels'])
    lists = []
    for data in response['CustomLabels']:
        lists.append(data["Name"])
    count = dict(Counter(lists))
#     print(count.get('person',0))
    people_count = count.get('person',0)
    evm_alert = count.get('evm_alert',0)
    return people_count,evm_alert


def main(url:str,num:int):
    stream_id = url.split('/')[-1]
    print(f"Detecting in {stream_id} {num}")
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    
    cap.set(3,640)#width
    cap.set(4,480)#height
    cap.set(cv2.CAP_PROP_BUFFERSIZE,3)
    start_frame_number = 20
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number)
    if not cap.isOpened():
        print(f'Cannot open RTSP stream {stream_id}')
        return
    lrt = time.time()
    while True:

        _, frame = cap.read()
        crt = time.time()
        if lrt + 1.0 > crt:
            lrt = time.time()
            # print(frame.shape)
            # print(frame)
            frame = cv2.resize(frame,(640,480),cv2.INTER_CUBIC)
            encoded_img = cv2.imencode('.jpg', frame)[1].tobytes()
            people,alert = get_people_and_alert(model,encoded_img,50)
            print(stream_id,people,alert)

            today_date = datetime.today().strftime('%Y/%m/%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            requests.post(f"http://alertdata.sstlive.com/api/headcount?date={today_date}&time={current_time}&stream_id={stream_id}&count={people}")
            if alert != 0:
                requests.post(f"http://alertdata.sstlive.com/api/evmalert?date={today_date}&{current_time}&stream_id={stream_id}&alert=1")
            
            continue
    
    cap.release()

if __name__ =='__main__':
    url_list = ["rtsp://ai1.sstlive.com:1935/live/6J07E0CPAZ4A8AE",
        "rtsp://ai1.sstlive.com:1935/live/6J07E0CPAZ018A2",
        "rtsp://ai1.sstlive.com:1935/live/6J07E0CPAZ84010",
        "rtsp://ai1.sstlive.com:1935/live/6J07E0CPAZBC3AA",
        "rtsp://ai1.sstlive.com:1935/live/6J07E0CPAZD8D1F",
        "rtsp://ai1.sstlive.com:1935/live/6J07E0CPAZ4CA5D"
        ] 

    # with concurrent.futures.ProcessPoolExecutor(max_workers=len(url_list)) as exe:
    #     results = [exe.submit(main, url, num) for num, url in enumerate(url_list)]
    #     for f in concurrent.futures.as_completed(results):
    #         print(f.result())
    #     # main(RTSP_URL)
    #     cv2.destroyAllWindows()
    for index,url in enumerate(url_list):
        t1 = threading.Thread(target=main, args=(url,index))
        # t2 = threading.Thread(target=getPicture, args=(rtsp1,))

        t1.start()
        # t2.start()
        # main(url_list[0],1)