#!/usr/bin/env python3
"""
PROFESSIONAL EMPLOYMENT DOCUMENT GENERATOR - PERFECT FOR VERIFICATION
✅ EMPLOYMENT VERIFICATION LETTER: Professional verification letter
✅ EMPLOYMENT CONTRACT: Official school employment contract  
✅ EMPLOYEE PAY STUB: Detailed salary payment stub
✅ INSTANT VERIFICATION: Super-fast verification system
✅ INSTITUTION NAME: Full school name from JSON only  
✅ EMPLOYEE INFO: Name, ID, Position, Department, Salary Proof
✅ HARDCODED DATES: Current employment dates
✅ PDF OUTPUT: Professional formatting
✅ ALL 24 COUNTRIES: Complete global support
✅ VERIFICATION READY: Perfect for employment verification
"""

import sys
import os
import re
import logging
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
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Logging & Helpers ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def clean_name(name: str) -> str:
    """Cleans up names from titles and unwanted characters."""
    name = re.sub(r"[.,]", "", name)
    name = re.sub(r"\b(Drs?|Ir|H|Prof|S|M|Bapak|Ibu)\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+", " ", name).strip()
    return name

# ==================== COMPLETE 24 COUNTRY CONFIGURATION ====================
COUNTRY_CONFIG = {
    'US': {
        'name': 'United States',
        'code': 'us',
        'locale': 'en_US',
        'schoolFile': 'schools_us.json',
        'currency': 'USD',
        'currency_symbol': '$',
        'salary_range': (40000, 80000),
        'bonus_range': (2000, 10000),
        'flag': '🇺🇸',
        'time_format': 'AM/PM',
        'date_format': '%B %d, %Y',
        'contract_types': ['Full-Time Permanent', 'Full-Time Contract', 'Part-Time'],
        'departments': ['Mathematics', 'Science', 'English', 'History', 'Physical Education', 'Arts', 'Special Education']
    },
    'CA': {
        'name': 'Canada',
        'code': 'ca',
        'locale': 'en_CA',
        'schoolFile': 'schools_ca.json',
        'currency': 'CAD',
        'currency_symbol': '$',
        'salary_range': (45000, 85000),
        'bonus_range': (2500, 12000),
        'flag': '🇨🇦',
        'time_format': 'AM/PM',
        'date_format': '%B %d, %Y',
        'contract_types': ['Full-Time Permanent', 'Full-Time Contract', 'Part-Time'],
        'departments': ['Mathematics', 'Science', 'English', 'History', 'Physical Education', 'Arts', 'French']
    },
    'GB': {
        'name': 'United Kingdom',
        'code': 'gb',
        'locale': 'en_GB',
        'schoolFile': 'schools_gb.json',
        'currency': 'GBP',
        'currency_symbol': '£',
        'salary_range': (30000, 60000),
        'bonus_range': (1500, 8000),
        'flag': '🇬🇧',
        'time_format': '24-hour',
        'date_format': '%d %B %Y',
        'contract_types': ['Full-Time Permanent', 'Full-Time Contract', 'Part-Time'],
        'departments': ['Mathematics', 'Science', 'English', 'History', 'Physical Education', 'Arts']
    },
    'IN': {
        'name': 'India',
        'code': 'in',
        'locale': 'en_IN',
        'schoolFile': 'schools_in.json',
        'currency': 'INR',
        'currency_symbol': '₹',
        'salary_range': (300000, 800000),
        'bonus_range': (20000, 100000),
        'flag': '🇮🇳',
        'time_format': 'AM/PM',
        'date_format': '%d %B %Y',
        'contract_types': ['Regular', 'Contract', 'Visiting'],
        'departments': ['Mathematics', 'Science', 'English', 'Social Studies', 'Physical Education', 'Arts']
    },
    'ID': {
        'name': 'Indonesia',
        'code': 'id',
        'locale': 'id_ID',
        'schoolFile': 'schools_id.json',
        'currency': 'IDR',
        'currency_symbol': 'Rp',
        'salary_range': (60000000, 180000000),
        'bonus_range': (5000000, 30000000),
        'flag': '🇮🇩',
        'time_format': '24-hour',
        'date_format': '%d %B %Y',
        'contract_types': ['Pegawai Negeri', 'Guru Honorer', 'Guru Kontrak'],
        'departments': ['Matematika', 'IPA', 'Bahasa Indonesia', 'IPS', 'Pendidikan Jasmani', 'Seni']
    },
    'AU': {
        'name': 'Australia',
        'code': 'au',
        'locale': 'en_AU',
        'schoolFile': 'schools_au.json',
        'currency': 'AUD',
        'currency_symbol': '$',
        'salary_range': (60000, 100000),
        'bonus_range': (3000, 15000),
        'flag': '🇦🇺',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Full-Time Ongoing', 'Full-Time Fixed Term', 'Part-Time'],
        'departments': ['Mathematics', 'Science', 'English', 'Humanities', 'Physical Education', 'Arts']
    },
    'DE': {
        'name': 'Germany',
        'code': 'de',
        'locale': 'de_DE',
        'schoolFile': 'schools_de.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'salary_range': (45000, 75000),
        'bonus_range': (2000, 10000),
        'flag': '🇩🇪',
        'time_format': '24-hour',
        'date_format': '%d.%m.%Y',
        'contract_types': ['Beamter', 'Angestellter', 'Teilzeit'],
        'departments': ['Mathematik', 'Naturwissenschaften', 'Deutsch', 'Geschichte', 'Sport', 'Kunst']
    },
    'FR': {
        'name': 'France',
        'code': 'fr',
        'locale': 'fr_FR',
        'schoolFile': 'schools_fr.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'salary_range': (35000, 65000),
        'bonus_range': (1500, 8000),
        'flag': '🇫🇷',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Titulaire', 'Contractuel', 'Temps Partiel'],
        'departments': ['Mathématiques', 'Sciences', 'Français', 'Histoire', 'Éducation Physique', 'Arts']
    },
    'ES': {
        'name': 'Spain',
        'code': 'es',
        'locale': 'es_ES',
        'schoolFile': 'schools_es.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'salary_range': (30000, 55000),
        'bonus_range': (1000, 7000),
        'flag': '🇪🇸',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Funcionario', 'Interino', 'Tiempo Parcial'],
        'departments': ['Matemáticas', 'Ciencias', 'Lengua', 'Historia', 'Educación Física', 'Arte']
    },
    'IT': {
        'name': 'Italy',
        'code': 'it',
        'locale': 'it_IT',
        'schoolFile': 'schools_it.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'salary_range': (32000, 58000),
        'bonus_range': (1200, 7500),
        'flag': '🇮🇹',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Di Ruolo', 'Precario', 'Part-Time'],
        'departments': ['Matematica', 'Scienze', 'Italiano', 'Storia', 'Educazione Fisica', 'Arte']
    },
    'BR': {
        'name': 'Brazil',
        'code': 'br',
        'locale': 'pt_BR',
        'schoolFile': 'schools_br.json',
        'currency': 'BRL',
        'currency_symbol': 'R$',
        'salary_range': (40000, 80000),
        'bonus_range': (3000, 15000),
        'flag': '🇧🇷',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Efetivo', 'Contratado', 'Tempo Parcial'],
        'departments': ['Matemática', 'Ciências', 'Português', 'História', 'Educação Física', 'Artes']
    },
    'MX': {
        'name': 'Mexico',
        'code': 'mx',
        'locale': 'es_MX',
        'schoolFile': 'schools_mx.json',
        'currency': 'MXN',
        'currency_symbol': '$',
        'salary_range': (200000, 500000),
        'bonus_range': (15000, 80000),
        'flag': '🇲🇽',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Base', 'Contrato', 'Medio Tiempo'],
        'departments': ['Matemáticas', 'Ciencias', 'Español', 'Historia', 'Educación Física', 'Artes']
    },
    'NL': {
        'name': 'Netherlands',
        'code': 'nl',
        'locale': 'nl_NL',
        'schoolFile': 'schools_nl.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'salary_range': (40000, 70000),
        'bonus_range': (2000, 12000),
        'flag': '🇳🇱',
        'time_format': '24-hour',
        'date_format': '%d-%m-%Y',
        'contract_types': ['Vast', 'Tijdelijk', 'Parttime'],
        'departments': ['Wiskunde', 'Natuurkunde', 'Nederlands', 'Geschiedenis', 'Lichamelijke Opvoeding', 'Kunst']
    },
    'SE': {
        'name': 'Sweden',
        'code': 'se',
        'locale': 'sv_SE',
        'schoolFile': 'schools_se.json',
        'currency': 'SEK',
        'currency_symbol': 'kr',
        'salary_range': (350000, 600000),
        'bonus_range': (20000, 100000),
        'flag': '🇸🇪',
        'time_format': '24-hour',
        'date_format': '%Y-%m-%d',
        'contract_types': ['Tillsvidare', 'Tidsbegränsad', 'Deltid'],
        'departments': ['Matematik', 'Naturvetenskap', 'Svenska', 'Historia', 'Idrott', 'Konst']
    },
    'NO': {
        'name': 'Norway',
        'code': 'no',
        'locale': 'no_NO',
        'schoolFile': 'schools_no.json',
        'currency': 'NOK',
        'currency_symbol': 'kr',
        'salary_range': (450000, 750000),
        'bonus_range': (25000, 120000),
        'flag': '🇳🇴',
        'time_format': '24-hour',
        'date_format': '%d.%m.%Y',
        'contract_types': ['Fast', 'Midlertidig', 'Deltid'],
        'departments': ['Matematikk', 'Naturfag', 'Norsk', 'Historie', 'Kroppsøving', 'Kunst']
    },
    'DK': {
        'name': 'Denmark',
        'code': 'dk',
        'locale': 'da_DK',
        'schoolFile': 'schools_dk.json',
        'currency': 'DKK',
        'currency_symbol': 'kr',
        'salary_range': (380000, 650000),
        'bonus_range': (22000, 110000),
        'flag': '🇩🇰',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Fast', 'Tidsbegrænset', 'Deltid'],
        'departments': ['Matematik', 'Naturvidenskab', 'Dansk', 'Historie', 'Idræt', 'Kunst']
    },
    'JP': {
        'name': 'Japan',
        'code': 'jp',
        'locale': 'ja_JP',
        'schoolFile': 'schools_jp.json',
        'currency': 'JPY',
        'currency_symbol': '¥',
        'salary_range': (4000000, 7000000),
        'bonus_range': (200000, 1000000),
        'flag': '🇯🇵',
        'time_format': '24-hour',
        'date_format': '%Y年%m月%d日',
        'contract_types': ['常勤', '契約', 'パートタイム'],
        'departments': ['数学', '理科', '国語', '社会', '体育', '美術']
    },
    'KR': {
        'name': 'South Korea',
        'code': 'kr',
        'locale': 'ko_KR',
        'schoolFile': 'schools_kr.json',
        'currency': 'KRW',
        'currency_symbol': '₩',
        'salary_range': (40000000, 70000000),
        'bonus_range': (2000000, 10000000),
        'flag': '🇰🇷',
        'time_format': '24-hour',
        'date_format': '%Y년 %m월 %d일',
        'contract_types': ['정규직', '계약직', '파트타임'],
        'departments': ['수학', '과학', '국어', '사회', '체육', '미술']
    },
    'SG': {
        'name': 'Singapore',
        'code': 'sg',
        'locale': 'en_SG',
        'schoolFile': 'schools_sg.json',
        'currency': 'SGD',
        'currency_symbol': '$',
        'salary_range': (50000, 90000),
        'bonus_range': (3000, 20000),
        'flag': '🇸🇬',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Permanent', 'Contract', 'Part-Time'],
        'departments': ['Mathematics', 'Science', 'English', 'Humanities', 'Physical Education', 'Arts']
    },
    'NZ': {
        'name': 'New Zealand',
        'code': 'nz',
        'locale': 'en_NZ',
        'schoolFile': 'schools_nz.json',
        'currency': 'NZD',
        'currency_symbol': '$',
        'salary_range': (55000, 95000),
        'bonus_range': (3500, 18000),
        'flag': '🇳🇿',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Permanent', 'Fixed Term', 'Part-Time'],
        'departments': ['Mathematics', 'Science', 'English', 'Social Sciences', 'Physical Education', 'Arts']
    },
    'ZA': {
        'name': 'South Africa',
        'code': 'za',
        'locale': 'en_ZA',
        'schoolFile': 'schools_za.json',
        'currency': 'ZAR',
        'currency_symbol': 'R',
        'salary_range': (250000, 500000),
        'bonus_range': (15000, 80000),
        'flag': '🇿🇦',
        'time_format': 'AM/PM',
        'date_format': '%Y/%m/%d',
        'contract_types': ['Permanent', 'Contract', 'Part-Time'],
        'departments': ['Mathematics', 'Science', 'English', 'Social Studies', 'Physical Education', 'Arts']
    },
    'CN': {
        'name': 'China',
        'code': 'cn',
        'locale': 'zh_CN',
        'schoolFile': 'schools_cn.json',
        'currency': 'CNY',
        'currency_symbol': '¥',
        'salary_range': (120000, 300000),
        'bonus_range': (10000, 50000),
        'flag': '🇨🇳',
        'time_format': '24-hour',
        'date_format': '%Y年%m月%d日',
        'contract_types': ['编制', '合同', '兼职'],
        'departments': ['数学', '科学', '语文', '历史', '体育', '美术']
    },
    'AE': {
        'name': 'UAE',
        'code': 'ae',
        'locale': 'en_AE',
        'schoolFile': 'schools_ae.json',
        'currency': 'AED',
        'currency_symbol': 'د.إ',
        'salary_range': (120000, 250000),
        'bonus_range': (10000, 50000),
        'flag': '🇦🇪',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'contract_types': ['Permanent', 'Contract', 'Part-Time'],
        'departments': ['Mathematics', 'Science', 'English', 'Social Studies', 'Physical Education', 'Arts']
    },
    'PH': {
        'name': 'Philippines',
        'code': 'ph',
        'locale': 'en_PH',
        'schoolFile': 'schools_ph.json',
        'currency': 'PHP',
        'currency_symbol': '₱',
        'salary_range': (300000, 600000),
        'bonus_range': (20000, 100000),
        'flag': '🇵🇭',
        'time_format': 'AM/PM',
        'date_format': '%B %d, %Y',
        'contract_types': ['Regular', 'Contractual', 'Part-Time'],
        'departments': ['Mathematics', 'Science', 'English', 'Social Studies', 'Physical Education', 'Arts']
    }
}

class ProfessionalEmploymentDocumentGenerator:
    def __init__(self):
        self.documents_dir = "employment_docs"
        self.employees_file = "employees.txt"
        self.selected_country = None
        self.all_schools = []
        
        self.faker_instances = []
        self.faker_lock = threading.Lock()
        self.faker_index = 0
        
        # Performance settings
        self.max_workers = 10
        self.memory_cleanup_interval = 100
        
        self.stats = {
            "documents_generated": 0,
            "employees_saved": 0,
            "start_time": None
        }
        
        # Professional color scheme for documents
        self.colors = {
            "primary": colors.HexColor("#1e3a8a"),
            "secondary": colors.HexColor("#2563eb"),
            "accent": colors.HexColor("#059669"),
            "success": colors.HexColor("#10b981"),
            "warning": colors.HexColor("#f59e0b"),
            "background": colors.HexColor("#f8fafc"),
            "header_bg": colors.HexColor("#1e40af"),
            "text_dark": colors.HexColor("#1f2937"),
            "text_light": colors.HexColor("#6b7280"),
            "white": colors.white,
            "border": colors.HexColor("#d1d5db"),
            "row_even": colors.white,
            "row_odd": colors.HexColor("#f3f4f6"),
            "paystub_green": colors.HexColor("#065f46"),
            "paystub_light": colors.HexColor("#d1fae5")
        }

        self.create_directories()
        self.clear_all_data()

    def create_directories(self):
        os.makedirs(self.documents_dir, exist_ok=True)

    def clear_all_data(self):
        try:
            if os.path.exists(self.documents_dir):
                for f in os.listdir(self.documents_dir):
                    if f.endswith(('.pdf', '.txt')):
                        try:
                            os.remove(os.path.join(self.documents_dir, f))
                        except Exception:
                            pass
            if os.path.exists(self.employees_file):
                try:
                    os.remove(self.employees_file)
                except Exception:
                    pass
            
            print("🗑️  All previous data cleared!")
            print("✅ EMPLOYMENT VERIFICATION: Professional verification letter") 
            print("✅ EMPLOYMENT CONTRACT: Official school employment contract")
            print("✅ EMPLOYEE PAY STUB: Detailed salary payment stub")
            print("✅ INSTITUTION: Full school name from JSON only")
            print("✅ EMPLOYEE INFO: Name, ID, Position, Department, Salary")
            print("✅ CURRENT DATES: Valid employment dates")
            print("✅ ALL 24 COUNTRIES: Complete global support")
            print("="*70)
        except Exception as e:
            print(f"⚠️  Warning: {e}")

    def load_schools(self):
        """Load schools ONLY from JSON file - no hardcoded data."""
        try:
            if not self.selected_country:
                return []
            
            config = COUNTRY_CONFIG[self.selected_country]
            school_file = config['schoolFile']
            
            print(f"📚 Loading {school_file}...")
            
            if not os.path.exists(school_file):
                print(f"❌ School file {school_file} not found!")
                return []
            
            with open(school_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            schools = []
            for s in data:
                if s.get('name') and s.get('id'):
                    schools.append({
                        'name': s['name'],
                        'id': s['id'],
                        'type': s.get('type', 'SCHOOL')
                    })
            
            print(f"✅ Loaded {len(schools)} schools from {school_file}")
            return schools
            
        except Exception as e:
            print(f"❌ ERROR loading schools from {school_file}: {e}")
            return []

    def get_country_schools(self, country_code):
        """ONLY used as fallback if JSON file is completely missing."""
        print(f"⚠️  No schools loaded from JSON, using minimal fallback")
        return [
            {'name': f'{COUNTRY_CONFIG[country_code]["name"]} High School', 'id': f'SCH001', 'type': 'HIGH_SCHOOL'},
            {'name': f'{COUNTRY_CONFIG[country_code]["name"]} Elementary School', 'id': f'SCH002', 'type': 'ELEMENTARY'}
        ]

    def select_country_and_load(self):
        """Country selection interface with all 24 countries."""
        print("\n🌍 COUNTRY SELECTION - 24 COUNTRIES AVAILABLE")
        print("=" * 70)
        countries = list(COUNTRY_CONFIG.keys())
        
        for i in range(0, len(countries), 4):
            row = countries[i:i+4]
            line = ""
            for country in row:
                config = COUNTRY_CONFIG[country]
                idx = list(COUNTRY_CONFIG.keys()).index(country) + 1
                line += f"{idx:2d}. {config['flag']} {config['name']:18} "
            print(line)
        print("=" * 70)
        
        country_list = list(COUNTRY_CONFIG.keys())
        
        while True:
            try:
                choice = input("\nSelect country (1-24): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= 24:
                    self.selected_country = country_list[int(choice) - 1]
                    break
                else:
                    print("❌ Please enter a number between 1 and 24")
            except (ValueError, IndexError):
                print("❌ Invalid selection. Please try again.")
        
        config = COUNTRY_CONFIG[self.selected_country]
        print(f"\n✅ Selected: {config['flag']} {config['name']} ({self.selected_country})")
        
        self.all_schools = self.load_schools()
        
        if not self.all_schools:
            print("❌ No schools loaded from JSON! Using minimal fallback.")
            self.all_schools = self.get_country_schools(self.selected_country)
        
        # Initialize Faker instances with English names
        try:
            self.faker_instances = [Faker('en_US') for _ in range(20)]
        except:
            self.faker_instances = [Faker() for _ in range(20)]
            
        print("✅ Generator ready!")
        
        return True

    def get_faker(self):
        """Thread-safe Faker instance rotation."""
        with self.faker_lock:
            faker = self.faker_instances[self.faker_index]
            self.faker_index = (self.faker_index + 1) % len(self.faker_instances)
            return faker

    def select_random_school(self):
        """Select a random school from JSON data only."""
        if not self.all_schools:
            config = COUNTRY_CONFIG.get(self.selected_country, COUNTRY_CONFIG['US'])
            return {'name': f'{config["name"]} School District', 'id': 'SCH001', 'type': 'SCHOOL'}
        return random.choice(self.all_schools)

    def generate_salary_data(self, country_config):
        """Generate realistic salary data for employment documents."""
        salary_min, salary_max = country_config['salary_range']
        bonus_min, bonus_max = country_config['bonus_range']
        
        annual_salary = random.randint(salary_min, salary_max)
        monthly_salary = annual_salary / 12
        bonus_amount = random.randint(bonus_min, bonus_max)
        
        # Deductions
        tax_rate = random.uniform(0.20, 0.35)
        tax_amount = monthly_salary * tax_rate
        insurance = monthly_salary * 0.05
        retirement = monthly_salary * 0.03
        total_deductions = tax_amount + insurance + retirement
        net_pay = monthly_salary - total_deductions
        
        # Generate payment dates
        payment_date = datetime.now() - timedelta(days=random.randint(1, 30))
        pay_period_start = payment_date - timedelta(days=30)
        pay_period_end = payment_date - timedelta(days=1)
        
        return {
            "annual_salary": annual_salary,
            "monthly_salary": monthly_salary,
            "bonus_amount": bonus_amount,
            "tax_amount": tax_amount,
            "insurance": insurance,
            "retirement": retirement,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
            "payment_date": payment_date,
            "pay_period_start": pay_period_start,
            "pay_period_end": pay_period_end,
            "payment_method": random.choice(["Direct Deposit", "Bank Transfer", "Check"]),
            "transaction_id": f"PAY{random.randint(100000, 999999)}"
        }

    def generate_employee_data(self, school):
        """Generate employee data with CURRENT employment dates."""
        fake = self.get_faker()
        config = COUNTRY_CONFIG[self.selected_country]
        
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = clean_name(f"{first_name} {last_name}")
        employee_id = f"EMP{fake.random_number(digits=6, fix_len=True)}"
        
        # CURRENT EMPLOYMENT DATES for verification
        current_date = datetime.now()
        
        # Generate employment dates (hired 1-5 years ago)
        years_employed = random.randint(1, 5)
        hire_date = current_date - timedelta(days=365 * years_employed + random.randint(0, 364))
        
        # Contract end date (if applicable)
        contract_type = random.choice(config['contract_types'])
        if "Contract" in contract_type or "Temporary" in contract_type or "Fixed" in contract_type:
            contract_end = current_date + timedelta(days=random.randint(180, 730))  # 6-24 months
        else:
            contract_end = None  # Permanent position
        
        # Country-specific positions
        positions_by_country = {
            'US': ["Teacher", "Senior Teacher", "Department Head", "Vice Principal", "Principal"],
            'GB': ["Teacher", "Senior Teacher", "Head of Department", "Deputy Head", "Head Teacher"],
            'IN': ["Teacher", "Senior Teacher", "Head of Department", "Vice Principal", "Principal"],
            'ID': ["Guru", "Guru Senior", "Kepala Jurusan", "Wakil Kepala Sekolah", "Kepala Sekolah"],
            'DE': ["Lehrer", "Oberlehrer", "Fachbereichsleiter", "Konrektor", "Rektor"],
            'FR': ["Professeur", "Professeur Principal", "Chef de Département", "Principal Adjoint", "Principal"],
            'ES': ["Profesor", "Profesor Titular", "Jefe de Departamento", "Subdirector", "Director"],
            'IT': ["Insegnante", "Insegnante Esperto", "Capo Dipartimento", "Vice Preside", "Preside"],
            'JP': ["教師", "主任教師", "学科主任", "教頭", "校長"],
            'KR': ["교사", "주임교사", "학과장", "교감", "교장"]
        }
        
        positions = positions_by_country.get(self.selected_country, ["Teacher", "Senior Teacher", "Department Head"])
        departments = config.get('departments', ["Mathematics", "Science", "English"])
        
        # Generate salary data
        salary_data = self.generate_salary_data(config)
        
        return {
            "full_name": full_name,
            "employee_id": employee_id,
            "school": school,
            "position": random.choice(positions),
            "department": random.choice(departments),
            "contract_type": contract_type,
            "hire_date": hire_date,
            "contract_end": contract_end,
            "current_date": current_date,
            "years_employed": years_employed,
            "country_config": config,
            "salary_data": salary_data
        }

    def format_currency(self, amount, country_config):
        """Format currency according to country preferences."""
        symbol = country_config['currency_symbol']
        currency = country_config['currency']
        
        if currency in ['USD', 'CAD', 'AUD', 'SGD', 'NZD']:
            return f"{symbol}{amount:,.2f}"
        elif currency in ['EUR', 'GBP']:
            return f"{symbol}{amount:,.2f}"
        elif currency in ['JPY', 'KRW']:
            return f"{symbol}{amount:,.0f}"
        elif currency in ['IDR']:
            return f"{symbol} {amount:,.0f}"
        else:
            return f"{symbol} {amount:,.2f}"

    def format_date(self, date_obj, country_config):
        """Format date according to country preferences."""
        return date_obj.strftime(country_config['date_format'])

    def create_employment_verification_letter(self, employee_data):
        """Create a professional employment verification letter."""
        school = employee_data['school']
        employee_id = employee_data['employee_id']
        school_id = school['id']
        config = employee_data['country_config']

        filename = f"VERIFICATION_{employee_id}_{school_id}.pdf"
        filepath = os.path.join(self.documents_dir, filename)

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=20
            )
            
            # Container for the 'Flowable' objects
            elements = []
            styles = getSampleStyleSheet()
            
            # School Letterhead
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=self.colors['primary'],
                alignment=0,
                spaceAfter=20
            )
            
            header = Paragraph(school['name'], header_style)
            elements.append(header)
            
            # Address line
            address_style = ParagraphStyle(
                'AddressStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=0,
                spaceAfter=15
            )
            
            fake = self.get_faker()
            address = Paragraph(f"{fake.street_address()} • {fake.city()} • {fake.postcode()} • {config['name']}", address_style)
            elements.append(address)
            
            elements.append(Spacer(1, 30))
            
            # Date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=self.colors['text_dark'],
                alignment=0,
                spaceAfter=20
            )
            
            current_date = self.format_date(employee_data['current_date'], config)
            date_line = Paragraph(current_date, date_style)
            elements.append(date_line)
            
            elements.append(Spacer(1, 20))
            
            # Title
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=self.colors['primary'],
                alignment=0,
                spaceAfter=20
            )
            
            title = Paragraph("EMPLOYMENT VERIFICATION LETTER", title_style)
            elements.append(title)
            
            # To Whom It May Concern
            to_style = ParagraphStyle(
                'ToStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=self.colors['text_dark'],
                alignment=0,
                spaceAfter=20
            )
            
            to_line = Paragraph("To Whom It May Concern,", to_style)
            elements.append(to_line)
            
            # Body text
            body_style = ParagraphStyle(
                'BodyStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=self.colors['text_dark'],
                alignment=4,  # Justify
                spaceAfter=10,
                leading=14
            )
            
            # Generate letter content
            hire_date = self.format_date(employee_data['hire_date'], config)
            annual_salary = self.format_currency(employee_data['salary_data']['annual_salary'], config)
            
            body_text = f"""
            This letter serves to verify that <b>{employee_data['full_name']}</b> (Employee ID: {employee_id}) 
            has been employed as a <b>{employee_data['position']}</b> in the <b>{employee_data['department']}</b> 
            Department at <b>{school['name']}</b> since <b>{hire_date}</b>.
            
            During their employment, {employee_data['full_name'].split()[0]} has demonstrated exceptional 
            professionalism and dedication to their role. They are currently employed on a 
            <b>{employee_data['contract_type']}</b> basis and their annual salary is <b>{annual_salary}</b>.
            
            {employee_data['full_name'].split()[0]}'s responsibilities include curriculum development, 
            classroom instruction, student assessment, and participation in departmental meetings 
            and professional development activities.
            
            Their employment status with our institution is <b>ACTIVE</b> and in good standing. 
            {employee_data['full_name'].split()[0]} has consistently met all performance expectations 
            and has been a valuable member of our educational team.
            """
            
            body = Paragraph(body_text, body_style)
            elements.append(body)
            
            elements.append(Spacer(1, 20))
            
            # Sincerely section
            sincerely_style = ParagraphStyle(
                'SincerelyStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=self.colors['text_dark'],
                alignment=0,
                spaceAfter=5
            )
            
            sincerely = Paragraph("Sincerely,", sincerely_style)
            elements.append(sincerely)
            
            elements.append(Spacer(1, 30))
            
            # Signature section
            signature_style = ParagraphStyle(
                'SignatureStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=self.colors['primary'],
                alignment=0,
                spaceAfter=5
            )
            
            principal_names = ["Dr. Robert Johnson", "Ms. Sarah Williams", "Mr. Michael Brown", 
                             "Dr. Jennifer Davis", "Mr. James Wilson", "Ms. Patricia Miller"]
            signature = Paragraph(random.choice(principal_names), signature_style)
            elements.append(signature)
            
            position_style = ParagraphStyle(
                'PositionStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=0
            )
            
            position = Paragraph("Principal / Head of School", position_style)
            elements.append(position)
            
            elements.append(Spacer(1, 10))
            
            # Contact information
            contact_style = ParagraphStyle(
                'ContactStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=self.colors['text_light'],
                alignment=0
            )
            
            contact = Paragraph(f"{school['name']} • Tel: {fake.phone_number()} • Email: hr@{school['name'].lower().replace(' ', '')}.edu", contact_style)
            elements.append(contact)
            
            # Footer
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceBefore=30
            )
            
            footer = Paragraph(
                f"Official Verification Letter • {school['name']} • {current_date} • Valid for employment verification purposes",
                footer_style
            )
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            return filename, employee_data
            
        except Exception as e:
            logger.error(f"Failed to create verification letter {filename}: {e}")
            return None, employee_data

    def create_employment_contract(self, employee_data):
        """Create a professional employment contract."""
        school = employee_data['school']
        employee_id = employee_data['employee_id']
        school_id = school['id']
        config = employee_data['country_config']

        filename = f"CONTRACT_{employee_id}_{school_id}.pdf"
        filepath = os.path.join(self.documents_dir, filename)

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=20
            )
            
            # Container for the 'Flowable' objects
            elements = []
            styles = getSampleStyleSheet()
            
            # Header
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=self.colors['primary'],
                alignment=1,
                spaceAfter=10
            )
            
            header = Paragraph("EMPLOYMENT CONTRACT", header_style)
            elements.append(header)
            
            # School Name
            school_style = ParagraphStyle(
                'SchoolStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=self.colors['secondary'],
                alignment=1,
                spaceAfter=20
            )
            
            school_name = Paragraph(school['name'], school_style)
            elements.append(school_name)
            
            elements.append(Spacer(1, 15))
            
            # Contract Information
            contract_info_style = ParagraphStyle(
                'ContractInfoStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceAfter=15
            )
            
            contract_id = f"CON{random.randint(10000, 99999)}"
            contract_info = Paragraph(f"Contract ID: {contract_id} • Effective Date: {self.format_date(employee_data['hire_date'], config)}", contract_info_style)
            elements.append(contract_info)
            
            # Parties Section
            parties_title_style = ParagraphStyle(
                'PartiesTitleStyle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.colors['primary'],
                spaceAfter=10
            )
            
            parties_title = Paragraph("PARTIES TO THIS AGREEMENT", parties_title_style)
            elements.append(parties_title)
            
            # Parties Table
            parties_data = [
                ["EMPLOYER:", f"{school['name']}"],
                ["ADDRESS:", f"{self.get_faker().street_address()}, {self.get_faker().city()}, {self.get_faker().postcode()}"],
                ["EMPLOYEE:", employee_data["full_name"]],
                ["EMPLOYEE ID:", employee_id],
                ["POSITION:", employee_data["position"]],
                ["DEPARTMENT:", employee_data["department"]]
            ]
            
            parties_table = Table(parties_data, colWidths=[1.5*inch, 4.5*inch])
            parties_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('BACKGROUND', (0, 0), (0, -1), self.colors['row_odd']),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 1, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(parties_table)
            elements.append(Spacer(1, 15))
            
            # Terms and Conditions
            terms_title = Paragraph("TERMS AND CONDITIONS", parties_title_style)
            elements.append(terms_title)
            
            # Terms content
            terms_style = ParagraphStyle(
                'TermsStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_dark'],
                alignment=4,  # Justify
                spaceAfter=8,
                leading=12
            )
            
            annual_salary = self.format_currency(employee_data['salary_data']['annual_salary'], config)
            hire_date = self.format_date(employee_data['hire_date'], config)
            contract_end = self.format_date(employee_data['contract_end'], config) if employee_data['contract_end'] else "Ongoing"
            
            terms = [
                f"<b>1. EMPLOYMENT TERM:</b> This contract begins on {hire_date} and continues {contract_end if employee_data['contract_end'] else 'until terminated by either party with appropriate notice'}.",
                f"<b>2. POSITION AND DUTIES:</b> The Employee shall serve as {employee_data['position']} in the {employee_data['department']} Department.",
                f"<b>3. COMPENSATION:</b> The Employee shall receive an annual salary of {annual_salary}, payable in accordance with the school's standard payroll schedule.",
                f"<b>4. WORK SCHEDULE:</b> Standard working hours are 8:00 AM to 4:00 PM, Monday through Friday, with additional hours as needed for school activities.",
                f"<b>5. BENEFITS:</b> The Employee is entitled to participate in the school's benefits program including health insurance, retirement plan, and paid leave.",
                f"<b>6. PROFESSIONAL DEVELOPMENT:</b> The school will provide opportunities for professional growth and development relevant to the Employee's position.",
                f"<b>7. CONFIDENTIALITY:</b> The Employee agrees to maintain confidentiality of all student records and school information.",
                f"<b>8. TERMINATION:</b> Either party may terminate this agreement with 30 days written notice."
            ]
            
            for term in terms:
                elements.append(Paragraph(term, terms_style))
                elements.append(Spacer(1, 5))
            
            elements.append(Spacer(1, 15))
            
            # Signatures Section
            signatures_title = Paragraph("SIGNATURES", parties_title_style)
            elements.append(signatures_title)
            
            # Signatures table
            signatures_data = [
                ["FOR THE SCHOOL:", "", "EMPLOYEE:"],
                ["", "", ""],
                ["________________________", "", "________________________"],
                ["Principal / Head of School", "", employee_data["full_name"]],
                [f"{school['name']}", "", "Employee"],
                [f"Date: {self.format_date(employee_data['current_date'], config)}", "", f"Date: {self.format_date(employee_data['current_date'], config)}"]
            ]
            
            signatures_table = Table(signatures_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
            signatures_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 2), (-1, 2), 'Helvetica', 10),
                ('FONT', (0, 3), (-1, 4), 'Helvetica', 9),
                ('FONT', (0, 5), (-1, 5), 'Helvetica', 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEABOVE', (0, 2), (0, 2), 1, self.colors['text_dark']),
                ('LINEABOVE', (2, 2), (2, 2), 1, self.colors['text_dark']),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(signatures_table)
            
            # Footer
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceBefore=20
            )
            
            footer = Paragraph(
                f"Official Employment Contract • {school['name']} • {contract_id} • For verification purposes only",
                footer_style
            )
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            logger.error(f"Failed to create employment contract {filename}: {e}")
            return None

    def create_employee_pay_stub(self, employee_data):
        """Create a professional employee pay stub."""
        school = employee_data['school']
        employee_id = employee_data['employee_id']
        school_id = school['id']
        config = employee_data['country_config']
        salary_data = employee_data['salary_data']

        filename = f"PAYSTUB_{employee_id}_{school_id}.pdf"
        filepath = os.path.join(self.documents_dir, filename)

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=20
            )
            
            # Container for the 'Flowable' objects
            elements = []
            styles = getSampleStyleSheet()
            
            # Header
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=self.colors['primary'],
                alignment=1,
                spaceAfter=10
            )
            
            header = Paragraph("EMPLOYEE PAY STUB", header_style)
            elements.append(header)
            
            # School Name
            school_style = ParagraphStyle(
                'SchoolStyle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.colors['secondary'],
                alignment=1,
                spaceAfter=15
            )
            
            school_name = Paragraph(school['name'], school_style)
            elements.append(school_name)
            
            # Pay Period Information
            period_style = ParagraphStyle(
                'PeriodStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceAfter=20
            )
            
            pay_period = f"Pay Period: {self.format_date(salary_data['pay_period_start'], config)} - {self.format_date(salary_data['pay_period_end'], config)}"
            pay_date = f"Pay Date: {self.format_date(salary_data['payment_date'], config)}"
            period_info = Paragraph(f"{pay_period} | {pay_date}", period_style)
            elements.append(period_info)
            
            # Employee Information Table
            employee_info_title_style = ParagraphStyle(
                'EmployeeInfoTitleStyle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=self.colors['primary'],
                spaceAfter=8
            )
            
            employee_info_title = Paragraph("EMPLOYEE INFORMATION", employee_info_title_style)
            elements.append(employee_info_title)
            
            employee_info_data = [
                ["Employee Name:", employee_data["full_name"]],
                ["Employee ID:", employee_id],
                ["Position:", employee_data["position"]],
                ["Department:", employee_data["department"]],
                ["Contract Type:", employee_data["contract_type"]],
                ["Pay Method:", salary_data["payment_method"]]
            ]
            
            employee_info_table = Table(employee_info_data, colWidths=[1.5*inch, 4.5*inch])
            employee_info_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('BACKGROUND', (0, 0), (0, -1), self.colors['row_odd']),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 1, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(employee_info_table)
            elements.append(Spacer(1, 15))
            
            # Earnings Section
            earnings_title = Paragraph("EARNINGS", employee_info_title_style)
            elements.append(earnings_title)
            
            earnings_data = [
                ["Description", "Rate", "Hours/Days", "Current", "YTD"],
                ["Monthly Salary", f"{self.format_currency(salary_data['monthly_salary']/160, config)}/hr", "160.00", self.format_currency(salary_data['monthly_salary'], config), self.format_currency(salary_data['annual_salary'] * (employee_data['years_employed'] + 0.5), config)],
                ["Bonus Payment", "", "", self.format_currency(salary_data['bonus_amount']/12, config), self.format_currency(salary_data['bonus_amount'], config)],
                ["", "", "", "", ""],
                ["TOTAL EARNINGS", "", "", self.format_currency(salary_data['monthly_salary'] + salary_data['bonus_amount']/12, config), self.format_currency((salary_data['annual_salary'] + salary_data['bonus_amount']) * (employee_data['years_employed'] + 0.5), config)]
            ]
            
            earnings_table = Table(earnings_data, colWidths=[1.8*inch, 1*inch, 1*inch, 1.2*inch, 1.2*inch])
            earnings_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid and styling
                ('LINEABOVE', (0, -1), (-1, -1), 2, self.colors['paystub_green']),
                ('BACKGROUND', (0, -1), (-1, -1), self.colors['paystub_light']),
                ('TEXTCOLOR', (0, -1), (-1, -1), self.colors['paystub_green']),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.colors['border']),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(earnings_table)
            elements.append(Spacer(1, 10))
            
            # Deductions Section
            deductions_title = Paragraph("DEDUCTIONS", employee_info_title_style)
            elements.append(deductions_title)
            
            deductions_data = [
                ["Description", "Current", "YTD"],
                ["Income Tax", self.format_currency(salary_data['tax_amount'], config), self.format_currency(salary_data['tax_amount'] * 12, config)],
                ["Health Insurance", self.format_currency(salary_data['insurance'], config), self.format_currency(salary_data['insurance'] * 12, config)],
                ["Retirement Plan", self.format_currency(salary_data['retirement'], config), self.format_currency(salary_data['retirement'] * 12, config)],
                ["", "", ""],
                ["TOTAL DEDUCTIONS", self.format_currency(salary_data['total_deductions'], config), self.format_currency(salary_data['total_deductions'] * 12, config)]
            ]
            
            deductions_table = Table(deductions_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            deductions_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid and styling
                ('LINEABOVE', (0, -1), (-1, -1), 2, colors.red),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#fee2e2")),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.red),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.colors['border']),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(deductions_table)
            elements.append(Spacer(1, 15))
            
            # Net Pay Section
            net_pay_style = ParagraphStyle(
                'NetPayStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=self.colors['success'],
                alignment=1,
                spaceAfter=10
            )
            
            net_pay_data = [
                ["NET PAY", self.format_currency(salary_data['net_pay'], config)],
                ["Payment Method", salary_data['payment_method']],
                ["Transaction ID", salary_data['transaction_id']]
            ]
            
            net_pay_table = Table(net_pay_data, colWidths=[3*inch, 3*inch])
            net_pay_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 14),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('TEXTCOLOR', (0, 0), (0, 0), self.colors['success']),
                ('TEXTCOLOR', (1, 0), (1, 0), self.colors['success']),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEABOVE', (0, 0), (-1, 0), 3, self.colors['success']),
                ('LINEBELOW', (0, 0), (-1, 0), 3, self.colors['success']),
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['paystub_light']),
                ('BOX', (0, 0), (-1, -1), 1, self.colors['success']),
                ('PADDING', (0, 0), (-1, -1), 12),
            ]))
            
            elements.append(net_pay_table)
            
            # Footer
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceBefore=20
            )
            
            footer = Paragraph(
                f"Official Pay Stub • {school['name']} • Transaction ID: {salary_data['transaction_id']} • For verification purposes only",
                footer_style
            )
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            logger.error(f"Failed to create pay stub {filename}: {e}")
            return None

    def save_employee(self, employee_data):
        """Save employee data to file."""
        try:
            with open(self.employees_file, 'a', encoding='utf-8', buffering=32768) as f:
                contract_end = employee_data['contract_end'].strftime('%Y-%m-%d') if employee_data['contract_end'] else 'PERMANENT'
                line = f"{employee_data['full_name']}|{employee_data['employee_id']}|{employee_data['school']['id']}|{employee_data['school']['name']}|{self.selected_country}|{employee_data['position']}|{employee_data['contract_type']}|{employee_data['hire_date'].strftime('%Y-%m-%d')}|{contract_end}|{employee_data['salary_data']['annual_salary']}|{employee_data['salary_data']['transaction_id']}\n"
                f.write(line)
                f.flush()

            self.stats["employees_saved"] += 1
            return True
        except Exception as e:
            logger.error(f"⚠️ Save error: {e}")
            return False

    def process_one(self, num):
        try:
            school = self.select_random_school()
            if school is None:
                return False
            
            employee_data = self.generate_employee_data(school)
                
            # Generate all three employment documents
            verification_filename, _ = self.create_employment_verification_letter(employee_data)
            contract_filename = self.create_employment_contract(employee_data)
            paystub_filename = self.create_employee_pay_stub(employee_data)
            
            if verification_filename and contract_filename and paystub_filename:
                self.save_employee(employee_data)
                self.stats["documents_generated"] += 1
                return True
            return False
        except Exception as e:
            logger.error(f"Error processing employee {num}: {e}")
            return False

    def generate_bulk(self, quantity):
        config = COUNTRY_CONFIG[self.selected_country]
        print(f"⚡ Generating {quantity} EMPLOYMENT DOCUMENTS for {config['flag']} {config['name']}")
        print(f"✅ {len(self.all_schools)} schools loaded from JSON")
        print("✅ EMPLOYMENT VERIFICATION: Professional verification letter")
        print("✅ EMPLOYMENT CONTRACT: Official school employment contract")
        print("✅ EMPLOYEE PAY STUB: Detailed salary payment stub")
        print("✅ INSTITUTION: Full school names from JSON only")
        print("✅ EMPLOYEE INFO: Name, ID, Position, Department, Salary")
        print("✅ CURRENT DATES: Valid employment dates")
        print("✅ VERIFICATION READY: Perfect for employment verification")
        print("=" * 70)

        start = time.time()
        success = 0
        
        # Process in chunks for better memory management
        chunk_size = 50
        
        for chunk_start in range(0, quantity, chunk_size):
            chunk_end = min(chunk_start + chunk_size, quantity)
            chunk_qty = chunk_end - chunk_start
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self.process_one, i+1) for i in range(chunk_start, chunk_end)]
                
                for i, future in enumerate(concurrent.futures.as_completed(futures), chunk_start + 1):
                    if future.result():
                        success += 1
                    
                    if i % 10 == 0 or i == quantity:
                        elapsed = time.time() - start
                        rate = i / elapsed if elapsed > 0 else 0
                        rate_per_min = rate * 60
                        print(f"Progress: {i}/{quantity} ({(i/quantity*100):.1f}%) | Rate: {rate_per_min:.0f} sets/min")
        
        duration = time.time() - start
        rate_per_min = (success / duration) * 60 if duration > 0 else 0
        
        print("\n" + "="*70)
        print(f"✅ COMPLETE - {config['flag']} {config['name']}")
        print("="*70)
        print(f"⏱️  Time: {duration:.1f}s")
        print(f"⚡ Speed: {rate_per_min:.0f} document sets/minute")
        print(f"✅ Success: {success}/{quantity}")
        print(f"📁 Folder: {self.documents_dir}/")
        print(f"📄 Employees: {self.employees_file}")
        print(f"✅ VERIFICATION LETTER: Professional employment verification")
        print(f"✅ EMPLOYMENT CONTRACT: Official school contract")
        print(f"✅ PAY STUB: Detailed salary payment information")
        print(f"✅ INSTITUTION: Names from JSON files only")
        print(f"✅ DATES: Current employment dates")
        print(f"✅ VERIFICATION: Perfect for employment verification")
        print("="*70)

    def interactive(self):
        total = 0
        config = COUNTRY_CONFIG[self.selected_country]
        
        while True:
            print(f"\n{'='*60}")
            print(f"Country: {config['flag']} {config['name']}")
            print(f"Total Generated: {total}")
            print(f"Schools from JSON: {len(self.all_schools)}")
            print(f"Mode: Employment verification + contract + pay stub")
            print(f"Institution: JSON names only")
            print(f"Dates: Current employment dates")
            print(f"Verification: Employment verification ready")
            print(f"{'='*60}")
            
            user_input = input(f"\nQuantity (0 to exit): ").strip()
            
            if user_input == "0":
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
            total = self.stats["documents_generated"]

def main():
    print("\n" + "="*70)
    print("PROFESSIONAL EMPLOYMENT DOCUMENT GENERATOR - VERIFICATION READY")
    print("="*70)
    print("✅ EMPLOYMENT VERIFICATION: Professional verification letter")
    print("✅ EMPLOYMENT CONTRACT: Official school employment contract")
    print("✅ EMPLOYEE PAY STUB: Detailed salary payment stub")
    print("✅ INSTITUTION: Full school names from JSON only")
    print("✅ EMPLOYEE INFO: Name, ID, Position, Department, Salary")
    print("✅ CURRENT DATES: Valid employment dates")
    print("✅ INSTANT VERIFICATION: Super-fast verification system")
    print("✅ PERFECT FORMAT: Professional PDF layout")
    print("✅ ALL 24 COUNTRIES: Complete global support")
    print("="*70)
    
    gen = ProfessionalEmploymentDocumentGenerator()
    
    if not gen.select_country_and_load():
        return
    
    gen.interactive()
    
    print("\n✅ FINISHED! All documents are employment verification ready!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")