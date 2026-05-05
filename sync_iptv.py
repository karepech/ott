import requests
import xml.etree.ElementTree as ET
import re
import traceback

M3U_URL = "https://raw.githubusercontent.com/jrpahe-del/IPTV/refs/heads/main/RafaDervian.m3u"
EPG_URL = "https://raw.githubusercontent.com/AqFad2811/epg/main/indonesia.xml"
OUTPUT_FILE = "indonesia_synced.m3u"

def clean_name(name):
    """Membersihkan nama channel dari simbol dan spasi agar mudah dicocokkan"""
    if not name:
        return ""
    # Hapus kata-kata resolusi yang sering bikin gagal cocok
    name = re.sub(r'(?i)\b(HD|FHD|SD|4K|1080p|720p)\b', '', str(name))
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

def main():
    try:
        print("1. Mengunduh data EPG...")
        epg_response = requests.get(EPG_URL, timeout=30)
        epg_response.raise_for_status()
        root = ET.fromstring(epg_response.content)

        # Map EPG: clean_name -> { 'id': tvg-id, 'name': Nama Resmi EPG }
        epg_data = {}
        for channel in root.findall('channel'):
            ch_id = channel.get('id')
            display_name_elem = channel.find('display-name')
            if ch_id and display_name_elem is not None and display_name_elem.text:
                name = display_name_elem.text.strip()
                cleaned = clean_name(name)
                epg_data[cleaned] = {'id': ch_id, 'name': name}

        print(f"   Ditemukan {len(epg_data)} channel di EPG.")

        print("2. Mengunduh data M3U...")
        m3u_response = requests.get(M3U_URL, timeout=30)
        m3u_response.raise_for_status()
        lines = m3u_response.text.splitlines()

        output_lines = ["#EXTM3U"]
        matched_count = 0
        total_indo = 0

        print("3. Memfilter & Menyinkronkan...")
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Jika baris adalah info channel
            if line.startswith("#EXTINF"):
                # Cek apakah ini channel kategori Indonesia
                if re.search(r'group-title="[^"]*Indonesia[^"]*"', line, re.IGNORECASE):
                    total_indo += 1
                    
                    # Ambil nama channel di M3U (teks setelah koma terakhir)
                    parts = line.split(',')
                    original_name = parts[-1].strip()
                    cleaned_name = clean_name(original_name)

                    # Jika nama channel M3U ada di database EPG kita
                    if cleaned_name in epg_data:
                        ch_id = epg_data[cleaned_name]['id']
                        epg_name = epg_data[cleaned_name]['name']
                        
                        # 1. Hapus tvg-id lama jika ada, lalu pasang tvg-id yang baru dari EPG
                        line = re.sub(r'tvg-id="[^"]*"', '', line) # Hapus yang lama
                        line = line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-id="{ch_id}"')
                        
                        # 2. Ganti nama channel di ujung baris dengan nama resmi dari EPG
                        # Gabungkan kembali semua bagian sebelum koma terakhir, lalu tambahkan epg_name
                        base_extinf = ",".join(parts[:-1])
                        line = f"{base_extinf},{epg_name}"
                        
                        # Bersihkan spasi ganda yang mungkin terjadi
                        line = re.sub(r'\s+', ' ', line).replace(' ,', ',')
                        
                        matched_count += 1
                    
                    # Masukkan baris #EXTINF yang sudah diolah
                    output_lines.append(line)
                    
                    # Masukkan baris URL stream di bawahnya (biasanya baris berikutnya)
                    if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                        output_lines.append(lines[i + 1])
            i += 1

        # 4. Simpan ke file output
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

        print(f"Selesai! Berhasil memfilter {total_indo} channel Indonesia.")
        print(f"Berhasil menyinkronkan {matched_count} channel dengan EPG.")
        print(f"File disimpan sebagai: {OUTPUT_FILE}")

    except Exception as e:
        print(f"Terjadi error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
