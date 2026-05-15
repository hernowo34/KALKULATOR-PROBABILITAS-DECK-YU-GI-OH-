import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import threading

from api_client import cari_kartu_ygoprodeck, download_gambar_kartu, format_data_kartu_untuk_deck
from deck.manager import inisialisasi_deck, tambah_kartu, hapus_kartu, hitung_total_kartu, dapatkan_kuantitas
from file_io import simpan_json, muat_json
from utils import hitung_peluang, hitung_peluang_minimal

class YuGiOhProbApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kalkulator Probabilitas Yu-Gi-Oh!")
        self.geometry("1100x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.deck_aktif = inisialisasi_deck()
        self.kartu_pencarian_terpilih = None # Menyimpan data kartu dari API yang sedang dipilih
        self.kartu_gambar_cache = {} # Cache gambar agar tidak download berulang

        self.inisialisasi_ui()
        self.refresh_deck_list()

    def inisialisasi_ui(self):
        # Konfigurasi grid utama (3 kolom)
        self.grid_columnconfigure(0, weight=1) # Panel Kiri: Deck
        self.grid_columnconfigure(1, weight=1) # Panel Tengah: Pencarian & Gambar
        self.grid_columnconfigure(2, weight=2) # Panel Kanan: Probabilitas
        self.grid_rowconfigure(0, weight=1)

        # ==================== PANEL KIRI (DECK) ====================
        self.frame_kiri = ctk.CTkFrame(self)
        self.frame_kiri.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.lbl_deck_title = ctk.CTkLabel(self.frame_kiri, text="Isi Deck", font=("Arial", 18, "bold"))
        self.lbl_deck_title.pack(pady=10)

        self.textbox_deck = ctk.CTkTextbox(self.frame_kiri, state="disabled")
        self.textbox_deck.pack(expand=True, fill="both", padx=10, pady=5)

        self.frame_deck_btn = ctk.CTkFrame(self.frame_kiri, fg_color="transparent")
        self.frame_deck_btn.pack(fill="x", padx=10, pady=10)

        self.btn_hapus = ctk.CTkButton(self.frame_deck_btn, text="Hapus Kartu", fg_color="red", hover_color="darkred", command=self.hapus_kartu_dialog)
        self.btn_hapus.pack(side="left", expand=True, padx=2)

        self.btn_save = ctk.CTkButton(self.frame_deck_btn, text="Save JSON", command=self.simpan_deck)
        self.btn_save.pack(side="left", expand=True, padx=2)

        self.btn_load = ctk.CTkButton(self.frame_deck_btn, text="Load JSON", command=self.muat_deck)
        self.btn_load.pack(side="left", expand=True, padx=2)

        # ==================== PANEL TENGAH (PENCARIAN) ====================
        self.frame_tengah = ctk.CTkFrame(self)
        self.frame_tengah.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.lbl_cari_title = ctk.CTkLabel(self.frame_tengah, text="Cari Kartu (API)", font=("Arial", 18, "bold"))
        self.lbl_cari_title.pack(pady=10)

        self.frame_search_input = ctk.CTkFrame(self.frame_tengah, fg_color="transparent")
        self.frame_search_input.pack(fill="x", padx=10)

        self.entry_cari = ctk.CTkEntry(self.frame_search_input, placeholder_text="Nama Kartu...")
        self.entry_cari.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.entry_cari.bind("<Return>", lambda event: self.cari_kartu())

        self.btn_cari = ctk.CTkButton(self.frame_search_input, text="Cari", width=60, command=self.cari_kartu)
        self.btn_cari.pack(side="right")

        self.lbl_status_cari = ctk.CTkLabel(self.frame_tengah, text="", text_color="yellow")
        self.lbl_status_cari.pack(pady=5)

        # Dropdown/OptionMenu untuk hasil pencarian (jika lebih dari 1)
        self.combo_hasil = ctk.CTkOptionMenu(self.frame_tengah, values=["- Hasil Pencarian -"], command=self.pilih_kartu_dari_hasil)
        self.combo_hasil.pack(fill="x", padx=10, pady=5)
        self.hasil_pencarian_data = []

        # Area Gambar Kartu
        self.lbl_gambar = ctk.CTkLabel(self.frame_tengah, text="[Gambar Kartu]", width=200, height=290, fg_color="gray30")
        self.lbl_gambar.pack(pady=15)

        # Area Detail Singkat
        self.lbl_detail_kartu = ctk.CTkLabel(self.frame_tengah, text="-", justify="left")
        self.lbl_detail_kartu.pack(pady=5, padx=10, fill="x")

        # Tombol Tambah ke Deck
        self.frame_tambah_qty = ctk.CTkFrame(self.frame_tengah, fg_color="transparent")
        self.frame_tambah_qty.pack(fill="x", padx=10, pady=10)

        self.lbl_qty = ctk.CTkLabel(self.frame_tambah_qty, text="Qty:")
        self.lbl_qty.pack(side="left", padx=5)

        self.combo_qty = ctk.CTkOptionMenu(self.frame_tambah_qty, values=["1", "2", "3"], width=60)
        self.combo_qty.pack(side="left", padx=5)

        self.btn_tambah = ctk.CTkButton(self.frame_tambah_qty, text="Tambah ke Deck", fg_color="green", hover_color="darkgreen", command=self.tambah_ke_deck)
        self.btn_tambah.pack(side="right", expand=True, fill="x", padx=5)

        # ==================== PANEL KANAN (PROBABILITAS) ====================
        self.frame_kanan = ctk.CTkFrame(self)
        self.frame_kanan.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.lbl_prob_title = ctk.CTkLabel(self.frame_kanan, text="Kalkulasi Probabilitas", font=("Arial", 18, "bold"))
        self.lbl_prob_title.pack(pady=10)

        self.frame_draw = ctk.CTkFrame(self.frame_kanan, fg_color="transparent")
        self.frame_draw.pack(fill="x", padx=10, pady=5)

        self.lbl_draw = ctk.CTkLabel(self.frame_draw, text="Jumlah Draw (n):")
        self.lbl_draw.pack(side="left", padx=5)

        self.entry_draw = ctk.CTkEntry(self.frame_draw, width=60)
        self.entry_draw.insert(0, "5")
        self.entry_draw.pack(side="left", padx=5)

        self.btn_hitung = ctk.CTkButton(self.frame_draw, text="Hitung Peluang", command=self.hitung_probabilitas)
        self.btn_hitung.pack(side="right", padx=5)

        self.textbox_hasil = ctk.CTkTextbox(self.frame_kanan, state="disabled", font=("Courier", 12))
        self.textbox_hasil.pack(expand=True, fill="both", padx=10, pady=10)


    def refresh_deck_list(self):
        self.textbox_deck.configure(state="normal")
        self.textbox_deck.delete("0.0", "end")
        
        main_total = hitung_total_kartu(self.deck_aktif, "Main Deck")
        extra_total = hitung_total_kartu(self.deck_aktif, "Extra Deck")
        
        teks = f"Total Main Deck: {main_total}/60\n"
        teks += f"Total Extra Deck: {extra_total}/15\n\n"

        kategori_dict = {}
        for nama, data in self.deck_aktif.items():
            kat = data.get('kategori', 'Lainnya')
            if kat not in kategori_dict:
                kategori_dict[kat] = []
            kategori_dict[kat].append((nama, data))

        for kat in ["Main Deck", "Extra Deck"]:
            if kat in kategori_dict:
                teks += f"--- {kat.upper()} ---\n"
                kartu_list = kategori_dict[kat]
                kartu_list.sort(key=lambda x: (x[1].get('tipe', ''), x[0]))
                for nama, data in kartu_list:
                    teks += f"- {data['kuantitas']}x {nama} [{data['tipe']}]\n"
                teks += "\n"

        self.textbox_deck.insert("0.0", teks)
        self.textbox_deck.configure(state="disabled")

    def cari_kartu(self):
        keyword = self.entry_cari.get().strip()
        if not keyword:
            return
        
        self.lbl_status_cari.configure(text="Mencari...", text_color="yellow")
        self.btn_cari.configure(state="disabled")

        # Menggunakan thread agar GUI tidak freeze saat hit API
        def task():
            hasil = cari_kartu_ygoprodeck(keyword)
            self.after(0, self.update_hasil_pencarian, hasil)

        threading.Thread(target=task, daemon=True).start()

    def update_hasil_pencarian(self, hasil):
        self.btn_cari.configure(state="normal")
        self.hasil_pencarian_data = hasil
        
        if not hasil:
            self.lbl_status_cari.configure(text="Kartu tidak ditemukan!", text_color="red")
            self.combo_hasil.configure(values=["- Kosong -"])
            self.combo_hasil.set("- Kosong -")
            self.kartu_pencarian_terpilih = None
            self.lbl_gambar.configure(image=None, text="[Not Found]")
            self.lbl_detail_kartu.configure(text="-")
        else:
            self.lbl_status_cari.configure(text=f"Ditemukan {len(hasil)} hasil", text_color="green")
            nama_list = [k['name'] for k in hasil]
            self.combo_hasil.configure(values=nama_list)
            self.combo_hasil.set(nama_list[0])
            self.pilih_kartu_dari_hasil(nama_list[0])

    def pilih_kartu_dari_hasil(self, nama_terpilih):
        kartu = next((k for k in self.hasil_pencarian_data if k['name'] == nama_terpilih), None)
        if kartu:
            self.kartu_pencarian_terpilih = format_data_kartu_untuk_deck(kartu)
            
            # Tampilkan detail teks
            tipe = self.kartu_pencarian_terpilih['tipe']
            kat = self.kartu_pencarian_terpilih['kategori']
            detail_teks = f"{tipe} | {kat}\n"
            if tipe == "Monster":
                detail_teks += f"Atribut: {self.kartu_pencarian_terpilih['atribut']}\n"
                detail_teks += f"ATK: {self.kartu_pencarian_terpilih['atk']} / DEF: {self.kartu_pencarian_terpilih['def']}\n"
            
            self.lbl_detail_kartu.configure(text=detail_teks)

            # Download dan tampilkan gambar
            img_url = self.kartu_pencarian_terpilih['image_url']
            if img_url:
                if img_url in self.kartu_gambar_cache:
                    self.tampilkan_gambar(self.kartu_gambar_cache[img_url])
                else:
                    self.lbl_gambar.configure(image=None, text="Loading Image...")
                    def download_task():
                        pil_img = download_gambar_kartu(img_url)
                        if pil_img:
                            self.kartu_gambar_cache[img_url] = pil_img
                            self.after(0, self.tampilkan_gambar, pil_img)
                        else:
                            self.after(0, lambda: self.lbl_gambar.configure(text="Image Failed"))
                    threading.Thread(target=download_task, daemon=True).start()

    def tampilkan_gambar(self, pil_image):
        # Resize gambar proporsional
        basewidth = 200
        wpercent = (basewidth / float(pil_image.size[0]))
        hsize = int((float(pil_image.size[1]) * float(wpercent)))
        img_resized = pil_image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
        
        ctk_image = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(basewidth, hsize))
        self.lbl_gambar.configure(image=ctk_image, text="")
        # Menyimpan referensi agar tidak di-garbage collect
        self.lbl_gambar.image = ctk_image

    def tambah_ke_deck(self):
        if not self.kartu_pencarian_terpilih:
            messagebox.showwarning("Peringatan", "Pilih kartu dari hasil pencarian terlebih dahulu!")
            return
            
        kategori = self.kartu_pencarian_terpilih['kategori']
        qty_tambah = int(self.combo_qty.get())
        nama = self.kartu_pencarian_terpilih['nama']

        qty_sekarang = dapatkan_kuantitas(self.deck_aktif, nama)
        if qty_sekarang + qty_tambah > 3:
            messagebox.showerror("Error", f"Maksimal 3 copy per kartu tercapai untuk '{nama}'.\n(Saat ini ada {qty_sekarang})")
            return

        total_kini = hitung_total_kartu(self.deck_aktif, kategori)
        limit = 60 if kategori == "Main Deck" else 15
        
        if total_kini + qty_tambah > limit:
            messagebox.showerror("Error", f"{kategori} penuh! (Limit: {limit})")
            return

        tambah_kartu(
            deck=self.deck_aktif,
            nama=nama,
            tipe=self.kartu_pencarian_terpilih['tipe'],
            atribut=self.kartu_pencarian_terpilih['atribut'],
            level_rank=self.kartu_pencarian_terpilih['level_rank'],
            atk=self.kartu_pencarian_terpilih['atk'],
            def_score=self.kartu_pencarian_terpilih['def'],
            kuantitas=qty_tambah,
            kategori=kategori,
            image_url=self.kartu_pencarian_terpilih['image_url']
        )
        
        self.refresh_deck_list()
        self.lbl_status_cari.configure(text=f"Berhasil ditambah: {qty_tambah}x {nama}", text_color="green")

    def hapus_kartu_dialog(self):
        dialog = ctk.CTkInputDialog(text="Masukkan Nama Kartu yang ingin dihapus:", title="Hapus Kartu")
        nama = dialog.get_input()
        if nama:
            if hapus_kartu(self.deck_aktif, nama):
                self.refresh_deck_list()
                messagebox.showinfo("Sukses", f"Kartu '{nama}' dihapus dari deck.")
            else:
                messagebox.showwarning("Gagal", f"Kartu '{nama}' tidak ditemukan di deck.")

    def simpan_deck(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json", 
            filetypes=[("JSON Files", "*.json")],
            title="Simpan Deck"
        )
        if filepath:
            simpan_json(self.deck_aktif, filepath)
            messagebox.showinfo("Sukses", "Deck berhasil disimpan!")

    def muat_deck(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Load Deck"
        )
        if filepath:
            self.deck_aktif = muat_json(filepath)
            self.refresh_deck_list()
            messagebox.showinfo("Sukses", "Deck berhasil diload!")

    def hitung_probabilitas(self):
        total_kartu = hitung_total_kartu(self.deck_aktif, "Main Deck")
        if total_kartu == 0:
            messagebox.showerror("Error", "Main Deck kosong. Tambahkan kartu terlebih dahulu.")
            return

        try:
            n = int(self.entry_draw.get())
            if n <= 0 or n > total_kartu:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Jumlah draw (n) tidak valid!")
            return

        self.textbox_hasil.configure(state="normal")
        self.textbox_hasil.delete("0.0", "end")

        header = f"{'Nama Kartu':<30} | {'Qty':<3} | {'P(>=1)':<7} | {'P(1)':<6} | {'P(2)':<6}\n"
        self.textbox_hasil.insert("end", f"Total Deck (N): {total_kartu} | Draw (n): {n}\n")
        self.textbox_hasil.insert("end", "-"*65 + "\n")
        self.textbox_hasil.insert("end", header)
        self.textbox_hasil.insert("end", "-"*65 + "\n")

        main_deck_items = [(nama, data) for nama, data in self.deck_aktif.items() if data.get('kategori') == 'Main Deck']
        main_deck_items.sort(key=lambda x: x[0])

        for nama, data in main_deck_items:
            K = data['kuantitas']
            p1 = hitung_peluang(total_kartu, K, n, 1)
            p2 = hitung_peluang(total_kartu, K, n, 2)
            p_min1 = hitung_peluang_minimal(total_kartu, K, n, 1)

            nama_cetak = nama if len(nama) <= 30 else nama[:27] + "..."
            baris = f"{nama_cetak:<30} | {K:<3} | {p_min1*100:>6.1f}% | {p1*100:>5.1f}% | {p2*100:>5.1f}%\n"
            self.textbox_hasil.insert("end", baris)

        self.textbox_hasil.configure(state="disabled")

if __name__ == "__main__":
    app = YuGiOhProbApp()
    app.mainloop()
