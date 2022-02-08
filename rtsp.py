import cv2
import os
import boto3
 
RTSP_URL = "rtsp://ai1.sstlive.com:1935/live/6J07E0CPAZ4A8AE"
 
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
model = 'arn:aws:rekognition:ap-south-1:666009661528:project/PersonEvmCoombined06feb/version/PersonEvmCoombined06feb.2022-02-06T13.00.42/1644132640501'
def show_custom_labels(model,photo, min_confidence):
    client=boto3.client('rekognition',region_name='ap-south-1')

    #Call DetectCustomLabels
    response = client.detect_custom_labels(Image={'Bytes': photo},
        MinConfidence=min_confidence,
        ProjectVersionArn=model)
#     print(response['CustomLabels'])

    return len(response['CustomLabels'])
 
cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
 
if not cap.isOpened():
    print('Cannot open RTSP stream')
    exit(-1)
 
while True:
    _, frame = cap.read()
    # cv2.imshow('RTSP stream', frame)
    frame = cv2.resize(frame,(640,480),cv2.INTER_CUBIC)
    frame = cv2.imencode('.jpg', frame)[1].tobytes()
    print(show_custom_labels(model,frame,50))
 
    if cv2.waitKey(1) == 27:
        break
 
cap.release()
cv2.destroyAllWindows()