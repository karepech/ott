import requests
import xml.etree.ElementTree as ET
import re
import traceback

M3U_URL = "https://raw.githubusercontent.com/jrpahe-del/IPTV/refs/heads/main/RafaDervian.m3u"
EPG_URL = "https://raw.githubusercontent.com/AqFad2811/epg/main/indonesia.xml"
OUTPUT_FILE = "indonesia_synced.m3u"

def clean_name(name):
    if not name: return ""
    name = re.sub(r'(?i)\b(HD|FHD|SD|4K|1080p|720p)\b', '', str(name))
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

def main():
    try:
        print("1. Mengunduh data EPG...")
        epg_response = requests.get(EPG_URL, timeout=30)
        epg_response.raise_for_status()
        root = ET.fromstring(epg_response.content)

        epg_data = {}
        for channel in root.findall('channel'):
            ch_id = channel.get('id')
            display_name_elem = channel.find('display-name')
            if ch_id and display_name_elem is not None and display_name_elem.text:
                name = display_name_elem.text.strip()
                cleaned = clean_name(name)
                epg_data[cleaned] = {'id': ch_id, 'name': name}

        print("2. Mengunduh data M3U...")
        m3u_response = requests.get(M3U_URL, timeout=30)
        m3u_response.raise_for_status()
        lines = m3u_response.text.splitlines()

        output_lines = ["#EXTM3U"]
        matched_count = 0
        total_indo = 0
        
        # Variabel untuk menampung baris-baris satu channel utuh
        current_block = []
        
        print("3. Memproses blok per channel...")
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.upper().startswith("#EXTM3U"):
                continue # Skip header pertama
                
            # Kumpulkan semua baris ke dalam blok
            current_block.append(line)
            
            # Jika baris ini BUKAN diawali '#', berarti ini adalah link URL stream.
            # Artinya, SATU BLOK CHANNEL SUDAH SELESAI dan siap diproses.
            if not line.startswith("#"):
                
                # Cari di mana posisi baris #EXTINF di dalam blok ini
                extinf_index = -1
                for idx, b_line in enumerate(current_block):
                    if b_line.upper().startswith("#EXTINF"):
                        extinf_index = idx
                        break
                
                # Jika baris #EXTINF ditemukan
                if extinf_index != -1:
                    extinf_line = current_block[extinf_index]
                    
                    # Cek apakah ini kategori Indonesia
                    if re.search(r'group-title="[^"]*Indonesia[^"]*"', extinf_line, re.IGNORECASE):
                        total_indo += 1
                        
                        # Ekstrak nama channel
                        parts = extinf_line.split(',')
                        original_name = parts[-1].strip()
                        cleaned_name = clean_name(original_name)
                        
                        # Jika nama cocok dengan EPG, lakukan sinkronisasi
                        if cleaned_name in epg_data:
                            ch_id = epg_data[cleaned_name]['id']
                            epg_name = epg_data[cleaned_name]['name']
                            
                            # Hapus tvg-id lama dan ganti dengan yang baru
                            extinf_line = re.sub(r'tvg-id="[^"]*"', '', extinf_line)
                            extinf_line = extinf_line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-id="{ch_id}"')
                            
                            # Ganti nama channel dengan nama dari EPG
                            base_extinf = ",".join(parts[:-1])
                            extinf_line = f"{base_extinf},{epg_name}"
                            
                            # Bersihkan spasi berlebih
                            extinf_line = re.sub(r'\s+', ' ', extinf_line).replace(' ,', ',')
                            
                            matched_count += 1
                        
                        # Update baris #EXTINF di dalam blok dengan yang sudah disinkronisasi
                        current_block[extinf_index] = extinf_line
                        
                        # Masukkan SELURUH blok channel (termasuk EXTVLCOPT dan URL) ke output
                        output_lines.extend(current_block)
                
                # Kosongkan blok untuk mulai membaca channel berikutnya
                current_block = []

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
