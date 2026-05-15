def inisialisasi_deck():
    return {}

def cari_key_asli(deck, nama_input):
    for key in deck.keys():
        if key.lower() == nama_input.strip().lower():
            return key
    return None

def dapatkan_kuantitas(deck, nama):
    key = cari_key_asli(deck, nama)
    if key: return deck[key]['kuantitas']
    return 0

def tambah_kartu(deck, nama, tipe, atribut, level_rank, atk, def_score, kuantitas, kategori, image_url=""):
    key_asli = cari_key_asli(deck, nama)
    if key_asli:
        deck[key_asli]["kuantitas"] += kuantitas
        return key_asli
    else:
        nama_format = nama.strip().title()
        deck[nama_format] = {
            "tipe": tipe,
            "atribut": atribut,
            "level_rank": level_rank,
            "atk": atk,
            "def": def_score,
            "kuantitas": kuantitas,
            "kategori": kategori,
            "image_url": image_url
        }
        return nama_format

def hapus_kartu(deck, nama):
    key_asli = cari_key_asli(deck, nama)
    if key_asli:
        del deck[key_asli]
        return True
    return False

def cari_kartu(deck, keyword):
    hasil = {}
    for nama, data in deck.items():
        if keyword.lower() in nama.lower():
            hasil[nama] = data
    return hasil

def hitung_total_kartu(deck, kategori="Main Deck"):
    total = 0
    for data in deck.values():
        if data["kategori"] == kategori:
            total += data["kuantitas"]
    return total

def tampilkan_isi_deck(deck):
    if not deck:
        print("Deck masih kosong.")
        return
        
    kategori_dict = {}
    for nama, data in deck.items():
        kat = data.get('kategori', 'Lainnya')
        if kat not in kategori_dict:
            kategori_dict[kat] = []
        kategori_dict[kat].append((nama, data))
        
    for kat, kartu_list in kategori_dict.items():
        print(f"\n--- {kat.upper()} ---")
        
        def sort_key(item):
            n = item[0]
            t = item[1].get('tipe', '').title()
            group = 0
            if 'Spell' in t: group = 1
            elif 'Trap' in t: group = 2
            
            if kat.lower() == 'extra deck':
                return (group, t, n)
            return (group, n)
            
        kartu_list.sort(key=sort_key)
        
        for nama, data in kartu_list:
            tipe_cetak = data.get('tipe', '').title()
            if kat.lower() == 'main deck' and tipe_cetak not in ['Spell', 'Trap']:
                tipe_cetak = 'Monster'
            print(f"- {data['kuantitas']}x {nama} [{tipe_cetak}]")
            
    print("----------------")