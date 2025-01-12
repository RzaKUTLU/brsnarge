import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import io
import xlsxwriter
import base64
import time

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """

st.set_page_config(page_title="Borsan Ar-Ge Yemek Sipariş Sistemi", layout="wide")

# CSS stillerini güncelle
st.markdown(
    """
    <style>
    /* Ana arka plan */
    .stApp {
        background-image: url("https://cdn.wallpapersafari.com/5/24/IvSYOt.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Başlıklar için stil */
    h1, h2, h3 {
        color: white !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        text-shadow: 
            2px 2px 0 #000,
            -2px 2px 0 #000,
            2px -2px 0 #000,
            -2px -2px 0 #000,
            0 2px 0 #000,
            0 -2px 0 #000,
            2px 0 0 #000,
            -2px 0 0 #000 !important;
    }

    /* Alt başlıklar için özel boyut */
    h2 { font-size: 1.8rem !important; }
    h3 { font-size: 1.5rem !important; }

    /* Normal metin için stil */
    p, label, span, .stMarkdown {
        color: white !important;
        font-weight: 500 !important;
        font-size: 1.2rem !important;
        text-shadow: 
            1.5px 1.5px 0 #000,
            -1.5px 1.5px 0 #000,
            1.5px -1.5px 0 #000,
            -1.5px -1.5px 0 #000 !important;
    }

    /* Parıltı efekti için stil */
    .sparkle {
        position: fixed;
        border-radius: 50%;
        background-color: white;
        box-shadow: 0 0 10px 2px rgba(255, 255, 255, 0.3);
        pointer-events: none;
        opacity: 0;
        z-index: 9999;
    }

    /* 60 farklı parıltı için stil ve animasyon */
    .sparkle:nth-child(1) { width: 8px; height: 8px; animation: sparkleRandom1 3s infinite; }
    .sparkle:nth-child(2) { width: 6px; height: 6px; animation: sparkleRandom2 4s infinite; }
    .sparkle:nth-child(3) { width: 7px; height: 7px; animation: sparkleRandom3 5s infinite; }
    .sparkle:nth-child(4) { width: 5px; height: 5px; animation: sparkleRandom4 6s infinite; }
    .sparkle:nth-child(5) { width: 4px; height: 4px; animation: sparkleRandom5 3.5s infinite; }
    .sparkle:nth-child(6) { width: 6px; height: 6px; animation: sparkleRandom6 4.5s infinite; }
    .sparkle:nth-child(7) { width: 7px; height: 7px; animation: sparkleRandom7 5.5s infinite; }
    .sparkle:nth-child(8) { width: 5px; height: 5px; animation: sparkleRandom8 3.2s infinite; }
    .sparkle:nth-child(9) { width: 6px; height: 6px; animation: sparkleRandom9 4.2s infinite; }
    .sparkle:nth-child(10) { width: 8px; height: 8px; animation: sparkleRandom10 5.2s infinite; }
    /* ... diğer parıltılar için benzer tanımlamalar ... */

    /* Parıltı animasyonları */
    @keyframes sparkleRandom1 { 0% { transform: translate(5vw, 5vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(95vw, 95vh); opacity: 0; }}
    @keyframes sparkleRandom2 { 0% { transform: translate(95vw, 5vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(5vw, 95vh); opacity: 0; }}
    @keyframes sparkleRandom3 { 0% { transform: translate(50vw, 0vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(50vw, 100vh); opacity: 0; }}
    @keyframes sparkleRandom4 { 0% { transform: translate(0vw, 50vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(100vw, 50vh); opacity: 0; }}
    @keyframes sparkleRandom5 { 0% { transform: translate(25vw, 75vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(75vw, 25vh); opacity: 0; }}
    @keyframes sparkleRandom6 { 0% { transform: translate(75vw, 25vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(25vw, 75vh); opacity: 0; }}
    @keyframes sparkleRandom7 { 0% { transform: translate(10vw, 90vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(90vw, 10vh); opacity: 0; }}
    @keyframes sparkleRandom8 { 0% { transform: translate(90vw, 90vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(10vw, 10vh); opacity: 0; }}
    @keyframes sparkleRandom9 { 0% { transform: translate(30vw, 70vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(70vw, 30vh); opacity: 0; }}
    @keyframes sparkleRandom10 { 0% { transform: translate(60vw, 40vh); opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(40vw, 60vh); opacity: 0; }}
    /* ... diğer animasyonlar için benzer tanımlamalar ... */

    /* Metric değeri için stil */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: white !important;
        font-weight: 700 !important;
        text-shadow: 
            2px 2px 0 #000,
            -2px 2px 0 #000,
            2px -2px 0 #000,
            -2px -2px 0 #000,
            0 2px 0 #000,
            0 -2px 0 #000,
            2px 0 0 #000,
            -2px 0 0 #000 !important;
    }

    /* Metric delta değeri için stil (eğer varsa) */
    [data-testid="stMetricDelta"] {
        color: white !important;
        font-weight: 500 !important;
        text-shadow: 
            1px 1px 0 #000,
            -1px 1px 0 #000,
            1px -1px 0 #000,
            -1px -1px 0 #000 !important;
    }

    /* Sepete Ekle butonu için yeşil stil */
    button[data-testid="baseButton-secondary"]:contains("Sepete Ekle") {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

    /* Sil butonu için kırmızı stil */
    button[data-testid="baseButton-secondary"]:contains("Sil") {
        background-color: #dc3545 !important;
        color: white !important;
        border: none !important;
    }

    /* Siparişleri Temizle butonu için kırmızı stil */
    button[data-testid="baseButton-secondary"]:contains("Siparişleri Temizle") {
        background-color: #dc3545 !important;
        color: white !important;
        border: none !important;
    }

    /* Hover efekti */
    button[data-testid="baseButton-secondary"]:hover {
        opacity: 0.8 !important;
        transition: opacity 0.2s !important;
    }
    </style>

    <!-- 60 adet parıltı elementi -->
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <div class="sparkle"></div>
    <!-- ... diğer parıltı elementleri ... -->
    """,
    unsafe_allow_html=True
)

# Başlığın hemen altına bu kodu ekleyin (st.title() satırından sonra)
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://cdn.wallpapersafari.com/5/24/IvSYOt.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Metin okunabilirliği için arka plan overlay'i */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7); /* Yarı saydam siyah overlay */
        z-index: -1;
    }
    
    /* Metin rengini beyaz yapın */
    .stMarkdown, .stTitle, h1, h2, h3, p, .stMetric {
        color: white !important;
    }
    
    /* Sidebar stilini düzenleyin */
    .css-1d391kg {
        background-color: rgba(0, 0, 0, 0.5);
    }
    
    /* Cart item stilini güncelleyin */
    .cart-item {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# CSS stillerini güncelleyelim - Input alanları için belirgin stil ekleyerek
st.markdown("""
<style>
    /* Sidebar ana container */
    section[data-testid="stSidebar"] > div {
        background-color: white !important;
    }
    
    /* Sidebar içindeki tüm yazı elementleri */
    section[data-testid="stSidebar"] * {
        color: black !important;
        text-shadow: none !important;
        font-weight: normal !important;
    }
    
    /* Sidebar butonları için özel stil */
    section[data-testid="stSidebar"] button {
        background-color: #f0f2f6 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 4px !important;
        padding: 4px 12px !important;
        margin: 4px 0 !important;
        color: black !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }

    /* Buton hover efekti */
    section[data-testid="stSidebar"] button:hover {
        background-color: #e0e2e6 !important;
        border-color: #d0d0d0 !important;
    }
    
    /* Input alanları için belirgin stil */
    section[data-testid="stSidebar"] input[type="text"],
    section[data-testid="stSidebar"] input[type="number"],
    section[data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: white !important;
        border: 1px solid #ccc !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
        margin: 4px 0 !important;
        width: 100% !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }

    /* Input focus efekti */
    section[data-testid="stSidebar"] input[type="text"]:focus,
    section[data-testid="stSidebar"] input[type="number"]:focus,
    section[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
        border-color: #80bdff !important;
        box-shadow: 0 0 0 2px rgba(0,123,255,0.25) !important;
        outline: none !important;
    }

    /* Email linki için özel stil */
    section[data-testid="stSidebar"] a[href^="mailto:"] {
        color: #0066cc !important;
        text-decoration: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Ana sayfa düzenini güncelle
st.markdown('<div class="card"><h1 align="center">🍽️ Borsan Ar-Ge Yemek Sipariş Sistemi</h1></div>', unsafe_allow_html=True)

# Sidebar'ı gizle ve ana sayfada minimal tutun
with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("⚙️ Yönetim")
    
    # Mevcut yönetim seçenekleri...
    
    st.markdown("---")  # Ayırıcı çizgi
    
    # Hakkında butonu
    if st.button("ℹ️ Hakkında"):
        st.markdown("""
        ### 🍽️ Borsan Ar-Ge Yemek Sipariş Sistemi

        **Versiyon:** 2.0
        
        **Uygulama Çıkış Tarihi:**
        * 10.20.2024
        **Uygulama Son Güncelleme:** 
        * 12.01.2025

        **Geliştirmeler:**
        * 📦 Çoklu sipariş
        * 🔒 Güvenlik
        * ✨ Animasyon - UI

        **Özellikler:**
        * 🍽️ Restoran ve menü yönetimi
        * 🛒 Çoklu yemek siparişi
        * 📝 Sipariş notu ekleme
        * 💰 Otomatik fiyat hesaplama
        * 📊 Kişi bazlı raporlama
        * 📥 Excel rapor indirme
        * 🗑️ Sipariş silme ve düzenleme
        * ⚡ Anlık sipariş takibi

        **Geliştirici:** RK
        
        **İletişim:** rizakutlu@borsan.com.tr

        **Amaç:** 
        * ⏱️ Borsan Ar-Ge personellerinin yemek siparişi sırasında gereksiz zaman kaybının önüne geçilmesi

        © 2024 Borsan Ar-Ge
        """)
    # ... sidebar içeriği ...
    st.markdown('</div>', unsafe_allow_html=True)

# Ana içerik alanını düzenle
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🛒 Sipariş Ver")
    # ... sipariş formu ...
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📋 Günlük Siparişler")
    # ... siparişler listesi ...
    st.markdown('</div>', unsafe_allow_html=True)

# SQLite veritabanı bağlantısı
conn = sqlite3.connect('siparisler.db')

# Siparişler tablosunu oluştur
def create_table():
    conn.execute('''
    CREATE TABLE IF NOT EXISTS siparisler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih TEXT,
        isim TEXT,
        restoran TEXT,
        yemek TEXT,
        fiyat REAL,
        adet INTEGER,
        notlar TEXT
    )
    ''')
    conn.commit()

create_table()


# Excel indirme fonksiyonu
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Siparişler', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Siparişler']

        # Format ayarları
        para_format = workbook.add_format({'num_format': '#,##0.00 ₺'})
        tarih_format = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})

        # Sütun genişliklerini ayarla
        worksheet.set_column('A:A', 20)  # Tarih sütunu
        worksheet.set_column('B:B', 15)  # İsim sütunu
        worksheet.set_column('C:C', 15)  # Restoran sütunu
        worksheet.set_column('D:D', 15)  # Yemek sütunu
        worksheet.set_column('E:E', 12)  # Fiyat sütunu
        worksheet.set_column('F:F', 12)  # Adet sütunu
        worksheet.set_column('G:G', 12)  # Notlar sütunu

        # Fiyat sütununa format uygula
        worksheet.set_column('E:E', 12, para_format)

    return output.getvalue()

# Restoranları sakla
if 'restoranlar' not in st.session_state:
    st.session_state.restoranlar = {
        'Nazar Petrol': {
            'Adana Dürüm': 170,
            'Adana Porsiyon': 240,
            'Tavuk Dürüm': 155,
            'Kanat Porsiyon': 200,
            'Tavuk Porsiyon': 150,
            'Yarım Tavuk': 130,
            'Yarım Çeyrek Tavuk': 150,
            'Bütün Ekmek Tavuk': 170,
            'Ciğer Dürüm': 170,
            'Ciğer Porsiyon': 240,
            'Et Dürüm': 190,
            'Et Porsiyon': 270,
            'Köfte Porsiyon': 240,
            'Yarım Köfte': 170,
            'Yarım Çeyrek Köfte': 170,
            'Bütün Köfte': 190,
            'Kapalı Pide': 90,
            'Lahmacun': 80,
            'Açık Kıymalı': 170,
            'Açık Kaşarlı': 180,
            'Açık Karışık': 220,
            'Açık Sucuklu': 230,
            'Kuşbaşı Pide': 230,
            'Açık Pastırmalı': 230,
            'Açık Beyaz Peynirli': 190,
            'Kapalı Beyaz Peynirli': 170,
            'Yağlı': 140,
            'Extra Lavaş': 10,
            'Extra Yumurta': 10,
            'Extra Kaşar': 25,
            'Çoban Salata': 30,
            'Ezme': 20,
            'Patlıcan Salatası': 50,
            'Tropicana M. Suyu': 35,
            '2.5 Lt Kola': 70,
            '1 Lt Kola': 50,
            'Kutu Kola': 35,
            'Şalgam': 30,
            'Şişe Kola': 50,
            '1 Lt Fanta': 50,
            '2.5 Lt Fanta': 70,
            'Kutu Fanta': 30,
            'Sprite': 30,
            'Şişe Zero': 40,
            'Türk Kahvesi': 40,
            'Su': 5,
            'Çay': 10,
            'Ice Tea Şeftali': 35,
            'Açık Ayran': 35,
            'Ayran Pet': 35,
            'Ayran Şişe': 35,
            'Portakal Suyu': 35,
            'Künefe': 85,
            'Sütlaç': 75,
            'Katmer': 75
            # ... Diğer yemekler burada
        },
        'Çalıkuşu Kirazlık': {
            'Tavuk Dürüm Ç.lavaş Döner(100gr)': 160,
            'Tavuk Dürüm Döner(50gr)': 80,
            'Et Dürüm Döner': 140,
            'Pepsi kola kutu': 40,
            'Kola': 30,
            'Ayran': 25,
            'Ice tea şeftali': 40
            # ... Diğer yemekler burada
        }
    }

# Başlık
st.title("🍽️ Borsan Ar-Ge Yemek Sipariş Sistemi")

# Sidebar - Yeni Restoran ve Menü Ekleme
with st.sidebar:
    st.header("Restoran Yönetimi")

    # Yeni restoran ekleme
    new_restaurant = st.text_input("Yeni Restoran")
    if st.button("Restoran Ekle") and new_restaurant:
        if new_restaurant not in st.session_state.restoranlar:
            st.session_state.restoranlar[new_restaurant] = {}
            st.success(f"{new_restaurant} başarıyla eklendi!")
        else:
            st.error("Bu restoran zaten mevcut!")

    # Mevcut restorana yemek ekleme
    st.subheader("Menü Yönetimi")
    restaurant_select = st.selectbox("Restoran Seçin", options=list(st.session_state.restoranlar.keys()))

    new_item = st.text_input("Yemek")
    new_price = st.number_input("Fiyat (TL)", min_value=0, value=0)

    if st.button("Menüye Ekle") and new_item and new_price > 0:
        st.session_state.restoranlar[restaurant_select][new_item] = new_price
        st.success(f"{new_item} menüye eklendi!")

# Ana sayfa - Sipariş verme
col1, col2 = st.columns([1.2, 1])  # Sütun oranlarını değiştir

with col1:
    st.header("Sipariş Ver")

    # Kullanıcı bilgileri
    isim = st.text_input("Adınız")
    secilen_restoran = st.selectbox("Restoran", options=list(st.session_state.restoranlar.keys()))

    if secilen_restoran:
        # Çoklu yemek seçimi için container
        with st.container():
            st.subheader("Yemek Seçimi")
            
            # Session state'i başlat
            if 'siparisler' not in st.session_state:
                st.session_state.siparisler = []
            
            # Yeni yemek ekleme formu
            with st.form(key='yemek_form'):
                secilen_yemek = st.selectbox(
                    "Yemek",
                    options=list(st.session_state.restoranlar[secilen_restoran].keys())
                )
                
                fiyat = st.session_state.restoranlar[secilen_restoran][secilen_yemek]
                st.write(f"Fiyat: {fiyat} TL")
                
                adet = st.number_input("Adet", min_value=1, value=1)
                not_girisi = st.text_input("Not")
                
                submit_button = st.form_submit_button("Sepete Ekle")
                if submit_button:
                    st.session_state.siparisler.append({
                        'yemek': secilen_yemek,
                        'adet': adet,
                        'fiyat': fiyat * adet,
                        'not': not_girisi
                    })
                    st.success(f"{secilen_yemek} sepete eklendi!")

        # Sepeti göster
        if st.session_state.siparisler:
            st.subheader("Sepetiniz")
            for i, siparis in enumerate(st.session_state.siparisler):
                col_info, col_sil = st.columns([3, 1])
                with col_info:
                    st.write(f"{siparis['adet']}x {siparis['yemek']} - {siparis['fiyat']} TL")
                    if siparis['not']:
                        st.write(f"Not: {siparis['not']}")
                with col_sil:
                    if st.button("Sil", key=f"sil_{i}"):
                        st.session_state.siparisler.pop(i)
                        st.rerun()

            toplam = sum(s['fiyat'] for s in st.session_state.siparisler)
            st.write(f"**Toplam: {toplam} TL**")

            # Siparişi tamamla butonu
            if st.button("Siparişi Tamamla") and isim:
                for siparis in st.session_state.siparisler:
                    conn.execute('''
                        INSERT INTO siparisler (tarih, isim, restoran, yemek, fiyat, adet, notlar) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                        ((datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
                         isim,
                         secilen_restoran,
                         siparis['yemek'],
                         siparis['fiyat'],
                         siparis['adet'],
                         siparis['not'])
                    )
                conn.commit()
                st.session_state.siparisler = []  # Sepeti temizle
                st.success("❄️ Siparişiniz başarıyla alındı!")
                st.snow()  # Kar efekti
                time.sleep(2)
                st.rerun()

# Siparişleri görüntüleme
with col2:
    st.header("Günlük Siparişler")
    # Veritabanından tüm siparişleri oku
    df = pd.read_sql_query('SELECT * FROM siparisler', conn)

    if not df.empty:
        # Kişi bazlı toplam tutarlar
        st.subheader("Kişi Bazlı Toplam")
        kisi_bazli = df.groupby('isim')['fiyat'].sum().reset_index()
        st.dataframe(kisi_bazli)

        # Excel indirme butonları
        col_a, col_b = st.columns(2)

        with col_a:
            # Tüm siparişlerin Excel'i
            excel_data = to_excel(df)
            st.download_button(
                label="📥 Tüm Siparişleri İndir",
                data=excel_data,
                file_name=f'siparisler_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        with col_b:
            # Kişi bazlı toplamların Excel'i
            excel_data_summary = to_excel(kisi_bazli)
            st.download_button(
                label="📥 Özeti İndir",
                data=excel_data_summary,
                file_name=f'siparis_ozeti_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        # Tüm siparişler
        st.subheader("Tüm Siparişler")
        
        # Sipariş ID'lerini içeren bir dropdown oluştur
        selected_order_id = st.selectbox("Silmek için sipariş ID'sini seçin", options=df['id'].tolist())

        if st.button("Sil"):
            if selected_order_id:
                conn.execute('DELETE FROM siparisler WHERE id = ?', (selected_order_id,))
                conn.commit()
                st.success(f"{selected_order_id} ID'li sipariş silindi!")
                st.rerun()
            else:
                st.warning("Silmek için bir sipariş seçmelisiniz.")

        # Tüm siparişleri göster
        st.dataframe(df[['id', 'tarih', 'isim', 'restoran', 'yemek', 'adet', 'fiyat', 'notlar']])

        # Toplam tutar
        toplam_tutar = df['fiyat'].sum()
        st.metric("Toplam Tutar", f"{toplam_tutar} TL")

        # Siparişleri temizleme butonu
        if st.button("Siparişleri Temizle"):
            try:
                conn.execute('DELETE FROM siparisler')
                conn.commit()
                st.success("❄️ Tüm siparişler başarıyla silindi!")
                st.snow()  # Kar efekti
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Silme işlemi sırasında hata: {e}")
    else:
        st.info("Henüz sipariş bulunmamaktadır.")

# Sepet öğelerini özel div içine alın
if st.session_state.siparisler:
    for i, siparis in enumerate(st.session_state.siparisler):
        st.markdown(f'''
        <div class="cart-item">
            <p>{siparis['adet']}x {siparis['yemek']} - {siparis['fiyat']} TL</p>
            {f"<p><small>Not: {siparis['not']}</small></p>" if siparis['not'] else ""}
        </div>
        ''', unsafe_allow_html=True)
