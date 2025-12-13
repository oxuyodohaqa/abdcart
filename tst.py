#!/usr/bin/env python3
"""
PROFESSIONAL EDUCATOR VERIFICATION DOCUMENT GENERATOR - USA K-12 SCHOOLS
✅ EMPLOYMENT LETTER: Official school-issued employment verification
✅ EMPLOYMENT CONTRACT: School employment agreement with key terms
✅ PAY STUB: Recent salary payment documentation
✅ ALL REQUIRED DETAILS: Full name, job title, school name, dates
✅ K-12 SPECIFIC: Elementary, Middle, and High Schools
✅ SCHOOL LETTERHEAD: Official school branding and seals
✅ USA ONLY: United States school system
"""

import sys
import os
import re
import logging
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from faker import Faker
import qrcode
import random
import json
from datetime import datetime, timedelta
from io import BytesIO
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def clean_name(name: str) -> str:
    """Cleans up names."""
    name = re.sub(r"[.,]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

# ==================== USA K-12 SCHOOL CONFIGURATION ====================
K12_SCHOOL_TYPES = {
    'ELEMENTARY': {
        'grades': ['K', '1st', '2nd', '3rd', '4th', '5th'],
        'subjects': ['Reading', 'Mathematics', 'Science', 'Social Studies', 'Art', 'Music', 'Physical Education'],
        'job_titles': ['Elementary Teacher', 'Grade Level Teacher', 'Classroom Teacher',
                      'Special Education Teacher', 'Reading Specialist', 'Math Specialist',
                      'Arts Instructor', 'Music Instructor']
    },
    'MIDDLE': {
        'grades': ['6th', '7th', '8th'],
        'subjects': ['English Language Arts', 'Mathematics', 'Science', 'Social Studies',
                    'Foreign Language', 'Art', 'Music', 'Physical Education', 'Technology'],
        'job_titles': ['Middle School Teacher', 'Subject Teacher', 'Special Education Teacher',
                      'STEM Instructor', 'Language Instructor', 'Arts Instructor']
    },
    'HIGH': {
        'grades': ['9th', '10th', '11th', '12th'],
        'subjects': ['English', 'Mathematics', 'Science', 'Social Studies', 'Foreign Language',
                    'Art', 'Music', 'Physical Education', 'Technology', 'Career Education'],
        'job_titles': ['High School Teacher', 'Subject Teacher', 'Special Education Teacher',
                      'AP Instructor', 'Honors Instructor', 'Career Education Instructor']
    }
}

USA_CONFIG = {
    'name': 'United States',
    'code': 'US',
    'currency': 'USD',
    'currency_symbol': '$',
    'date_format': '%B %d, %Y',
    'school_year': '2024-2025',
    'flag': '🇺🇸',
    'salary_range': (35000, 85000),
    'address_format': '{street}, {city}, {state} {zip_code}',
    'states': [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ]
}

def normalize_school_type(value: str):
    if not value:
        return None

    value = value.strip().lower()
    mapping = {
        "1": "ELEMENTARY",
        "elementary": "ELEMENTARY",
        "k-5": "ELEMENTARY",
        "k5": "ELEMENTARY",
        "primary": "ELEMENTARY",
        "2": "MIDDLE",
        "middle": "MIDDLE",
        "6-8": "MIDDLE",
        "6_8": "MIDDLE",
        "junior": "MIDDLE",
        "junior-high": "MIDDLE",
        "3": "HIGH",
        "high": "HIGH",
        "9-12": "HIGH",
        "912": "HIGH",
        "senior": "HIGH"
    }

    return mapping.get(value)


class EducatorDocumentGenerator:
    def __init__(self, custom_teacher_name=None, custom_school_name=None, preselected_school_type=None):
        self.documents_dir = "educator_documents"
        self.employees_file = "educators.txt"
        self.selected_school_type = preselected_school_type if preselected_school_type in K12_SCHOOL_TYPES else None
        self.schools = []

        self.logo_cache = {}

        self.custom_teacher_name = clean_name(custom_teacher_name) if custom_teacher_name else None
        self.custom_school_name = clean_name(custom_school_name) if custom_school_name else None
        self.custom_school_data = None
        
        self.faker = Faker('en_US')
        
        # Professional color scheme
        self.colors = {
            "primary": colors.HexColor("#1e3a8a"),  # Navy blue
            "secondary": colors.HexColor("#2563eb"),  # Royal blue
            "accent": colors.HexColor("#059669"),  # Emerald green
            "background": colors.HexColor("#f8fafc"),
            "header_bg": colors.HexColor("#1e40af"),
            "text_dark": colors.HexColor("#1f2937"),
            "text_light": colors.HexColor("#6b7280"),
            "white": colors.white,
            "border": colors.HexColor("#d1d5db"),
            "row_even": colors.white,
            "row_odd": colors.HexColor("#f3f4f6")
        }

        self.create_directories()
        self.clear_all_data()
    
    def create_directories(self):
        os.makedirs(self.documents_dir, exist_ok=True)

    def generate_school_logo(self, school_name: str) -> str:
        """Generate a simple school logo image using initials and return the file path."""
        if not school_name:
            return ""

        cache_key = school_name.strip().lower()
        if cache_key in self.logo_cache:
            return self.logo_cache[cache_key]

        slug = re.sub(r"[^A-Za-z0-9]+", "_", cache_key).strip("_") or "school"
        logo_path = os.path.join(self.documents_dir, f"{slug}_logo.png")

        primary_rgb = (30, 58, 138)
        accent_rgb = (5, 150, 105)
        text_rgb = (255, 255, 255)

        img_size = 240
        img = Image.new("RGB", (img_size, img_size), primary_rgb)
        draw = ImageDraw.Draw(img)

        inset = 16
        draw.rounded_rectangle(
            [(inset, inset), (img_size - inset, img_size - inset)],
            radius=28,
            outline=accent_rgb,
            width=6
        )

        initials = "".join(part[0].upper() for part in school_name.split()[:3] if part) or "EDU"
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 96)
        except Exception:
            font = ImageFont.load_default()

        try:
            bbox = draw.textbbox((0, 0), initials, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except Exception:
            text_width, text_height = font.getsize(initials)

        text_x = (img_size - text_width) / 2
        text_y = (img_size - text_height) / 2
        draw.text((text_x, text_y), initials, fill=text_rgb, font=font)

        img.save(logo_path, format="PNG")
        self.logo_cache[cache_key] = logo_path
        return logo_path
    
    def clear_all_data(self):
        try:
            if os.path.exists(self.documents_dir):
                for f in os.listdir(self.documents_dir):
                    if f.endswith('.pdf'):
                        os.remove(os.path.join(self.documents_dir, f))
            
            if os.path.exists(self.employees_file):
                os.remove(self.employees_file)

            print("🗑️  All previous data cleared!")
            print("✅ EMPLOYMENT LETTER: Official school verification")
            print("✅ EMPLOYMENT CONTRACT: Detailed school agreement")
            print("✅ PAY STUB: Recent salary documentation")
            print("✅ LETTERHEAD: Official school branding")
            print("✅ REQUIRED DETAILS: Name, Title, School, Dates")
            print("✅ K-12 SPECIFIC: Elementary/Middle/High Schools")
            print("✅ USA ONLY: United States school system")
            print("="*70)
        except Exception as e:
            print(f"⚠️  Warning: {e}")
    
    def load_schools(self):
        """Load schools from JSON file or generate sample schools."""
        try:
            if os.path.exists('schools_us.json'):
                with open('schools_us.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Filter schools by type
                filtered_schools = []
                for school in data:
                    if school.get('type') == self.selected_school_type:
                        filtered_schools.append({
                            'name': school['name'],
                            'address': school.get('address', ''),
                            'district': school.get('district', ''),
                            'phone': school.get('phone', ''),
                            'email': school.get('email', ''),
                            'principal': school.get('principal', 'Dr. John Smith')
                        })
                
                if filtered_schools:
                    print(f"✅ Loaded {len(filtered_schools)} {self.selected_school_type} schools from JSON")
                    return filtered_schools
        except Exception as e:
            print(f"⚠️  Could not load schools from JSON: {e}")
        
        # Generate sample schools if no JSON file
        print("📝 Generating sample schools...")
        
        school_prefix = ""
        if self.selected_school_type == 'ELEMENTARY':
            school_prefix = random.choice(['Oak', 'Maple', 'Pine', 'Sunset', 'Riverside', 'Hilltop'])
            suffix = random.choice(['Elementary School', 'Primary School', 'Elementary'])
        elif self.selected_school_type == 'MIDDLE':
            school_prefix = random.choice(['Central', 'West', 'East', 'North', 'South', 'Community'])
            suffix = random.choice(['Middle School', 'Junior High School'])
        else:  # HIGH
            school_prefix = random.choice(['Lincoln', 'Washington', 'Jefferson', 'Roosevelt', 'Kennedy', 'Madison'])
            suffix = random.choice(['High School', 'Senior High School'])
        
        sample_schools = []
        for i in range(10):
            city = self.faker.city()
            state = random.choice(USA_CONFIG['states'])
            sample_schools.append({
                'name': f"{school_prefix} {suffix}",
                'address': f"{self.faker.street_address()}, {city}, {state} {self.faker.zipcode()}",
                'district': f"{city} School District",
                'phone': f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                'email': f"info@{school_prefix.lower()}{suffix.replace(' ', '').lower()}.edu",
                'principal': f"Dr. {self.faker.last_name()}"
            })
        
        return sample_schools
    
    def select_school_type(self):
        """Select school type: Elementary, Middle, or High School."""
        print("\n🏫 SELECT SCHOOL TYPE")
        print("=" * 70)
        print("1. Elementary School (K-5)")
        print("2. Middle School (6-8)")
        print("3. High School (9-12)")
        print("=" * 70)

        if self.selected_school_type:
            print(f"✅ Using preselected option: {self.selected_school_type} School")
        else:
            while True:
                choice = input("\nSelect school type (1-3): ").strip()
                normalized = normalize_school_type(choice)
                if normalized:
                    self.selected_school_type = normalized
                    break
                else:
                    print("❌ Please enter 1, 2, or 3")

        self.schools = self.load_schools()
        print(f"✅ Selected: {self.selected_school_type} School")
        print(f"📚 Schools available: {len(self.schools)}")

        return True
    
    def generate_educator_data(self):
        """Generate educator data with all required fields."""
        if self.custom_teacher_name:
            name_parts = self.custom_teacher_name.split()
            if len(name_parts) >= 2:
                first_name, last_name = name_parts[0], name_parts[-1]
            else:
                first_name = self.custom_teacher_name
                last_name = self.faker.last_name()
            full_name = self.custom_teacher_name
        else:
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            full_name = clean_name(f"{first_name} {last_name}")

        if self.custom_school_name:
            if not self.custom_school_data:
                city = self.faker.city()
                state = random.choice(USA_CONFIG['states'])
                domain = re.sub(r"[^a-zA-Z0-9]", "", self.custom_school_name).lower()
                self.custom_school_data = {
                    'name': self.custom_school_name,
                    'address': f"{self.faker.street_address()}, {city}, {state} {self.faker.zipcode()}",
                    'district': f"{city} School District",
                    'phone': f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                    'email': f"info@{domain or 'school'}.edu",
                    'principal': f"Dr. {self.faker.last_name()}"
                }
            school = self.custom_school_data
        else:
            school = random.choice(self.schools)
        school_type_config = K12_SCHOOL_TYPES[self.selected_school_type]
        
        # Generate employment data
        employee_id = f"EMP{random.randint(10000, 99999)}"
        hire_date = datetime.now() - timedelta(days=random.randint(30, 1825))  # 1 month to 5 years
        job_title = random.choice(school_type_config['job_titles'])
        
        # Salary data
        salary_min, salary_max = USA_CONFIG['salary_range']
        annual_salary = random.randint(salary_min, salary_max)
        monthly_salary = round(annual_salary / 12, 2)
        
        # Generate class/subject info
        if 'Teacher' in job_title:
            if self.selected_school_type == 'ELEMENTARY':
                grade = random.choice(school_type_config['grades'])
                subject = f"Grade {grade} Homeroom"
            else:
                grade = random.choice(school_type_config['grades'])
                subject = random.choice(school_type_config['subjects'])
                subject = f"{grade} Grade {subject}"
        else:
            grade = ""
            subject = job_title
        
        return {
            "full_name": full_name,
            "employee_id": employee_id,
            "job_title": job_title,
            "school": school,
            "hire_date": hire_date,
            "annual_salary": annual_salary,
            "monthly_salary": monthly_salary,
            "grade_level": grade,
            "subject_area": subject,
            "email": f"{first_name.lower()}.{last_name.lower()}@{school['email'].split('@')[1]}",
            "phone": school['phone'],
            "address": self.faker.address(),
            "date_issued": datetime.now()
        }
    
    def format_currency(self, amount):
        """Format currency as USD."""
        return f"${amount:,.2f}"
    
    def create_employment_letter(self, educator_data):
        """Create official employment verification letter."""
        school = educator_data['school']
        employee_id = educator_data['employee_id']
        
        filename = f"EMPLOYMENT_{employee_id}.pdf"
        filepath = os.path.join(self.documents_dir, filename)
        
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=20
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # Letterhead/Header
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=self.colors['primary'],
                alignment=0,
                spaceAfter=6
            )

            address_style = ParagraphStyle(
                'AddressStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=0,
                spaceAfter=4
            )

            logo_path = self.generate_school_logo(school['name'])
            logo_image = RLImage(logo_path, width=0.85 * inch, height=0.85 * inch) if logo_path else Spacer(0, 0)

            header_block = Paragraph(school['name'], header_style)
            address_block = Paragraph(
                f"{school['address']}<br/>{school['district']}<br/>Phone: {school['phone']}<br/>{USA_CONFIG['flag']} United States",
                address_style
            )

            letterhead_table = Table(
                [[logo_image, header_block], [Spacer(0, 0), address_block]],
                colWidths=[1 * inch, 5 * inch]
            )
            letterhead_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.colors['row_odd']),
                ('BOX', (0, 0), (-1, -1), 0.75, self.colors['border']),
                ('SPAN', (1, 0), (1, 1)),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            elements.append(letterhead_table)

            elements.append(Spacer(1, 24))
            
            # Date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=self.colors['text_dark'],
                alignment=0
            )
            
            current_date = datetime.now().strftime(USA_CONFIG['date_format'])
            date_para = Paragraph(current_date, date_style)
            elements.append(date_para)
            
            elements.append(Spacer(1, 20))
            
            # Subject Line
            subject_style = ParagraphStyle(
                'SubjectStyle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.colors['primary'],
                alignment=0,
                spaceAfter=10
            )
            
            subject = Paragraph("EMPLOYMENT & EDUCATOR STATUS VERIFICATION", subject_style)
            elements.append(subject)
            
            elements.append(Spacer(1, 20))
            
            # Letter Body
            body_style = ParagraphStyle(
                'BodyStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=self.colors['text_dark'],
                alignment=4,  # Justified
                spaceAfter=10
            )
            
            letter_body = f"""
            To Whom It May Concern:<br/><br/>

            This letter confirms that <b>{educator_data['full_name']}</b> (Employee ID: {educator_data['employee_id']})
            is employed full-time at <b>{school['name']}</b>, a K–12 academic institution, during the
            <b>{USA_CONFIG['school_year']} academic year</b>.<br/><br/>

            {educator_data['full_name']} serves as a <b>{educator_data['job_title']}</b> and <b>ACTIVE CLASSROOM INSTRUCTOR</b>.
            As part of their regular assigned duties, they teach
            <b>{educator_data['subject_area']}</b> to <b>{educator_data['grade_level']}</b> students.<br/><br/>

            Employment Status: <b>Full-Time</b><br/>
            Start Date: <b>{educator_data['hire_date'].strftime(USA_CONFIG['date_format'])}</b><br/><br/>

            This letter is issued for educator verification purposes.<br/><br/>
            """
            
            body = Paragraph(letter_body, body_style)
            elements.append(body)
            
            elements.append(Spacer(1, 30))
            
            # Signature Section
            sig_style = ParagraphStyle(
                'SigStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=self.colors['text_dark'],
                alignment=0,
                spaceAfter=5
            )
            
            signature_text = (
                f"Sincerely,<br/><br/><br/>"
                f"{school['principal']}<br/>"
                f"Principal / HR Manager<br/>"
                f"{school['name']}<br/>"
                f"Phone: {school['phone']}<br/>"
                f"Email: {school['email']}"
            )
            signature = Paragraph(signature_text, sig_style)
            elements.append(signature)
            
            # Footer
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceBefore=40
            )
            
            footer = Paragraph(
                "OFFICIAL SCHOOL DOCUMENT • EMPLOYMENT VERIFICATION • CONFIDENTIAL",
                footer_style
            )
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            logger.error(f"Failed to create employment letter: {e}")
            return None
    
    def create_employment_contract(self, educator_data):
        """Create formal school employment contract with key terms."""
        school = educator_data['school']
        employee_id = educator_data['employee_id']

        filename = f"EMPLOYMENT_CONTRACT_{employee_id}.pdf"
        filepath = os.path.join(self.documents_dir, filename)

        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=20
            )

            elements = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'ContractTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=self.colors['primary'],
                alignment=1,
                spaceAfter=12
            )

            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceAfter=20
            )

            section_header = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=13,
                textColor=self.colors['primary'],
                alignment=0,
                spaceAfter=6
            )

            body_style = ParagraphStyle(
                'ContractBody',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                textColor=self.colors['text_dark'],
                alignment=4,
                spaceAfter=10
            )

            logo_path = self.generate_school_logo(school['name'])
            logo_image = RLImage(logo_path, width=0.8 * inch, height=0.8 * inch) if logo_path else Spacer(0, 0)

            letterhead_left = Paragraph(
                f"<b>{school['name']}</b><br/>{school['district']}<br/>{school['address']}<br/>"
                f"Phone: {school['phone']}<br/>Email: {school['email']}",
                ParagraphStyle(
                    'LetterheadLeft',
                    parent=styles['Normal'],
                    fontSize=9,
                    leading=12,
                    textColor=self.colors['text_dark'],
                )
            )

            letterhead_right = Paragraph(
                f"<b>OFFICIAL CONTRACT</b><br/>School Year {USA_CONFIG['school_year']}<br/>"
                f"Issued: {datetime.now().strftime('%B %d, %Y')}<br/>{USA_CONFIG['flag']} United States",
                ParagraphStyle(
                    'LetterheadRight',
                    parent=styles['Normal'],
                    fontSize=9,
                    leading=12,
                    alignment=2,
                    textColor=self.colors['text_dark'],
                )
            )

            letterhead_table = Table(
                [[logo_image, letterhead_left, letterhead_right]],
                colWidths=[0.9 * inch, 3 * inch, 2.1 * inch]
            )
            letterhead_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.colors['row_odd']),
                ('BOX', (0, 0), (-1, -1), 0.75, self.colors['border']),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))

            elements.append(letterhead_table)
            elements.append(Spacer(1, 14))

            elements.append(Paragraph(school['name'], title_style))
            elements.append(Paragraph(f"{school['district']} • {school['address']} • {school['phone']}", subtitle_style))

            contract_title = Paragraph("SCHOOL EMPLOYMENT CONTRACT", title_style)
            elements.append(contract_title)

            summary_data = [
                ["Employee", educator_data['full_name']],
                ["Position", educator_data['job_title']],
                ["Employee ID", educator_data['employee_id']],
                ["Start Date", educator_data['hire_date'].strftime(USA_CONFIG['date_format'])],
                ["Annual Salary", self.format_currency(educator_data['annual_salary'])],
                ["Monthly Salary", self.format_currency(educator_data['monthly_salary'])],
                ["School", school['name']]
            ]

            summary_table = Table(summary_data, colWidths=[1.6*inch, 4.4*inch])
            summary_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('FONT', (1, 0), (1, 0), 'Helvetica-Bold', 11),
                ('BACKGROUND', (0, 0), (0, -1), self.colors['row_odd']),
                ('TEXTCOLOR', (0, 0), (0, -1), self.colors['text_dark']),
                ('TEXTCOLOR', (1, 0), (1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 14))

            responsibilities = (
                f"The employee agrees to perform the duties of {educator_data['job_title']} for {school['name']}, "
                f"including classroom instruction, curriculum planning, student support, and participation in "
                f"school improvement activities for {educator_data['subject_area']}."
            )

            compensation = (
                f"The school will compensate the employee at an annual rate of {self.format_currency(educator_data['annual_salary'])} "
                f"({self.format_currency(educator_data['monthly_salary'])} monthly) in accordance with district payroll schedules, "
                "with eligibility for standard benefits consistent with school policy."
            )

            schedule = (
                "The employee will adhere to the academic calendar and schedule established by the school district, "
                "including required professional development days and parent engagement events."
            )

            compliance = (
                "The employee shall maintain all required licensure, follow district policies and code of conduct, "
                "and comply with federal and state education regulations."
            )

            termination = (
                "Either party may terminate this agreement in accordance with district policy. The school may place the "
                "employee on administrative leave or terminate employment for cause, including misconduct or failure to "
                "maintain required certifications."
            )

            elements.append(Paragraph("POSITION & RESPONSIBILITIES", section_header))
            elements.append(Paragraph(responsibilities, body_style))

            elements.append(Paragraph("COMPENSATION & BENEFITS", section_header))
            elements.append(Paragraph(compensation, body_style))

            elements.append(Paragraph("SCHEDULE & ATTENDANCE", section_header))
            elements.append(Paragraph(schedule, body_style))

            elements.append(Paragraph("COMPLIANCE & CONDUCT", section_header))
            elements.append(Paragraph(compliance, body_style))

            elements.append(Paragraph("TERM & TERMINATION", section_header))
            elements.append(Paragraph(termination, body_style))

            elements.append(Spacer(1, 20))
            elements.append(Paragraph("ACCEPTANCE & SIGNATURES", section_header))

            signature_text = (
                "By signing below, both parties acknowledge and agree to the terms of this employment contract and "
                "confirm that the information provided is accurate."
            )
            elements.append(Paragraph(signature_text, body_style))

            signature_table = Table([
                ["____________________________", "____________________________"],
                [f"{school['principal']}\nPrincipal", f"{educator_data['full_name']}\nEmployee"],
                [datetime.now().strftime('%m/%d/%Y'), datetime.now().strftime('%m/%d/%Y')]
            ], colWidths=[3*inch, 3*inch])
            signature_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONT', (0, 1), (-1, 1), 'Helvetica', 10),
                ('FONT', (0, 2), (-1, 2), 'Helvetica', 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text_dark']),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(signature_table)

            footer_style = ParagraphStyle(
                'ContractFooter',
                parent=styles['Normal'],
                fontSize=8,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceBefore=30
            )

            footer = Paragraph(
                "OFFICIAL SCHOOL DOCUMENT • EMPLOYMENT CONTRACT • CONFIDENTIAL", footer_style
            )
            elements.append(footer)

            doc.build(elements)
            return filename

        except Exception as e:
            logger.error(f"Failed to create employment contract: {e}")
            return None
    
    def create_pay_stub(self, educator_data):
        """Create recent pay stub documentation."""
        employee_id = educator_data['employee_id']
        
        filename = f"PAY_STUB_{employee_id}.pdf"
        filepath = os.path.join(self.documents_dir, filename)
        
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=20
            )
            
            elements = []
            styles = getSampleStyleSheet()

            logo_path = self.generate_school_logo(educator_data['school']['name'])
            logo_image = RLImage(logo_path, width=0.8 * inch, height=0.8 * inch) if logo_path else Spacer(0, 0)

            letterhead_left = Paragraph(
                f"<b>{educator_data['school']['name']}</b><br/>{educator_data['school']['district']}<br/>"
                f"Payroll Department • {educator_data['school']['address']}",
                ParagraphStyle(
                    'PayStubLeft',
                    parent=styles['Normal'],
                    fontSize=9,
                    leading=12,
                    textColor=self.colors['text_dark'],
                )
            )

            letterhead_right = Paragraph(
                f"<b>PAY STUB</b><br/>Issued: {datetime.now().strftime('%B %d, %Y')}<br/>{USA_CONFIG['flag']} Official",
                ParagraphStyle(
                    'PayStubRight',
                    parent=styles['Normal'],
                    fontSize=9,
                    leading=12,
                    alignment=2,
                    textColor=self.colors['text_dark'],
                )
            )

            letterhead_table = Table(
                [[logo_image, letterhead_left, letterhead_right]],
                colWidths=[0.9 * inch, 3 * inch, 2.1 * inch]
            )
            letterhead_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.colors['row_odd']),
                ('BOX', (0, 0), (-1, -1), 0.75, self.colors['border']),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))

            elements.append(letterhead_table)
            elements.append(Spacer(1, 12))

            # Header
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=self.colors['primary'],
                alignment=1,
                spaceAfter=10
            )

            header = Paragraph("EMPLOYEE PAY STUB", header_style)
            elements.append(header)

            # School Info
            school_style = ParagraphStyle(
                'SchoolStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceAfter=15
            )

            school_info = Paragraph(f"{educator_data['school']['name']} • {educator_data['school']['district']}", school_style)
            elements.append(school_info)

            elements.append(Spacer(1, 15))
            
            # Pay Period Info
            pay_date = datetime.now() - timedelta(days=random.randint(1, 30))
            pay_period_start = pay_date - timedelta(days=14)
            
            info_table_data = [
                ["Employee:", educator_data['full_name'], "Employee ID:", educator_data['employee_id']],
                ["Job Title:", educator_data['job_title'], "Pay Date:", pay_date.strftime('%m/%d/%Y')],
                ["Pay Period:", f"{pay_period_start.strftime('%m/%d/%Y')} - {pay_date.strftime('%m/%d/%Y')}", "Check #:", f"{random.randint(10000, 99999)}"]
            ]

            info_table = Table(info_table_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
            info_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('FONT', (1, 0), (1, 0), 'Helvetica-Bold', 11),
                ('BACKGROUND', (0, 0), (0, -1), self.colors['row_odd']),
                ('BACKGROUND', (2, 0), (2, -1), self.colors['row_odd']),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text_dark']),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 20))
            
            # Earnings Section
            earnings_title_style = ParagraphStyle(
                'EarningsTitle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=self.colors['primary'],
                alignment=0,
                spaceAfter=8
            )
            
            earnings_title = Paragraph("EARNINGS", earnings_title_style)
            elements.append(earnings_title)
            
            # Calculate earnings and deductions
            gross_pay = educator_data['monthly_salary'] / 2  # Bi-weekly pay
            federal_tax = gross_pay * 0.15
            state_tax = gross_pay * 0.05
            social_security = gross_pay * 0.062
            medicare = gross_pay * 0.0145
            retirement = gross_pay * 0.07
            health_insurance = 150.00
            total_deductions = federal_tax + state_tax + social_security + medicare + retirement + health_insurance
            net_pay = gross_pay - total_deductions
            
            earnings_data = [
                ["Description", "Hours", "Rate", "Current", "YTD"],
                ["Regular Pay", "80.00", f"${gross_pay/80:.2f}", self.format_currency(gross_pay), self.format_currency(gross_pay * 12)],
                ["", "", "", "", ""],
                ["Gross Pay", "", "", self.format_currency(gross_pay), self.format_currency(gross_pay * 12)]
            ]
            
            earnings_table = Table(earnings_data, colWidths=[2*inch, 0.8*inch, 1*inch, 1.2*inch, 1.2*inch])
            earnings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),
                ('LINEABOVE', (0, -1), (-1, -1), 1, self.colors['border']),
                ('GRID', (0, 0), (-1, -2), 0.5, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(earnings_table)
            elements.append(Spacer(1, 20))
            
            # Deductions Section
            deductions_title = Paragraph("DEDUCTIONS", earnings_title_style)
            elements.append(deductions_title)
            
            deductions_data = [
                ["Description", "Current", "YTD"],
                ["Federal Income Tax", self.format_currency(federal_tax), self.format_currency(federal_tax * 12)],
                ["State Income Tax", self.format_currency(state_tax), self.format_currency(state_tax * 12)],
                ["Social Security", self.format_currency(social_security), self.format_currency(social_security * 12)],
                ["Medicare", self.format_currency(medicare), self.format_currency(medicare * 12)],
                ["Retirement Plan", self.format_currency(retirement), self.format_currency(retirement * 12)],
                ["Health Insurance", self.format_currency(health_insurance), self.format_currency(health_insurance * 12)],
                ["", "", ""],
                ["Total Deductions", self.format_currency(total_deductions), self.format_currency(total_deductions * 12)]
            ]
            
            deductions_table = Table(deductions_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            deductions_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('LINEABOVE', (0, -1), (-1, -1), 2, self.colors['accent']),
                ('BACKGROUND', (0, -1), (-1, -1), self.colors['row_odd']),
                ('GRID', (0, 0), (-1, -2), 0.5, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(deductions_table)
            elements.append(Spacer(1, 20))
            
            # Net Pay Summary
            net_pay_data = [
                ["TOTAL NET PAY:", self.format_currency(net_pay)]
            ]
            
            net_pay_table = Table(net_pay_data, colWidths=[4*inch, 2*inch])
            net_pay_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['accent']),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['row_odd']),
                ('BOX', (0, 0), (-1, 0), 1, self.colors['border']),
                ('PADDING', (0, 0), (-1, 0), 12),
            ]))
            
            elements.append(net_pay_table)
            
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
                "CONFIDENTIAL PAYROLL DOCUMENT • FOR VERIFICATION PURPOSES ONLY • DIRECT DEPOSIT TO BANK ACCOUNT",
                footer_style
            )
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            logger.error(f"Failed to create pay stub: {e}")
            return None
    
    def save_educator(self, educator_data):
        """Save educator data to file."""
        try:
            with open(self.employees_file, 'a', encoding='utf-8') as f:
                line = (f"{educator_data['full_name']}|{educator_data['employee_id']}|"
                       f"{educator_data['job_title']}|{educator_data['school']['name']}|"
                       f"{educator_data['hire_date'].strftime('%Y-%m-%d')}|"
                       f"{educator_data['annual_salary']}|{datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(line)
            
            return True
        except Exception as e:
            logger.error(f"⚠️ Save error: {e}")
            return False
    
    def generate_document_set(self, quantity):
        """Generate a complete set of documents for educators."""
        print(f"\n⚡ Generating {quantity} EDUCATOR DOCUMENT SETS")
        print("=" * 70)
        print(f"🏫 School Type: {self.selected_school_type}")
        print(f"📚 Schools: {len(self.schools)} available")
        print("📄 Documents per set:")
        print("   1. Official Employment Letter")
        print("   2. School Employment Contract")
        print("   3. Recent Pay Stub")
        print("✅ All documents include:")
        print("   • Full Name • Job Title • School Name")
        print("   • Current Dates • Official Letterhead")
        print("=" * 70)
        
        start = time.time()
        success = 0
        
        for i in range(1, quantity + 1):
            try:
                educator_data = self.generate_educator_data()
                
                # Generate all three documents
                letter_file = self.create_employment_letter(educator_data)
                contract_file = self.create_employment_contract(educator_data)
                paystub_file = self.create_pay_stub(educator_data)

                if letter_file and contract_file and paystub_file:
                    self.save_educator(educator_data)
                    success += 1
                
                if i % 5 == 0 or i == quantity:
                    elapsed = time.time() - start
                    print(f"Progress: {i}/{quantity} ({(i/quantity*100):.1f}%) | Sets: {success}")
                    
            except Exception as e:
                logger.error(f"Error generating document set {i}: {e}")
        
        duration = time.time() - start
        
        print("\n" + "="*70)
        print("✅ DOCUMENT GENERATION COMPLETE")
        print("="*70)
        print(f"⏱️  Time: {duration:.1f}s")
        print(f"✅ Success: {success}/{quantity} document sets")
        print(f"📁 Folder: {self.documents_dir}/")
        print(f"📄 Educator list: {self.employees_file}")
        print(f"📋 Documents generated per educator:")
        print(f"   • Official Employment Letter")
        print(f"   • School Employment Contract")
        print(f"   • Recent Pay Stub")
        print("="*70)

def main():
    parser = argparse.ArgumentParser(description="Generate educator verification documents.")
    parser.add_argument("--teacher-name", help="Teacher name to use in generated documents", default=None)
    parser.add_argument("--school-name", help="School name to use in generated documents", default=None)
    parser.add_argument(
        "--school-type",
        help="Preselect school type: 1/elementary, 2/middle, or 3/high",
        default=None
    )
    args = parser.parse_args()

    print("\n" + "="*70)
    print("PROFESSIONAL EDUCATOR DOCUMENT GENERATOR - USA K-12 SCHOOLS")
    print("="*70)
    print("📄 Generates complete verification documents for educators")
    print("🏫 Supports Elementary, Middle, and High Schools")
    print("📋 Includes ALL required details:")
    print("   • Full Name • Job Title • School Name")
    print("   • Current Dates • Official School Letterhead")
    print("📁 Three documents per educator:")
    print("   1. Official Employment Letter")
    print("   2. School Employment Contract")
    print("   3. Recent Pay Stub")
    print("="*70)

    teacher_name = clean_name(args.teacher_name) if args.teacher_name else None
    school_name = clean_name(args.school_name) if args.school_name else None

    if not teacher_name:
        provided = input("What is the teacher's full name? (press Enter to generate one automatically): ").strip()
        teacher_name = clean_name(provided) if provided else None

    if not school_name:
        provided = input("What is the official school name? (press Enter to generate one automatically): ").strip()
        school_name = clean_name(provided) if provided else None

    generator = EducatorDocumentGenerator(
        custom_teacher_name=teacher_name,
        custom_school_name=school_name,
        preselected_school_type=normalize_school_type(args.school_type)
    )

    if generator.custom_teacher_name:
        print(f"🧑‍🏫 Using teacher name: {generator.custom_teacher_name}")
    else:
        print("🧑‍🏫 No teacher name provided. A realistic name will be generated.")

    if generator.custom_school_name:
        print(f"🏫 Using school name: {generator.custom_school_name}")
    else:
        print("🏫 No school name provided. A school will be generated for you.")
    if args.school_type:
        provided_type = normalize_school_type(args.school_type)
        if provided_type:
            print(f"🏫 Using provided school type: {provided_type.title()} School")
        else:
            print("❌ Invalid school type provided. Please use 1, 2, 3 or elementary/middle/high.")

    if not generator.select_school_type():
        return
    
    while True:
        print(f"\n{'='*60}")
        print(f"School Type: {generator.selected_school_type}")
        print(f"Available Schools: {len(generator.schools)}")
        print(f"Document Set includes:")
        print("   • Employment Letter • Employment Contract • Pay Stub")
        print(f"{'='*60}")
        
        user_input = input("\nNumber of educators to generate (0 to exit): ").strip()
        
        if user_input == "0":
            break
        
        try:
            quantity = int(user_input)
            if quantity < 1:
                print("❌ Enter a number greater than 0")
                continue
            
            generator.generate_document_set(quantity)
            
        except ValueError:
            print("❌ Enter a valid number")
            continue
    
    print("\n✅ FINISHED! All documents are ready for verification!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
