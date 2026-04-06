import requests
from datetime import datetime, timedelta

# Cấu hình
FILENAME = "all_matches.m3u"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def process_standard(url, provider_name):
    """Xử lý HoiQuan và ThienDinh (Giờ UTC+7)"""
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
                            'group': provider_name, # Tên nhóm (HoiQuanTV hoặc ThienDinhTV)
                            'title': f"{item.get('title')} ({nickname})" if nickname else item.get('title'),
                            'logo': item.get('homeTeam', {}).get('logoUrl', ''),
                            'url': s.get('sourceUrl')
                        })
                        break
    except: pass
    return fixtures

def process_vongcam():
    """Xử lý Vongcam (Giờ VN gốc)"""
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
                    'group': "VongcamTV", # Tên nhóm riêng
                    'title': item.get('title'),
                    'logo': item.get('homeClub', {}).get('logoUrl', ''),
                    'url': stream_url
                })
    except: pass
    return fixtures

if __name__ == "__main__":
    # Lấy dữ liệu riêng từng nguồn
    hoiquan_data = process_standard("https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished", "HoiQuanTV")
    thiendinh_data = process_standard("https://sv.thiendinhtv.xyz/api/v1/external/fixtures/unfinished", "ThienDinhTV")
    vongcam_data = process_vongcam()

    # Sắp xếp theo giờ nội bộ từng nhóm (tùy chọn)
    hoiquan_data.sort(key=lambda x: x['time'])
    thiendinh_data.sort(key=lambda x: x['time'])
    vongcam_data.sort(key=lambda x: x['time'])

    # Ghi vào file M3U với phân nhóm rõ ràng
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        # Ghi nhóm HoiQuanTV
        for item in hoiquan_data:
            time_str = item['time'].strftime('%H:%M') if item['time'] != datetime.max else "Live"
            f.write(f"#EXTINF:-1 tvg-logo='{item['logo']}' group-title='HoiQuanTV', {time_str} | {item['title']}\n")
            f.write(f"{item['url']}|User-Agent={HEADERS['User-Agent']}\n")

        # Ghi nhóm ThienDinhTV
        for item in thiendinh_data:
            time_str = item['time'].strftime('%H:%M') if item['time'] != datetime.max else "Live"
            f.write(f"#EXTINF:-1 tvg-logo='{item['logo']}' group-title='ThienDinhTV', {time_str} | {item['title']}\n")
            f.write(f"{item['url']}|User-Agent={HEADERS['User-Agent']}\n")

        # Ghi nhóm VongcamTV
        for item in vongcam_data:
            time_str = item['time'].strftime('%H:%M') if item['time'] != datetime.max else "Live"
            f.write(f"#EXTINF:-1 tvg-logo='{item['logo']}' group-title='VongcamTV', {time_str} | {item['title']}\n")
            f.write(f"{item['url']}|User-Agent={HEADERS['User-Agent']}\n")
            
    print(f"Hoàn thành! Đã chia {len(hoiquan_data + thiendinh_data + vongcam_data)} trận vào 3 nhóm riêng biệt.")
