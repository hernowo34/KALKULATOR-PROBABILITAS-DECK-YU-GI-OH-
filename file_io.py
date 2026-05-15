import json
import os
import csv

def simpan_json(data_dict, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, indent=4)

def muat_json(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def simpan_csv(data_dict, filepath):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["Nama", "Tipe", "Atribut", "Level_Rank", "ATK", "DEF", "Kuantitas", "Kategori"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for nama, data in data_dict.items():
            baris = {"Nama": nama}
            baris.update(data)
            writer.writerow(baris)

def simpan_laporan_txt(teks_laporan, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(teks_laporan)

def daftar_file(ekstensi, direktori='.'):
    if not os.path.exists(direktori):
        return []
    return [f for f in os.listdir(direktori) if f.endswith(ekstensi)]