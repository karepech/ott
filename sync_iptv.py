import requests
import xml.etree.ElementTree as ET
import re
import os

M3U_URL = "https://raw.githubusercontent.com/jrpahe-del/IPTV/refs/heads/main/RafaDervian.m3u"
EPG_URL = "https://raw.githubusercontent.com/AqFad2811/epg/main/indonesia.xml"
OUTPUT_FILE = "indonesia_synced.m3u"

def clean_name(name):
    # Menghapus karakter khusus dan spasi agar pencocokan nama lebih akurat
    return re.sub(r'[^a-zA-Z0-9]', '', str(name)).lower()

def main():
    print("Mengunduh data EPG...")
    epg_response = requests.get(EPG_URL)
    epg_response.raise_for_status()
    root = ET.fromstring(epg_response.content)

    # Memetakan nama channel EPG ke ID EPG-nya
    epg_map = {}
    epg_names = {}
    for channel in root.findall('channel'):
        ch_id = channel.get('id')
        for display_name in channel.findall('display-name'):
            name = display_name.text
            if name:
                cleaned = clean_name(name)
                epg_map[cleaned] = ch_id
                epg_names[cleaned] = name

    print("Mengunduh data M3U...")
    m3u_response = requests.get(M3U_URL)
    m3u_response.raise_for_status()
    lines = m3u_response.text.splitlines()

    output_lines = ["#EXTM3U"]
    i = 0

    print("Memfilter kategori Indonesia dan menyinkronkan EPG...")
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            # Filter hanya yang memiliki group-title="Indonesia"
            if re.search(r'group-title="[^"]*Indonesia[^"]*"', line, re.IGNORECASE):
                # Ekstrak nama channel saat ini (setelah koma terakhir)
                channel_name = line.split(',')[-1].strip()
                cleaned_ch_name = clean_name(channel_name)
                
                # Jika nama channel M3U cocok dengan EPG XML
                if cleaned_ch_name in epg_map:
                    ch_id = epg_map[cleaned_ch_name]
                    epg_name = epg_names[cleaned_ch_name]
                    
                    # Update atau tambahkan tvg-id agar EPG bisa tayang
                    if 'tvg-id="' in line:
                        line = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{ch_id}"', line)
                    else:
                        line = line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-id="{ch_id}"')
                    
                    # Ubah nama channel di playlist agar persis sama dengan nama di EPG
                    line = re.sub(r',.*$', f',{epg_name}', line)
                
                output_lines.append(line)
                
                # Ambil URL stream yang biasanya ada di baris tepat di bawah #EXTINF
                if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                    output_lines.append(lines[i + 1])
        i += 1

    # Simpan sebagai file baru
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"Selesai! File disimpan sebagai {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
                  
