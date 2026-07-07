import requests
from datetime import datetime, timedelta

# Cấu hình chung
FILENAME = "all_matches.m3u"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": UA}

# Cấu hình Referer tương ứng cho từng nhóm để vượt tường lửa CDN
REFERER_MAP = {
    "🔴 ⚽ HỘI QUÁN TV": "https://hoiquantv.xyz/",
    "🔴 ⚽ THIÊN ĐÌNH TV": "https://hoiquantv.xyz/",  # Dùng chung hạ tầng với Hội Quán
    "🔴 ⚽ VÒNG CẤM TV": "https://vongcam.tv/"
}

def process_standard(url, provider_name, emoji_group):
    fixtures = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=15).json()
        for item in res.get('data', []):
            dt_vn = datetime.max
            if item.get('startTime'):
                dt_vn = datetime.strptime(item['startTime'][:19], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=7)
            
            # Lọc lấy link từ commentator
            for comm_entry in item.get('fixtureCommentators', []):
                comm_data = comm_entry.get('commentator', {})
                nickname = comm_data.get('nickname', '')
                
                for s in comm_data.get('streams', []):
                    s_name = s.get('name', '').upper()
                    
                    # Phân loại độ phân giải dựa trên tên stream
                    quality = ""
                    if "FHD" in s_name or "FULLHD" in s_name:
                        quality = "FHD"
                    elif "HD" in s_name:
                        quality = "HD"
                    elif "SD" in s_name or "MOBILE" in s_name:
                        quality = "SD"
                    
                    # Nếu đúng các định dạng trên thì lưu lại
                    if quality and s.get('sourceUrl'):
                        fixtures.append({
                            'time': dt_vn,
                            'group': emoji_group,
                            'title': f"{dt_vn.strftime('%H:%M')} | [{quality}] {item.get('title')} ({nickname})",
                            'logo': item.get('homeTeam', {}).get('logoUrl', ''),
                            'url': s.get('sourceUrl')
                        })
    except Exception as e:
        pass
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
            
            comm = item.get('commentator', {})
            # Quét qua cả 3 chất lượng luồng phát của Vòng Cấm
            streams = {
                'FHD': comm.get('streamSourceFhd'),
                'HD': comm.get('streamSourceHd'),
                'SD': comm.get('streamSourceSd')
            }
            
            for q_name, stream_url in streams.items():
                if stream_url:
                    fixtures.append({
                        'time': dt_vn,
                        'group': "🔴 ⚽ VÒNG CẤM TV",
                        'title': f"{dt_vn.strftime('%H:%M')} | [{q_name}] {item.get('title')}",
                        'logo': item.get('homeClub', {}).get('logoUrl', ''),
                        'url': stream_url
                    })
    except Exception as e:
        pass
    return fixtures

if __name__ == "__main__":
    print("Đang thu thập dữ liệu trận đấu...")
    
    # Lấy dữ liệu từ các nguồn
    hq = process_standard("https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished", "HoiQuanTV", "🔴 ⚽ HỘI QUÁN TV")
    td = process_standard("https://sv.hoiquantv.xyz/api/v1/external/fixtures/unfinished", "ThienDinhTV", "🔴 ⚽ THIÊN ĐÌNH TV")
    vc = process_vongcam()

    all_data = hq + td + vc
    
    # Sắp xếp lịch thi đấu tăng dần theo thời gian
    all_data.sort(key=lambda x: x['time'])

    print(f"Tìm thấy {len(all_data)} luồng phát. Đang tiến hành ghi file M3U...")

    # Tiến hành ghi file M3U theo định dạng nâng cao
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in all_data:
            # Lấy đúng mã Referer bảo mật của từng nhà đài
            ref = REFERER_MAP.get(item["group"], "https://google.com")
            
            # Ghi thông tin thẻ tên và logo
            f.write(f'#EXTINF:-1 group-title="{item["group"]}" tvg-logo="{item["logo"]}", {item["title"]}\n')
            
            # Giữ lại EXTVLCOPT để hỗ trợ tốt cho VLC / PotPlayer trên Máy tính
            f.write(f'#EXTVLCOPT:http-user-agent={UA}\n')
            f.write(f'#EXTVLCOPT:http-referer={ref}\n')
            
            # NỐI ĐUÔI BẰNG DẤU | : Ép các app IPTV trên Android TV (TiviMate, OTT Navigator) gửi Header đi kèm
            final_url = f"{item['url']}|User-Agent={UA}&Referer={ref}"
            f.write(f'{final_url}\n')
            
    print(f"Thành công! Đã tạo file: {FILENAME}")
