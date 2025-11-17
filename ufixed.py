#!/usr/bin/env python3
"""
SHEERID ID CARD GENERATOR - ULTRA MEGA FAST - 2000+ IDs/MIN ⚡⚡⚡⚡⚡
✅ EXACT NAMES: Zero modifications to college names from JSON
✅ CURRENT DATES: Within 30 days for SheerID verification
✅ LARGE LOGO: Prominent 300x300 institution logo
✅ SAME FORMAT: STUDENTID_COLLEGEID.png + students.txt
✅ 24 COUNTRIES: US, CA, GB, IN, ID, AU, DE, FR, ES, IT, BR, MX, NL, SE, NO, DK, JP, KR, SG, NZ, ZA, CN, AE, PH
✅ ULTRA MEGA FAST: 5000 workers, 250 sessions, 1000 batch, photo cache, aggressive optimization
Updated: 2025-11-11 19:29:07 UTC
User: Adeebaabkhan
Target: 2000+ IDs per minute (10K in 5 minutes)
"""

import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests
from faker import Faker
import qrcode
import random
import json
from datetime import datetime, timedelta, timezone
from io import BytesIO
import time
import concurrent.futures
import threading
from functools import lru_cache
import gc

# ==================== CONFIGURATION ====================
COUNTRY_CONFIG = {
    'US': {
        'name': 'United States',
        'code': 'us',
        'locale': 'en-us',
        'collegeFile': 'sheerid_us.json',
        'currency': 'USD',
        'currency_symbol': '$',
        'academic_terms': ['Fall 2024', 'Spring 2025', 'Summer 2024'],
        'flag': '🇺🇸'
    },
    'CA': {
        'name': 'Canada',
        'code': 'ca',
        'locale': 'en-ca',
        'collegeFile': 'sheerid_ca.json',
        'currency': 'CAD',
        'currency_symbol': '$',
        'academic_terms': ['Fall 2024', 'Winter 2025', 'Summer 2024'],
        'flag': '🇨🇦'
    },
    'GB': {
        'name': 'United Kingdom',
        'code': 'gb',
        'locale': 'en-gb',
        'collegeFile': 'sheerid_gb.json',
        'currency': 'GBP',
        'currency_symbol': '£',
        'academic_terms': ['Autumn 2024', 'Spring 2025', 'Summer 2024'],
        'flag': '🇬🇧'
    },
    'IN': {
        'name': 'India',
        'code': 'in',
        'locale': 'en-in',
        'collegeFile': 'sheerid_in.json',
        'currency': 'INR',
        'currency_symbol': '₹',
        'academic_terms': ['Monsoon 2024', 'Winter 2025', 'Summer 2024'],
        'flag': '🇮🇳'
    },
    'ID': {
        'name': 'Indonesia',
        'code': 'id',
        'locale': 'id-id',
        'collegeFile': 'sheerid_id.json',
        'currency': 'IDR',
        'currency_symbol': 'Rp',
        'academic_terms': ['Semester 1 2024', 'Semester 2 2025', 'Summer 2024'],
        'flag': '🇮🇩'
    },
    'AU': {
        'name': 'Australia',
        'code': 'au',
        'locale': 'en-au',
        'collegeFile': 'sheerid_au.json',
        'currency': 'AUD',
        'currency_symbol': '$',
        'academic_terms': ['Semester 1 2024', 'Semester 2 2025', 'Summer 2024'],
        'flag': '🇦🇺'
    },
    'DE': {
        'name': 'Germany',
        'code': 'de',
        'locale': 'de-de',
        'collegeFile': 'sheerid_de.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Wintersemester 2024', 'Sommersemester 2025'],
        'flag': '🇩🇪'
    },
    'FR': {
        'name': 'France',
        'code': 'fr',
        'locale': 'fr-fr',
        'collegeFile': 'sheerid_fr.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Semestre 1 2024', 'Semestre 2 2025'],
        'flag': '🇫🇷'
    },
    'ES': {
        'name': 'Spain',
        'code': 'es',
        'locale': 'es-es',
        'collegeFile': 'sheerid_es.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Primer Semestre 2024', 'Segundo Semestre 2025'],
        'flag': '🇪🇸'
    },
    'IT': {
        'name': 'Italy',
        'code': 'it',
        'locale': 'it-it',
        'collegeFile': 'sheerid_it.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Primo Semestre 2024', 'Secondo Semestre 2025'],
        'flag': '🇮🇹'
    },
    'BR': {
        'name': 'Brazil',
        'code': 'br',
        'locale': 'pt-br',
        'collegeFile': 'sheerid_br.json',
        'currency': 'BRL',
        'currency_symbol': 'R$',
        'academic_terms': ['Semestre 1 2024', 'Semestre 2 2025'],
        'flag': '🇧🇷'
    },
    'MX': {
        'name': 'Mexico',
        'code': 'mx',
        'locale': 'es-mx',
        'collegeFile': 'sheerid_mx.json',
        'currency': 'MXN',
        'currency_symbol': '$',
        'academic_terms': ['Semestre 1 2024', 'Semestre 2 2025'],
        'flag': '🇲🇽'
    },
    'NL': {
        'name': 'Netherlands',
        'code': 'nl',
        'locale': 'nl-nl',
        'collegeFile': 'sheerid_nl.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Semester 1 2024', 'Semester 2 2025'],
        'flag': '🇳🇱'
    },
    'SE': {
        'name': 'Sweden',
        'code': 'se',
        'locale': 'sv-se',
        'collegeFile': 'sheerid_se.json',
        'currency': 'SEK',
        'currency_symbol': 'kr',
        'academic_terms': ['Hösttermin 2024', 'Vårtermin 2025'],
        'flag': '🇸🇪'
    },
    'NO': {
        'name': 'Norway',
        'code': 'no',
        'locale': 'no-no',
        'collegeFile': 'sheerid_no.json',
        'currency': 'NOK',
        'currency_symbol': 'kr',
        'academic_terms': ['Høstsemester 2024', 'Vårsemester 2025'],
        'flag': '🇳🇴'
    },
    'DK': {
        'name': 'Denmark',
        'code': 'dk',
        'locale': 'da-dk',
        'collegeFile': 'sheerid_dk.json',
        'currency': 'DKK',
        'currency_symbol': 'kr',
        'academic_terms': ['Efterårssemester 2024', 'Forårssemester 2025'],
        'flag': '🇩🇰'
    },
    'JP': {
        'name': 'Japan',
        'code': 'jp',
        'locale': 'ja-jp',
        'collegeFile': 'sheerid_jp.json',
        'currency': 'JPY',
        'currency_symbol': '¥',
        'academic_terms': ['Spring 2024', 'Fall 2024'],
        'flag': '🇯🇵'
    },
    'KR': {
        'name': 'South Korea',
        'code': 'kr',
        'locale': 'ko-kr',
        'collegeFile': 'sheerid_kr.json',
        'currency': 'KRW',
        'currency_symbol': '₩',
        'academic_terms': ['Spring 2024', 'Fall 2024'],
        'flag': '🇰🇷'
    },
    'SG': {
        'name': 'Singapore',
        'code': 'sg',
        'locale': 'en-sg',
        'collegeFile': 'sheerid_sg.json',
        'currency': 'SGD',
        'currency_symbol': '$',
        'academic_terms': ['Semester 1 2024', 'Semester 2 2025'],
        'flag': '🇸🇬'
    },
    'NZ': {
        'name': 'New Zealand',
        'code': 'nz',
        'locale': 'en-nz',
        'collegeFile': 'sheerid_nz.json',
        'currency': 'NZD',
        'currency_symbol': '$',
        'academic_terms': ['Semester 1 2024', 'Semester 2 2025'],
        'flag': '🇳🇿'
    },
    'ZA': {
        'name': 'South Africa',
        'code': 'za',
        'locale': 'en-za',
        'collegeFile': 'sheerid_za.json',
        'currency': 'ZAR',
        'currency_symbol': 'R',
        'academic_terms': ['First Semester 2024', 'Second Semester 2025'],
        'flag': '🇿🇦'
    },
    'CN': {
        'name': 'China',
        'code': 'cn',
        'locale': 'zh-cn',
        'collegeFile': 'sheerid_cn.json',
        'currency': 'CNY',
        'currency_symbol': '¥',
        'academic_terms': ['Spring 2024', 'Fall 2024'],
        'flag': '🇨🇳'
    },
    'AE': {
        'name': 'UAE',
        'code': 'ae',
        'locale': 'en-ae',
        'collegeFile': 'sheerid_ae.json',
        'currency': 'AED',
        'currency_symbol': 'د.إ',
        'academic_terms': ['Fall 2024', 'Spring 2025'],
        'flag': '🇦🇪'
    },
    'PH': {
        'name': 'Philippines',
        'code': 'ph',
        'locale': 'en-ph',
        'collegeFile': 'sheerid_ph.json',
        'currency': 'PHP',
        'currency_symbol': '₱',
        'academic_terms': ['First Semester 2024-2025', 'Second Semester 2024-2025', 'Summer 2024'],
        'flag': '🇵🇭'
    }
}

class UnlimitedIDCardGenerator:
    def __init__(self):
        self.receipts_dir = "receipts"
        self.students_file = "students.txt"
        self.selected_country = None
        self.all_colleges = []
        self.colleges_lock = threading.Lock()
        
        self.faker_instances = []
        self.faker_lock = threading.Lock()
        self.faker_index = 0
        self.file_save_lock = threading.Lock()
        
        # ⚡⚡⚡⚡⚡ ULTRA MEGA FAST SETTINGS - 2000+ IDs/MIN
        self.max_workers = 5000  # Increased from 3000
        self.memory_cleanup_interval = 5000  # Reduced cleanup frequency
        
        # ⚡ MEGA BATCH FILE WRITES
        self.student_buffer = []
        self.buffer_size = 1000  # Increased from 500
        
        # ⚡⚡⚡ PHOTO CACHE for instant access
        self.photo_cache = []
        self.photo_cache_lock = threading.Lock()
        self.photo_cache_size = 100
        
        # ⚡ 250 PHOTO SESSIONS (increased from 150)
        self.sessions = []
        for i in range(250):
            session = requests.Session()
            session.headers.update({
                'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            })
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=500,  # Increased
                pool_maxsize=500,      # Increased
                max_retries=1          # Reduced retries
            )
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            self.sessions.append(session)
        
        self.stats = {
            "ids_generated": 0,
            "photos_downloaded": 0,
            "photo_retries": 0,
            "students_saved": 0,
            "start_time": None
        }
        
        self.colors = {
            "navy": (0, 33, 71),
            "gold": (255, 184, 28),
            "blue": (20, 60, 110),
            "dark_blue": (15, 40, 70),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "gray": (50, 50, 50),
            "light_gray": (160, 160, 160),
            "bg_cream": (245, 245, 240),
            "label_dark": (40, 40, 40),
            "light_blue": (173, 216, 230),
        }
        
        # ⚡ CACHE CURRENT YEAR
        self.current_year = datetime.now(timezone.utc).year
        
        self.create_directories()
        self.clear_all_data()
        self.fonts = self.load_fonts()
        
        # ⚡ LOGO CACHE
        self.logo_cache = {}
        self.logo_cache_lock = threading.Lock()

    def create_directories(self):
        os.makedirs(self.receipts_dir, exist_ok=True)

    def clear_all_data(self):
        try:
            if os.path.exists(self.receipts_dir):
                for f in os.listdir(self.receipts_dir):
                    if f.endswith(('.png', '.jpg')):
                        try:
                            os.remove(os.path.join(self.receipts_dir, f))
                        except:
                            pass
            if os.path.exists(self.students_file):
                try:
                    os.remove(self.students_file)
                except:
                    pass
            
            print("🗑️  All data cleared!")
            print(f"✅ EXACT NAMES: Uses JSON names as-is (NO changes)")
            print(f"✅ SHEERID READY: Dates within 30 days")
            print(f"✅ LARGE LOGO: 300x300 prominent display")
            print(f"✅ FORMAT: STUDENTID_COLLEGEID.png")
            print(f"✅ SAVE: students.txt + receipts/")
            print(f"✅ 24 COUNTRIES: Full global support")
            print(f"⚡⚡⚡⚡⚡ ULTRA MEGA FAST: 5000 workers, 250 sessions")
            print(f"⚡⚡⚡⚡⚡ TARGET: 2000+ IDs per minute (10K in 5 min)")
            print(f"⚡⚡⚡⚡⚡ BATCH: 1000 writes at once")
            print(f"⚡⚡⚡⚡⚡ PHOTO CACHE: 100 pre-loaded photos")
            print("="*70)
        except Exception as e:
            print(f"⚠️  Warning: {e}")

    def load_colleges(self):
        try:
            if not self.selected_country:
                return []
            
            config = COUNTRY_CONFIG[self.selected_country]
            college_file = config['collegeFile']
            
            print(f"\n📚 Loading {college_file}...")
            
            if not os.path.exists(college_file):
                print(f"❌ ERROR: {college_file} not found!")
                return []
            
            with open(college_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            colleges = []
            for c in data:
                if (c.get('name') and c.get('id') and
                    c.get('type') in ['UNIVERSITY', 'COLLEGE', 'HEI', 'POST_SECONDARY']):
                    colleges.append({
                        'name': c['name'],
                        'id': c['id'],
                        'type': c['type']
                    })
            
            if not colleges:
                print(f"❌ No valid colleges!")
                return []
            
            print(f"✅ Loaded {len(colleges)} colleges")
            print(f"✅ Names stored EXACTLY as in JSON (no modifications)")
            print(f"✅ UNLIMITED mode: Colleges can be reused")
            
            return colleges
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return []

    def select_country_and_load(self):
        print("\n🌍 COUNTRY SELECTION - 24 COUNTRIES AVAILABLE")
        print("=" * 70)
        print("1 . United States        (US) | 2 . Canada               (CA)")
        print("3 . United Kingdom       (GB) | 4 . India                (IN)")
        print("5 . Indonesia            (ID) | 6 . Australia            (AU)")
        print("7 . Germany              (DE) | 8 . France               (FR)")
        print("9 . Spain                (ES) | 10. Italy                (IT)")
        print("11. Brazil               (BR) | 12. Mexico               (MX)")
        print("13. Netherlands          (NL) | 14. Sweden               (SE)")
        print("15. Norway               (NO) | 16. Denmark              (DK)")
        print("17. Japan                (JP) | 18. South Korea          (KR)")
        print("19. Singapore            (SG) | 20. New Zealand          (NZ)")
        print("21. South Africa         (ZA) | 22. China                (CN)")
        print("23. UAE                  (AE) | 24. Philippines          (PH)")
        print("=" * 70)
        
        country_map = {
            '1': 'US', '2': 'CA', '3': 'GB', '4': 'IN',
            '5': 'ID', '6': 'AU', '7': 'DE', '8': 'FR',
            '9': 'ES', '10': 'IT', '11': 'BR', '12': 'MX',
            '13': 'NL', '14': 'SE', '15': 'NO', '16': 'DK',
            '17': 'JP', '18': 'KR', '19': 'SG', '20': 'NZ',
            '21': 'ZA', '22': 'CN', '23': 'AE', '24': 'PH'
        }
        
        while True:
            choice = input("\nSelect country (1-24): ").strip()
            if choice in country_map:
                self.selected_country = country_map[choice]
                break
            else:
                print("❌ Enter a number between 1 and 24")
        
        config = COUNTRY_CONFIG[self.selected_country]
        print(f"\n✅ Selected: {config['flag']} {config['name']} ({self.selected_country})")
        
        self.all_colleges = self.load_colleges()
        
        if not self.all_colleges:
            print("❌ No colleges!")
            return False
        
        locale_map = {
            'US': 'en_US', 'CA': 'en_CA', 'GB': 'en_GB', 'IN': 'en_IN',
            'ID': 'id_ID', 'AU': 'en_AU', 'DE': 'de_DE', 'FR': 'fr_FR',
            'ES': 'es_ES', 'IT': 'it_IT', 'BR': 'pt_BR', 'MX': 'es_MX',
            'NL': 'nl_NL', 'SE': 'sv_SE', 'NO': 'no_NO', 'DK': 'da_DK',
            'JP': 'ja_JP', 'KR': 'ko_KR', 'SG': 'en_SG', 'NZ': 'en_NZ',
            'ZA': 'en_ZA', 'CN': 'zh_CN', 'AE': 'en_US', 'PH': 'fil_PH'
        }
        
        locale = locale_map.get(self.selected_country, 'en_US')
        
        try:
            self.faker_instances = [Faker(locale) for _ in range(200)]  # Increased from 100
        except:
            print(f"⚠️  Locale {locale} not available, using en_US")
            self.faker_instances = [Faker('en_US') for _ in range(200)]
        
        # ⚡⚡⚡ Pre-fill photo cache
        print(f"\n⚡⚡⚡ Pre-loading {self.photo_cache_size} photos...")
        self.refill_photo_cache_sync(self.photo_cache_size)
        print(f"✅ Photo cache ready!")
        
        return True

    @lru_cache(maxsize=1)
    def load_fonts(self):
        try:
            if os.name == 'nt':
                return {
                    'huge': ImageFont.truetype("arialbd.ttf", 72),
                    'college': ImageFont.truetype("arialbd.ttf", 48),
                    'subtitle': ImageFont.truetype("arial.ttf", 22),
                    'name': ImageFont.truetype("arialbd.ttf", 36),
                    'value': ImageFont.truetype("arialbd.ttf", 28),
                    'label': ImageFont.truetype("arialbd.ttf", 22),
                    'small': ImageFont.truetype("arial.ttf", 16),
                    'watermark': ImageFont.truetype("arialbd.ttf", 70),
                    'logo_text': ImageFont.truetype("arialbd.ttf", 42),
                }
            else:
                return {k: ImageFont.load_default() for k in ['huge', 'college', 'subtitle', 'name', 'value', 'label', 'small', 'watermark', 'logo_text']}
        except:
            return {k: ImageFont.load_default() for k in ['huge', 'college', 'subtitle', 'name', 'value', 'label', 'small', 'watermark', 'logo_text']}

    def get_faker(self):
        with self.faker_lock:
            faker = self.faker_instances[self.faker_index]
            self.faker_index = (self.faker_index + 1) % len(self.faker_instances)
            return faker

    def create_large_logo(self, college_name):
        """⚡ CACHED LOGO GENERATION"""
        with self.logo_cache_lock:
            if college_name in self.logo_cache:
                return self.logo_cache[college_name].copy()
        
        size = (300, 300)
        logo = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(logo)
        
        center = 150
        
        draw.ellipse([20, 20, 280, 280], fill=self.colors["navy"], outline=self.colors["gold"], width=8)
        draw.ellipse([40, 40, 260, 260], fill=self.colors["white"], outline=self.colors["gold"], width=6)
        draw.ellipse([60, 60, 240, 240], fill=self.colors["navy"])
        
        book_width = 80
        book_height = 60
        book_x = center - book_width // 2
        book_y = center - book_height // 2 - 20
        
        draw.rectangle([book_x, book_y, book_x + book_width, book_y + book_height], 
                      fill=self.colors["white"], outline=self.colors["gold"], width=3)
        draw.line([book_x + book_width//2, book_y, book_x + book_width//2, book_y + book_height], 
                 fill=self.colors["gold"], width=4)
        
        torch_x = center
        torch_y = center + 50
        
        flame_points = [
            (torch_x, torch_y - 25),
            (torch_x - 15, torch_y - 10),
            (torch_x - 10, torch_y),
            (torch_x + 10, torch_y),
            (torch_x + 15, torch_y - 10)
        ]
        draw.polygon(flame_points, fill=self.colors["gold"])
        draw.rectangle([torch_x - 8, torch_y, torch_x + 8, torch_y + 35], fill=self.colors["gold"])
        
        star_positions = [
            (center - 70, center - 70),
            (center + 70, center - 70),
            (center - 70, center + 70),
            (center + 70, center + 70)
        ]
        
        for sx, sy in star_positions:
            draw.polygon([
                (sx, sy - 8), (sx - 3, sy - 3), (sx - 8, sy),
                (sx - 3, sy + 3), (sx, sy + 8), (sx + 3, sy + 3),
                (sx + 8, sy), (sx + 3, sy - 3)
            ], fill=self.colors["gold"])
        
        try:
            words = college_name.split()[:3]
            initials = ''.join([w[0] for w in words if w])[:3].upper()
            
            bbox = draw.textbbox((0, 0), initials, font=self.fonts['logo_text'])
            text_w = bbox[2] - bbox[0]
            
            draw.text((center - text_w//2, center + 80), initials, 
                     fill=self.colors["gold"], font=self.fonts['logo_text'])
        except:
            pass
        
        with self.logo_cache_lock:
            if len(self.logo_cache) < 2000:  # Increased cache limit
                self.logo_cache[college_name] = logo.copy()
        
        return logo

    def get_real_photo_guaranteed(self):
        """⚡⚡⚡⚡⚡ ULTRA FAST PHOTO DOWNLOADS - MINIMAL DELAYS"""
        attempt = 0
        session_index = random.randint(0, len(self.sessions) - 1)
        
        while True:
            attempt += 1
            
            try:
                session = self.sessions[session_index % len(self.sessions)]
                
                timestamp = int(time.time() * 1000)
                random_param = random.randint(100000, 999999)
                
                urls_to_try = [
                    f"https://thispersondoesnotexist.com/?{timestamp}",
                    f"https://thispersondoesnotexist.com/image?{random_param}",
                ]
                
                for url in urls_to_try:
                    try:
                        response = session.get(url, timeout=2, stream=True)  # Reduced to 2s
                        
                        if response.status_code == 200:
                            content = response.content
                            
                            if len(content) > 5000:
                                photo = Image.open(BytesIO(content)).convert("RGB")
                                
                                if photo.size[0] >= 100 and photo.size[1] >= 100:
                                    photo = photo.resize((350, 450), Image.Resampling.LANCZOS)
                                    self.stats["photos_downloaded"] += 1
                                    
                                    if attempt > 1:
                                        self.stats["photo_retries"] += (attempt - 1)
                                    
                                    return photo
                    except:
                        continue
                
                # ⚡⚡⚡⚡⚡ ULTRA MINIMAL DELAYS
                if attempt < 3:
                    time.sleep(0.001)  # 1ms
                elif attempt < 10:
                    time.sleep(0.005)  # 5ms
                else:
                    time.sleep(0.01)   # 10ms max
                
                session_index += 1
                
            except:
                time.sleep(0.001)
                continue

    def refill_photo_cache_sync(self, count):
        """⚡⚡⚡ Pre-fill photo cache synchronously"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(self.get_real_photo_guaranteed) for _ in range(count)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    photo = future.result()
                    with self.photo_cache_lock:
                        self.photo_cache.append(photo)
                except:
                    pass

    def refill_photo_cache_background(self):
        """⚡⚡⚡ Background thread to keep photo cache full"""
        while len(self.photo_cache) < self.photo_cache_size:
            try:
                photo = self.get_real_photo_guaranteed()
                with self.photo_cache_lock:
                    if len(self.photo_cache) < self.photo_cache_size:
                        self.photo_cache.append(photo)
            except:
                break

    def get_photo_from_cache(self):
        """⚡⚡⚡ Get photo from cache or download if needed"""
        with self.photo_cache_lock:
            if len(self.photo_cache) > 0:
                photo = self.photo_cache.pop(0)
                
                # Start background refill if cache is low
                if len(self.photo_cache) < 20:
                    threading.Thread(target=self.refill_photo_cache_background, daemon=True).start()
                
                return photo
        
        # Cache empty, download directly
        return self.get_real_photo_guaranteed()

    def select_random_college(self):
        with self.colleges_lock:
            if not self.all_colleges:
                return None
            return random.choice(self.all_colleges)

    def wrap_text_smart(self, text, font, max_width, draw):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def generate_student_data(self, college):
        fake = self.get_faker()
        config = COUNTRY_CONFIG[self.selected_country]
        
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}".upper()
        student_id = f"{fake.random_number(digits=8, fix_len=True)}"
        
        programs_by_country = {
            'US': ["Computer Science", "Business Administration", "Engineering", "Nursing", "Psychology", "Biology", "Mathematics"],
            'CA': ["Computer Science", "Business", "Engineering", "Medicine", "Arts", "Law"],
            'GB': ["Computer Science", "Business Studies", "Engineering", "Medicine", "Law", "Economics"],
            'IN': ["B.Tech", "B.E.", "MBBS", "B.Com", "BBA", "B.Sc", "BCA"],
            'ID': ["Teknik Informatika", "Ekonomi", "Kedokteran", "Hukum", "Teknik"],
            'AU': ["Computer Science", "Business", "Engineering", "Medicine", "Law"],
            'DE': ["Informatik", "BWL", "Ingenieurwesen", "Medizin", "Jura"],
            'FR': ["Informatique", "Commerce", "Ingénierie", "Médecine", "Droit"],
            'ES': ["Informática", "Administración", "Ingeniería", "Medicina", "Derecho"],
            'IT': ["Informatica", "Economia", "Ingegneria", "Medicina", "Giurisprudenza"],
            'BR': ["Ciência da Computação", "Administração", "Engenharia", "Medicina"],
            'MX': ["Informática", "Administración", "Ingeniería", "Medicina", "Derecho"],
            'NL': ["Computer Science", "Business", "Engineering", "Medicine", "Law"],
            'SE': ["Datavetenskap", "Ekonomi", "Teknik", "Medicin", "Juridik"],
            'NO': ["Informatikk", "Økonomi", "Ingeniørvitenskap", "Medisin", "Jus"],
            'DK': ["Datalogi", "Økonomi", "Ingeniørvidenskab", "Medicin", "Jura"],
            'JP': ["Computer Science", "Business", "Engineering", "Medicine", "Law"],
            'KR': ["Computer Science", "Business", "Engineering", "Medicine", "Law"],
            'SG': ["Computer Science", "Business", "Engineering", "Medicine", "Law"],
            'NZ': ["Computer Science", "Business", "Engineering", "Medicine", "Law"],
            'ZA': ["Computer Science", "Business", "Engineering", "Medicine", "Law"],
            'CN': ["Computer Science", "Business", "Engineering", "Medicine", "Law"],
            'AE': ["Computer Science", "Business", "Engineering", "Medicine", "Law"],
            'PH': ["BS Computer Science", "BS Business Administration", "BS Engineering", "BS Nursing", "BS Psychology"]
        }
        
        programs = programs_by_country.get(self.selected_country, ["Computer Science", "Business", "Engineering"])
        
        today = datetime.now(timezone.utc)
        days_ago = random.randint(0, 30)
        doc_date = today - timedelta(days=days_ago)
        exp_date = doc_date + timedelta(days=random.choice([365, 730, 1095]))
        
        return {
            "full_name": full_name,
            "student_id": student_id,
            "program": random.choice(programs),
            "college": college,
            "doc_date": doc_date,
            "exp_date": exp_date,
            "term": random.choice(config['academic_terms'])
        }

    def create_professional_id_card(self, student_data):
        college = student_data['college']
        college_name = college['name']
        college_id = college['id']
        student_id = student_data['student_id']
        
        filename = f"{student_id}_{college_id}.png"
        filepath = os.path.join(self.receipts_dir, filename)
        
        width, height = 1800, 1100
        
        card = Image.new("RGB", (width, height), self.colors["bg_cream"])
        draw = ImageDraw.Draw(card)
        fonts = self.load_fonts()
        config = COUNTRY_CONFIG[self.selected_country]
        
        border_thickness = 15
        for i in range(border_thickness):
            draw.rectangle([i, i, width-i-1, height-i-1], outline=self.colors["navy"], width=1)
        
        header_height = 280
        draw.rectangle([border_thickness, border_thickness, 
                       width-border_thickness, header_height], 
                      fill=self.colors["navy"])
        
        draw.rectangle([border_thickness, header_height - 20, 
                       width-border_thickness, header_height], 
                      fill=self.colors["gold"])
        
        logo = self.create_large_logo(college_name)
        logo_pos = (40, 40)
        
        card_rgba = card.convert('RGBA')
        card_rgba.paste(logo, logo_pos, logo)
        card = card_rgba.convert('RGB')
        draw = ImageDraw.Draw(card)
        
        temp_img = Image.new("RGB", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        max_width = width - 450
        
        name_x = 380
        name_y = 80
        
        bbox = temp_draw.textbbox((0, 0), college_name, font=fonts['college'])
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            draw.text((name_x, name_y), college_name, fill=self.colors["white"], 
                     font=fonts['college'])
        else:
            lines = self.wrap_text_smart(college_name, fonts['college'], max_width, temp_draw)
            y_start = name_y if len(lines) == 2 else name_y - 20
            for i, line in enumerate(lines[:3]):
                draw.text((name_x, y_start + (i * 55)), line, fill=self.colors["white"], 
                         font=fonts['college'])
        
        draw.text((name_x, name_y + 130), "STUDENT IDENTIFICATION CARD", 
                 fill=self.colors["gold"], font=fonts['subtitle'])
        
        draw.text((width - 200, 60), f"{self.current_year}-{self.current_year+1}", 
                 fill=self.colors["gold"], font=fonts['name'], anchor="mm")
        
        watermark_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        watermark_draw = ImageDraw.Draw(watermark_img)
        watermark_draw.text((width//2, height//2), "VALID", 
                          fill=(200, 200, 200, 30), font=fonts['watermark'], anchor="mm")
        card = Image.alpha_composite(card.convert('RGBA'), watermark_img).convert('RGB')
        draw = ImageDraw.Draw(card)
        
        content_y = header_height + 60
        
        # ⚡⚡⚡⚡⚡ USE PHOTO CACHE
        photo = self.get_photo_from_cache()
        photo_pos = (80, content_y)
        
        draw.rectangle([photo_pos[0]-5, photo_pos[1]-5, 
                       photo_pos[0]+355, photo_pos[1]+455], 
                      fill=self.colors["navy"])
        
        card.paste(photo, photo_pos)
        
        info_x = 520
        info_y = content_y + 40
        gap = 110
        
        details = [
            ("STUDENT NAME", student_data['full_name']),
            ("ID NUMBER", student_id),
            ("PROGRAM", student_data['program']),
            ("TERM", student_data['term']),
            ("ISSUE DATE", student_data['doc_date'].strftime('%d %B %Y')),
            ("VALID UNTIL", student_data['exp_date'].strftime('%d %B %Y'))
        ]
        
        for i, (label, value) in enumerate(details):
            y = info_y + (i * gap)
            draw.text((info_x, y), label, fill=self.colors["navy"], font=fonts['label'])
            draw.text((info_x, y + 30), value, fill=self.colors["black"], font=fonts['name'])
            draw.line([info_x, y + 80, info_x + 800, y + 80], 
                     fill=self.colors["gray"], width=2)
        
        # ⚡ QR Code (optional - can be disabled for even more speed)
        try:
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(f"{college_name}|{student_id}|{student_data['full_name']}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB").resize((200, 200))
            
            qr_x = width - 280
            qr_y = content_y + 300
            
            draw.rectangle([qr_x-5, qr_y-5, qr_x+205, qr_y+205], 
                          fill=self.colors["navy"])
            
            card.paste(qr_img, (qr_x, qr_y))
            
            draw.text((qr_x + 100, qr_y + 220), "SCAN TO VERIFY", 
                     fill=self.colors["gray"], font=fonts['small'], anchor="mm")
        except:
            pass
        
        footer_y = height - 120
        draw.rectangle([border_thickness, footer_y, width-border_thickness, height-border_thickness], 
                      fill=self.colors["light_blue"])
        
        draw.text((width//2, footer_y + 30), 
                 f"ID: {college_id} • {config['name']} • Issued: {student_data['doc_date'].strftime('%B %Y')}", 
                 fill=self.colors["navy"], font=fonts['value'], anchor="mm")
        
        draw.text((width//2, footer_y + 70), 
                 "This card is property of the institution • Report if lost", 
                 fill=self.colors["gray"], font=fonts['small'], anchor="mm")
        
        # ⚡⚡⚡ ULTRA FAST SAVE - Quality 85, compress_level 1
        card.save(filepath, "PNG", quality=85, optimize=False, compress_level=1)
        self.stats["ids_generated"] += 1
        
        return student_data

    def save_student(self, student_data):
        """⚡⚡⚡⚡⚡ MEGA BATCH SAVE - 1000 at once"""
        with self.file_save_lock:
            try:
                self.student_buffer.append(student_data)
                
                if len(self.student_buffer) >= self.buffer_size:
                    self._flush_buffer()
                
                return True
            except:
                return False

    def _flush_buffer(self):
        if not self.student_buffer:
            return
        
        try:
            with open(self.students_file, 'a', encoding='utf-8', buffering=32768) as f:  # Larger buffer
                for student_data in self.student_buffer:
                    line = f"{student_data['full_name']}|{student_data['student_id']}|{student_data['college']['id']}|{student_data['college']['name']}|{self.selected_country}|{student_data['doc_date'].strftime('%Y-%m-%d')}|{student_data['exp_date'].strftime('%Y-%m-%d')}\n"
                    f.write(line)
                f.flush()
            
            self.stats["students_saved"] += len(self.student_buffer)
            self.student_buffer.clear()
        except Exception as e:
            print(f"⚠️ Flush error: {e}")

    def process_one(self, num):
        try:
            college = self.select_random_college()
            if college is None:
                return False
            
            student_data = self.generate_student_data(college)
            self.create_professional_id_card(student_data)
            self.save_student(student_data)
            return True
        except Exception as e:
            return False

    def generate_bulk(self, quantity):
        config = COUNTRY_CONFIG[self.selected_country]
        print(f"\n⚡⚡⚡⚡⚡ Generating {quantity} IDs for {config['flag']} {config['name']}")
        print(f"✅ {len(self.all_colleges)} colleges available")
        print(f"✅ Using EXACT names from JSON (zero modifications)")
        print(f"✅ Dates within 30 days (SheerID verified)")
        print(f"✅ Large logos (300x300)")
        print(f"⚡⚡⚡⚡⚡ ULTRA MEGA FAST: 5000 workers, 250 sessions, 1000 batch")
        print(f"⚡⚡⚡⚡⚡ TARGET: 2000+ IDs per minute (10K in 5 min)")
        print("="*70)
        
        start = time.time()
        success = 0
        
        # Process in chunks for better photo cache management
        chunk_size = 1000
        
        for chunk_start in range(0, quantity, chunk_size):
            chunk_end = min(chunk_start + chunk_size, quantity)
            chunk_qty = chunk_end - chunk_start
            
            # Ensure photo cache is full before each chunk
            with self.photo_cache_lock:
                cache_size = len(self.photo_cache)
            
            if cache_size < 50:
                print(f"⚡⚡⚡ Refilling photo cache...")
                self.refill_photo_cache_sync(50)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self.process_one, i+1) for i in range(chunk_start, chunk_end)]
                
                for i, future in enumerate(concurrent.futures.as_completed(futures), chunk_start + 1):
                    if future.result():
                        success += 1
                    
                    if i % 200 == 0 or i == quantity:
                        elapsed = time.time() - start
                        rate = i / elapsed if elapsed > 0 else 0
                        rate_per_min = rate * 60
                        print(f"Progress: {i}/{quantity} ({(i/quantity*100):.1f}%) | Rate: {rate_per_min:.0f} IDs/min | Cache: {len(self.photo_cache)}")
        
        self._flush_buffer()
        
        duration = time.time() - start
        rate_per_min = (success / duration) * 60 if duration > 0 else 0
        
        print("\n" + "="*70)
        print(f"✅ COMPLETE - {config['flag']} {config['name']}")
        print("="*70)
        print(f"⏱️  Time: {duration:.1f}s ({duration/60:.2f} minutes)")
        print(f"⚡⚡⚡⚡⚡ Speed: {rate_per_min:.0f} IDs/minute")
        print(f"⚡⚡⚡⚡⚡ Rate: {success/duration:.1f} IDs/second")
        print(f"✅ Success: {success}/{quantity}")
        print(f"📸 Photos: {self.stats['photos_downloaded']}")
        print(f"📁 Folder: {self.receipts_dir}/")
        print(f"📄 Students: {self.students_file}")
        print(f"✅ NAMES: Exact from JSON (no modifications)")
        print(f"✅ DATES: Within 30 days (SheerID)")
        print(f"✅ LOGOS: 300x300 (prominent)")
        print("="*70)

    def interactive(self):
        total = 0
        config = COUNTRY_CONFIG[self.selected_country]
        
        while True:
            print(f"\n{'='*60}")
            print(f"Country: {config['flag']} {config['name']}")
            print(f"Total Generated: {total}")
            print(f"Available Colleges: {len(self.all_colleges)}")
            print(f"Mode: ULTRA MEGA FAST ⚡⚡⚡⚡⚡ (2000+ IDs/min)")
            print(f"Photo Cache: {len(self.photo_cache)} ready")
            print(f"{'='*60}")
            
            user_input = input(f"\nQuantity (0 to exit): ").strip()
            
            if user_input == "0":
                self._flush_buffer()
                break
            
            try:
                quantity = int(user_input)
            except:
                print("❌ Enter a valid number")
                continue
            
            if quantity < 1:
                print("❌ Enter a number greater than 0")
                continue
            
            self.generate_bulk(quantity)
            total = self.stats["ids_generated"]

def main():
    print("\n" + "="*70)
    print("⚡⚡⚡⚡⚡ SHEERID ID - ULTRA MEGA FAST - 2000+ IDs/MIN")
    print("="*70)
    print("📅 2025-11-11 19:29:07 UTC")
    print("👤 Adeebaabkhan")
    print("✅ EXACT NAMES: Uses JSON college names as-is (ZERO changes)")
    print("✅ DATES: Within 30 days (SheerID requirement)")
    print("✅ LARGE LOGO: 300x300 prominent display")
    print("✅ FORMAT: STUDENTID_COLLEGEID.png")
    print("✅ SAVE: students.txt + receipts/")
    print("✅ 24 COUNTRIES: US, CA, GB, IN, ID, AU, DE, FR, ES, IT,")
    print("                 BR, MX, NL, SE, NO, DK, JP, KR, SG, NZ,")
    print("                 ZA, CN, AE, PH")
    print("✅ UNLIMITED: Can reuse colleges")
    print("⚡⚡⚡⚡⚡ ULTRA MEGA FAST: 5000 workers, 250 sessions, 1000 batch")
    print("⚡⚡⚡⚡⚡ TARGET: 2000+ IDs per minute (10K in 5 min)")
    print("⚡⚡⚡⚡⚡ PHOTO CACHE: 100 pre-loaded photos")
    print("⚡⚡⚡⚡⚡ OPTIMIZED I/O: Minimal delays, large buffers")
    print("="*70)
    
    gen = UnlimitedIDCardGenerator()
    
    if not gen.select_country_and_load():
        return
    
    gen.interactive()
    
    print("\n✅ FINISHED!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")