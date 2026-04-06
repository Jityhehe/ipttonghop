import requests
from datetime import datetime, timedelta

FILENAME = "all_matches.m3u"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def process_standard(url, provider_name):
    fixtures = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=15).json()
        for item in res.get('data', []):
            dt_vn = datetime.max
            if item.get('startTime'):
                dt_vn = datetime.strptime(item['startTime'][:19], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=7)
            
            for comm_entry in item.get('fixtureCommentators', []):
                comm_data = comm_entry.get('commentator', {})
                nickname = comm_data.get('nickname', '')
                for s in comm_data.get('streams', []):
                    s_name = s.get('name', '').upper()
                    if "FHD" in s_name or "FULLHD" in s_name:
                        fixtures.append({
                            'time': dt_vn,
                            'group': provider_name,
                            'title': f"{item.get('title')} ({nickname})" if nickname else item.get('title'),
                            'logo': item.get('homeTeam', {}).get('logoUrl', ''),
                            'url': s.get('sourceUrl')
                        })
                        break
    except: pass
    return fixtures

def process_vongcam():
    url = "https://sv.bugiotv.xyz/internal/api/matches"
    fixtures = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=15).json()
        for item in res.get('data', []):
            dt_vn = datetime.max
            if item.get('startTime'):
                dt_vn = datetime.strptime(item['startTime'][:19], '%Y-%m-%dT%H:%M:%S')
            
            stream_url = item.get('commentator', {}).get('streamSourceFhd')
            if stream_url:
                fixtures.append({
                    'time': dt_vn,
                    'group': "VongcamTV",
                    'title': item.get('title'),
                    'logo': item.get('homeClub', {}).get('logoUrl', ''),
                    'url': stream_url
                })
    except: pass
    return fixtures

if __name__ == "__main__":
    sources = [
        {"name": "HoiQuanTV", "data": process_standard("https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished", "HoiQuanTV")},
        {"name": "ThienDinhTV", "data": process_standard("https://sv.thiendinhtv.xyz/api/v1/external/fixtures/unfinished", "ThienDinhTV")},
        {"name": "VongcamTV", "data": process_vongcam()}
    ]

    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        for source in sources:
            source['data'].sort(key=lambda x: x['time'])
            for item in source['data']:
                time_str = item['time'].strftime('%H:%M') if item['time'] != datetime.max else "Live"
                # Cấu trúc EXTINF chuẩn nhất cho mọi App
                inf_line = (f'#EXTINF:-1 tvg-logo="{item["logo"]}" '
                            f'group-title="{source["name"]}", '
                            f'{time_str} | {item["title"]}\n')
                f.write(inf_line)
                f.write(f"{item['url']}|User-Agent={HEADERS['User-Agent']}\n")
            
    print(f"Cập nhật thành công!")
