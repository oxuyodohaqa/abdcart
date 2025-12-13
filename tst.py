#!/usr/bin/env python3
"""
PROFESSIONAL EDUCATOR VERIFICATION DOCUMENT GENERATOR - USA K-12 SCHOOLS
✅ EMPLOYMENT LETTER: Official school-issued employment verification
✅ ID BADGE: Professional school staff identification
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
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from faker import Faker
import qrcode
import random
import json
from datetime import datetime, timedelta
from io import BytesIO
import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
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
        'job_titles': ['Elementary Teacher', 'Grade Level Teacher', 'Special Education Teacher', 
                      'Reading Specialist', 'Math Specialist', 'Elementary School Principal',
                      'Assistant Principal', 'School Counselor', 'Librarian']
    },
    'MIDDLE': {
        'grades': ['6th', '7th', '8th'],
        'subjects': ['English Language Arts', 'Mathematics', 'Science', 'Social Studies', 
                    'Foreign Language', 'Art', 'Music', 'Physical Education', 'Technology'],
        'job_titles': ['Middle School Teacher', 'Subject Teacher', 'Special Education Teacher',
                      'Department Chair', 'Middle School Principal', 'Assistant Principal',
                      'School Counselor', 'Athletic Director']
    },
    'HIGH': {
        'grades': ['9th', '10th', '11th', '12th'],
        'subjects': ['English', 'Mathematics', 'Science', 'Social Studies', 'Foreign Language',
                    'Art', 'Music', 'Physical Education', 'Technology', 'Career Education'],
        'job_titles': ['High School Teacher', 'Subject Teacher', 'Department Chair', 
                      'Special Education Teacher', 'High School Principal', 'Assistant Principal',
                      'School Counselor', 'Athletic Director', 'Dean of Students']
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

class EducatorDocumentGenerator:
    def __init__(self):
        self.documents_dir = "educator_documents"
        self.employees_file = "educators.txt"
        self.selected_school_type = None
        self.schools = []
        
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
            print("✅ ID BADGE: Professional staff identification")
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
        
        while True:
            choice = input("\nSelect school type (1-3): ").strip()
            if choice == '1':
                self.selected_school_type = 'ELEMENTARY'
                break
            elif choice == '2':
                self.selected_school_type = 'MIDDLE'
                break
            elif choice == '3':
                self.selected_school_type = 'HIGH'
                break
            else:
                print("❌ Please enter 1, 2, or 3")
        
        self.schools = self.load_schools()
        print(f"✅ Selected: {self.selected_school_type} School")
        print(f"📚 Schools available: {len(self.schools)}")
        
        return True
    
    def generate_educator_data(self):
        """Generate educator data with all required fields."""
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        full_name = clean_name(f"{first_name} {last_name}")
        
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
                spaceAfter=10
            )
            
            header = Paragraph(school['name'], header_style)
            elements.append(header)
            
            # School Address
            address_style = ParagraphStyle(
                'AddressStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=0,
                spaceAfter=20
            )
            
            address = Paragraph(f"{school['address']}<br/>{school['district']}<br/>Phone: {school['phone']}", address_style)
            elements.append(address)
            
            elements.append(Spacer(1, 30))
            
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
            
            subject = Paragraph("EMPLOYMENT VERIFICATION LETTER", subject_style)
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
            is employed by <b>{school['name']}</b> as a <b>{educator_data['job_title']}</b>.<br/><br/>
            
            {educator_data['full_name']} began employment with our school on 
            <b>{educator_data['hire_date'].strftime(USA_CONFIG['date_format'])}</b> and is currently employed 
            in a full-time capacity.<br/><br/>
            
            In their role as {educator_data['job_title']}, they are responsible for {educator_data['subject_area']} 
            instruction and related educational duties.<br/><br/>
            
            This individual is a valued member of our educational team and is in good standing with our institution.<br/><br/>
            
            This verification is provided at the request of the employee for personal purposes.<br/><br/>
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
            
            signature = Paragraph(
                f"Sincerely,<br/><br/><br/>"
                f"{school['principal']}<br/>"
                f"Principal<br/>"
                f"{school['name']}<br/>"
                f"Phone: {school['phone']}<br/>"
                f"Email: {school['email']}",
                sig_style
            )
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
    
    def create_id_badge(self, educator_data):
        """Create professional school ID badge."""
        school = educator_data['school']
        employee_id = educator_data['employee_id']
        
        filename = f"ID_BADGE_{employee_id}.pdf"
        filepath = os.path.join(self.documents_dir, filename)
        
        try:
            c = canvas.Canvas(filepath, pagesize=(3.375*inch, 2.125*inch))  # Standard ID card size
            
            # Background
            c.setFillColor(self.colors['primary'])
            c.rect(0, 0, 3.375*inch, 0.5*inch, fill=1, stroke=0)
            
            # School Name
            c.setFillColor(self.colors['white'])
            c.setFont("Helvetica-Bold", 10)
            c.drawString(0.2*inch, 2.0*inch, school['name'][:30])
            
            # Employee Photo Area
            c.setFillColor(self.colors['border'])
            c.rect(0.2*inch, 0.7*inch, 1*inch, 1.2*inch, fill=1, stroke=1)
            c.setFillColor(self.colors['text_light'])
            c.setFont("Helvetica", 8)
            c.drawString(0.3*inch, 1.3*inch, "PHOTO")
            
            # Employee Info
            c.setFillColor(self.colors['text_dark'])
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1.3*inch, 1.7*inch, educator_data['full_name'])
            
            c.setFont("Helvetica", 9)
            c.drawString(1.3*inch, 1.5*inch, f"Title: {educator_data['job_title']}")
            c.drawString(1.3*inch, 1.3*inch, f"ID: {educator_data['employee_id']}")
            c.drawString(1.3*inch, 1.1*inch, f"Dept: Education")
            
            # Issue Date
            c.setFont("Helvetica", 7)
            c.drawString(1.3*inch, 0.9*inch, f"Issued: {datetime.now().strftime('%m/%d/%Y')}")
            
            # Footer
            c.setFillColor(self.colors['text_light'])
            c.setFont("Helvetica-Oblique", 6)
            c.drawString(0.2*inch, 0.2*inch, "OFFICIAL SCHOOL STAFF IDENTIFICATION")
            
            # Border
            c.setStrokeColor(self.colors['border'])
            c.setLineWidth(1)
            c.rect(0.1*inch, 0.1*inch, 3.175*inch, 1.925*inch, fill=0, stroke=1)
            
            c.save()
            return filename
            
        except Exception as e:
            logger.error(f"Failed to create ID badge: {e}")
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
        print("   2. Professional ID Badge")
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
                id_file = self.create_id_badge(educator_data)
                paystub_file = self.create_pay_stub(educator_data)
                
                if letter_file and id_file and paystub_file:
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
        print(f"   • Professional ID Badge")
        print(f"   • Recent Pay Stub")
        print("="*70)

def main():
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
    print("   2. Professional ID Badge")
    print("   3. Recent Pay Stub")
    print("="*70)
    
    generator = EducatorDocumentGenerator()
    
    if not generator.select_school_type():
        return
    
    while True:
        print(f"\n{'='*60}")
        print(f"School Type: {generator.selected_school_type}")
        print(f"Available Schools: {len(generator.schools)}")
        print(f"Document Set includes:")
        print("   • Employment Letter • ID Badge • Pay Stub")
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