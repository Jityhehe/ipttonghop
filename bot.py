import requests
from datetime import datetime, timedelta

FILENAME = "all_matches.m3u"
# User-Agent bạn muốn sử dụng
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": UA}

def process_standard(url, provider_name, emoji_group):
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
                            'group': emoji_group,
                            'title': f"{nickname}" if nickname else item.get('title'),
                            'full_title': f"{dt_vn.strftime('%H:%M')} | {item.get('title')} ({nickname})",
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
                    'group': "🔴 ⚽ VÕNG CAM TV",
                    'title': item.get('title'),
                    'full_title': f"{dt_vn.strftime('%H:%M')} | {item.get('title')}",
                    'logo': item.get('homeClub', {}).get('logoUrl', ''),
                    'url': stream_url
                })
    except: pass
    return fixtures

if __name__ == "__main__":
    # Lấy dữ liệu
    hq = process_standard("https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished", "HoiQuanTV", "🔴 ⚽ HỘI QUÁN TV")
    td = process_standard("https://sv.thiendinhtv.xyz/api/v1/external/fixtures/unfinished", "ThienDinhTV", "🔴 ⚽ THIÊN ĐỊNH TV")
    vc = process_vongcam()

    all_sources = [hq, td, vc]

    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        for source_data in all_sources:
            source_data.sort(key=lambda x: x['time'])
            for item in source_data:
                # Dòng 1: Thông tin kênh và Group
                f.write(f'#EXTINF:-1 group-title="{item["group"]}" tvg-logo="{item["logo"]}", {item["full_title"]}\n')
                # Dòng 2: Option User-Agent theo đúng định dạng bạn yêu cầu
                f.write(f'#EXTVLCOPT:http-user-agent={UA}\n')
                # Dòng 3: Link stream
                f.write(f'{item["url"]}\n')
            
    print(f"Đã tạo file {FILENAME} theo định dạng EXTVLCOPT thành công!")
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
