from flask import Flask, render_template, request,jsonify
from googleapiclient.discovery import build
from flask_cors import CORS,cross_origin
import pandas as pd
app = Flask(__name__)

@app.route('/', methods=("POST", "GET"))
@cross_origin()
def yt_scrapping():
    api_key = 'AIzaSyCyDyT32dJHEkLcdMhsZ0k0TAlC-VHPc-U'
    channel_id = 'UCphU2bAGmw304CFAzy0Enuw'
    youtube=build('youtube','v3',developerKey = api_key)
    request=youtube.channels().list(part='snippet,contentDetails,statistics',id =channel_id)
    response = request.execute()
    data =dict(Playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
    Playlist_id = data['Playlist_id']
    def get_video_ids(youtube,Playlist_id):
        video_ids = []
        request = youtube.playlistItems().list(part = 'contentDetails',playlistId = Playlist_id,maxResults = 5)
        response = request.execute()
        for i in range (len(response['items'])):
            video_ids.append(response['items'][i]['contentDetails']['videoId'])
        return video_ids    
    video_ids = get_video_ids(youtube,Playlist_id)
    def get_video_details(youtube,video_ids):
        all_video_stats=[]
        request =  youtube.videos().list(part = "snippet,statistics", id = ','.join(video_ids[:5]))
        response = request.execute()
        for video in response['items']:
            video_stats = dict(Url= "https://www.youtube.com/watch?v=" + video['id'],
                                Title = video['snippet']['title'],
                                    Published_date = video['snippet']['publishedAt'],
                                    Thumbnails = video['snippet']['thumbnails']['standard']['url'],
                                    Views = video['statistics']['viewCount']
                                                                        )
            all_video_stats.append(video_stats)
                                        
        return all_video_stats   
                
    Video_details = get_video_details(youtube,video_ids)
    Video_data = pd.DataFrame(Video_details)
    Video_data = Video_data.set_index([pd.Index([1,2,3,4,5])])
    #Video_data = Video_data.reset_index()
    Video_data.to_csv('Video_Details_PW_Foundation.csv')
    data_final=pd.read_csv('Video_Details_PW_Foundation.csv',index_col=0)
    return render_template('results.html', tables=[data_final.to_html()], titles=[''])
                    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000,debug=True)
