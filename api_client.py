import requests
import io
from PIL import Image

def cari_kartu_ygoprodeck(keyword):
    """
    Mencari kartu berdasarkan kata kunci.
    Mengembalikan list berisi dictionary data kartu yang cocok, atau list kosong jika gagal/tidak ditemukan.
    """
    url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?fname={keyword}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            return []
    except Exception as e:
        print(f"Error mengakses API: {e}")
        return []

def download_gambar_kartu(image_url):
    """
    Mendownload gambar dari URL dan mengembalikan object Image PIL.
    """
    try:
        # Menambahkan User-Agent karena beberapa API memblokir permintaan bot default
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, stream=True, timeout=10)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        return None
    except Exception as e:
        print(f"Error mendownload gambar: {e}")
        return None

def format_data_kartu_untuk_deck(api_card_data, kuantitas=1):
    """
    Mengubah format data dari API ke format dictionary yang sesuai dengan struktur kalkulator deck kita.
    """
    nama = api_card_data.get('name', 'Unknown')
    tipe_raw = api_card_data.get('type', '')
    
    # Menentukan kategori deck
    kategori = "Main Deck"
    if any(x in tipe_raw.lower() for x in ['fusion', 'synchro', 'xyz', 'link']):
        kategori = "Extra Deck"
        
    # Menentukan tipe (Monster, Spell, Trap)
    if 'Spell' in tipe_raw:
        tipe = 'Spell'
    elif 'Trap' in tipe_raw:
        tipe = 'Trap'
    else:
        tipe = 'Monster'
        
    # Atribut, Level/Rank, ATK, DEF
    atribut = api_card_data.get('attribute', api_card_data.get('race', 'Unknown')).upper()
    
    level_rank = "-"
    if 'level' in api_card_data:
        level_rank = str(api_card_data['level'])
    elif 'linkval' in api_card_data:
        level_rank = str(api_card_data['linkval']) # Untuk Link Monster
        
    atk = str(api_card_data.get('atk', '-'))
    def_score = str(api_card_data.get('def', '-'))

    # Ambil URL gambar pertama
    image_url = ""
    card_images = api_card_data.get('card_images', [])
    if card_images:
        image_url = card_images[0].get('image_url', '')

    return {
        "nama": nama,
        "tipe": tipe,
        "atribut": atribut,
        "level_rank": level_rank,
        "atk": atk,
        "def": def_score,
        "kuantitas": kuantitas,
        "kategori": kategori,
        "image_url": image_url
    }
