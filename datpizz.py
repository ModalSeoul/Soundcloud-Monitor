import requests
from time import sleep
from bs4 import BeautifulSoup


class SCMonitor:
    """
    This does a few things:
        - Iterates over a list of Soundcloud profiles
        and fires an event when one uploads a new track.
        - Multiple gateways of alerting user (Discord, sms, email, etc)

        Written by Carter for datpizz.com - 12/27/16
    """

    def __init__(self, interval, artists):
        self.artists = artists
        self.interval = interval

        self.last_scan = []

    def scan(self):
        scan = []
        for artist in self.artists:
            songs = []

            r = requests.get(self._track_url(artist))

            tracks = BeautifulSoup(r.content, 'html.parser')
            track_list = BeautifulSoup(str(tracks.find_all(
                'noscript')[1].contents[0]), 'html.parser')
            track_list = track_list.find_all('article')

            for track in track_list:
                song_title = track.find_all('a')[0].text.strip()
                link = track.find_all('a', href=True)[0]
                songs.append('https://soundcloud.com%s' % link['href'])
            scan.append(songs)
        self._set_last_scan(scan)
        return scan

    def run(self):
        while 1:
            results = self.scan()
            for idx, artist in enumerate(results):
                difference = self._cmp(results[idx], self.last_scan[idx])

                if difference:
                    print(difference)

            sleep(self.interval)

    def get_interval(self):
        return self.interval

    def _track_url(self, artist):
        return 'https://soundcloud.com/%s/tracks' % artist

    def _set_last_scan(self, scan):
        if not self.last_scan:
            self.last_scan = scan

    def _cmp(self, a, b):
        return list(set(a) - set(b))

if __name__ == '__main__':
    SC = SCMonitor(5, ['datpizz', 'correyparks'])
    SC.run()
