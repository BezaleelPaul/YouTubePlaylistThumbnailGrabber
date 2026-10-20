import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import ytda

THREAD_COUNT = 10


def getAllPlaylistVideoIds(client, playlistId):
    results = []
    pageToken = None
    working = True
    while working:
        response = ytda.playlist_items_list_by_playlist_id(
            client,
            part="snippet,contentDetails",
            maxResults=50,
            pageToken=pageToken,
            playlistId=playlistId,
        )
        if "nextPageToken" in response:
            pageToken = response.get("nextPageToken")
        else:
            working = False
        for video in response.get("items"):
            result = video.get("contentDetails").get("videoId")
            results.append(result)
    return results


def getThumbnailUrl(videoId):
    return "http://img.youtube.com/vi/" + videoId + "/default.jpg"


def downloadThumbnail(videoId, index, total):
    try:
        data = urllib.request.urlopen(getThumbnailUrl(videoId)).read()
        with open("results/" + videoId + ".jpg", "wb") as f:
            f.write(data)
        print(videoId + " " + str(index) + "/" + str(total))
    except Exception as e:
        print("Failed to download thumbnail for " + videoId + ": " + str(e))


def main():
    playlistId = input("Enter Playlist Id")
    print(playlistId)
    videoIds = getAllPlaylistVideoIds(ytda.client, playlistId)
    total = len(videoIds)
    if not os.path.isdir("results"):
        os.makedirs("results")
    pool = ThreadPoolExecutor(max_workers=min(THREAD_COUNT, total) or 1)
    for i in range(total):
        pool.submit(downloadThumbnail, videoIds[i], i + 1, total)
    pool.shutdown(wait=True)
    print("Done")


if __name__ == "__main__":
    main()
