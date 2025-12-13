"""
SheerID Database Extractor - U.S. K-12 SCHOOLS ONLY
Language: Python
- Author: Adeebaabkhan
- Date: 2025-11-25
- Extracts ONLY K-12 schools in the United States
- English-only filtering
- NO duplicates - removes duplicate institutions
- NO SSO testing - extracts everything instantly
- High concurrency with 200 workers
- Saves K-12 schools to sheerid_[country].json
- K-12 Schools ONLY - NO DUPLICATES
"""

import requests
import json
import time
import os
import string
import re
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass
from typing import List, Dict, Set, Optional

@dataclass
class InstitutionStats:
    total_requests: int = 0
    successful_requests: int = 0
    total_found: int = 0
    institutions_saved: int = 0
    duplicates_removed: int = 0
    filtered_out: int = 0
    rate_limited: int = 0
    errors: int = 0
    max_offset_reached: int = 0

class FastSchoolsUniversitiesExtractor:
    def __init__(self, country: str = "US"):
        self.country = country.upper()
        self.institutions = {}  # Using dict to prevent duplicates by ID
        self.processed_ids = set()  # Track processed institution IDs
        self.lock = threading.Lock()
        self.stats = InstitutionStats()
        
        # API Configuration
        self.base_url = "https://services.sheerid.com/rest/0.5/organization"
        
        # Output file
        self.output_filename = f"sheerid_{self.country.lower()}.json"
        
        # ONLY ALLOW K-12 SCHOOLS
        self.allowed_types = {
            'K12', 'PRIMARY', 'SECONDARY', 'MIDDLE_SCHOOL', 'HIGH_SCHOOL',
            'ELEMENTARY', 'SCHOOL'
        }

        self.excluded_types = {
            'UNIVERSITY', 'COLLEGE', 'HIGHER_EDUCATION', 'COMMUNITY_COLLEGE',
            'TECHNICAL_COLLEGE', 'VOCATIONAL_SCHOOL', 'GRADUATE_SCHOOL',
            'MEDICAL_SCHOOL', 'LAW_SCHOOL', 'BUSINESS_SCHOOL', 'POST_SECONDARY',
            'GOVERNMENT', 'MILITARY', 'CORPORATION', 'NON_PROFIT', 'HEALTHCARE',
            'LIBRARY', 'OTHER', 'UNKNOWN'
        }
        
        self._load_existing_data()

    def _load_existing_data(self):
        """Delete old files and start fresh"""
        if os.path.exists(self.output_filename):
            try:
                os.remove(self.output_filename)
                print(f"🗑️ Deleted old file: {self.output_filename}")
            except Exception as e:
                print(f"⚠️ Could not delete {self.output_filename}: {e}")

    def is_english_only(self, text: str) -> bool:
        """STRICT English-only check"""
        if not text or not isinstance(text, str):
            return False
        
        cleaned = re.sub(r'[^\w\s\-\.\',\(\)&]', '', text)
        cleaned = cleaned.strip()
        
        if not cleaned:
            return False
        
        try:
            cleaned.encode('ascii')
        except UnicodeEncodeError:
            return False
        
        if any(ord(char) > 127 for char in cleaned):
            return False
            
        devanagari_pattern = re.compile(r'[\u0900-\u097F]')
        if devanagari_pattern.search(text):
            return False
            
        non_english_patterns = [
            r'[\u4E00-\u9FFF]',
            r'[\u0600-\u06FF]',
            r'[\u0400-\u04FF]',
        ]
        
        for pattern in non_english_patterns:
            if re.compile(pattern).search(text):
                return False
        
        return True

    def is_k12_school(self, institution: Dict) -> bool:
        """STRICT validation - ONLY K-12 schools"""
        name = institution.get('name', '').strip()

        if not name or len(name) < 2:
            return False

        if not self.is_english_only(name):
            return False

        inst_type = institution.get('type', '').upper()
        org_type = institution.get('organizationType', '').upper()

        if inst_type in self.excluded_types or org_type in self.excluded_types:
            return False

        if inst_type in self.allowed_types or org_type in self.allowed_types:
            return True

        return False

    def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        ]
        
        return {
            'User-Agent': user_agents[self.stats.total_requests % len(user_agents)],
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def make_api_request(self, query: str, offset: int = 0, limit: int = 100) -> Optional[List[Dict]]:
        """API request with timeout handling"""
        params = {
            'country': self.country,
            'name': query,
            'offset': offset,
            'limit': limit,
            'locale': 'en-us',
            '_': int(time.time() * 1000)
        }
        
        try:
            with self.lock:
                self.stats.total_requests += 1
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    with self.lock:
                        self.stats.successful_requests += 1
                    return data if isinstance(data, list) else data.get('data', [])
                except:
                    return []
            elif response.status_code == 429:
                with self.lock:
                    self.stats.rate_limited += 1
                time.sleep(0.5)
                return []
            else:
                return []
                
        except requests.exceptions.Timeout:
            with self.lock:
                self.stats.errors += 1
            return []
        except Exception:
            with self.lock:
                self.stats.errors += 1
            return []

    def process_institutions(self, institutions: List[Dict], query: str) -> int:
        """Process institutions - NO DUPLICATES"""
        if not institutions:
            return 0
        
        new_added = 0
        
        for inst in institutions:
            if not isinstance(inst, dict) or 'id' not in inst:
                continue
            
            inst_id = str(inst['id'])
            
            with self.lock:
                self.stats.total_found += 1
            
            # ✅ CHECK FOR DUPLICATES - Skip if already processed
            if inst_id in self.processed_ids:
                with self.lock:
                    self.stats.duplicates_removed += 1
                continue
            
            normalized = {
                'id': int(inst['id']) if str(inst['id']).isdigit() else inst['id'],
                'name': inst.get('name', '').strip(),
                'country': inst.get('country', self.country),
                'query_found': query,
                'extraction_date': datetime.now(timezone.utc).strftime('%Y-%m-%d')
            }
            
            for field in ['type', 'organizationType', 'city', 'state', 'website', 'domain']:
                if field in inst and inst[field]:
                    normalized[field] = str(inst[field]).strip()
            
            if not normalized['name']:
                continue
            
            if not self.is_k12_school(normalized):
                with self.lock:
                    self.stats.filtered_out += 1
                continue
            
            # ✅ SAVE INSTITUTION - No duplicates
            self.institutions[inst_id] = normalized  # Use ID as key to prevent duplicates
            self.processed_ids.add(inst_id)
            new_added += 1
            
            with self.lock:
                self.stats.institutions_saved += 1
        
        return new_added

    def generate_queries_for_country(self) -> List[str]:
        """Generate optimized queries"""
        queries = []
        
        # Single letters
        queries.extend(string.ascii_lowercase[:10])

        # Double letters
        for letter1 in string.ascii_lowercase[:5]:
            for letter2 in string.ascii_lowercase[:3]:
                queries.append(f"{letter1}{letter2}")

        # School keywords focused on K-12
        school_keywords = [
            'school', 'academy', 'high school', 'middle', 'elementary',
            'secondary', 'primary', 'prep'
        ]
        queries.extend(school_keywords)
        
        # Empty query
        queries.append('')
        
        # Country-specific terms (focused on U.S. K-12 schools)
        country_schools = {
            'US': ['high school', 'elementary school', 'middle school',
                   'public school', 'charter school', 'prep school']
        }

        if self.country in country_schools:
            queries.extend(country_schools[self.country])
        
        unique_queries = list(set(queries))
        unique_queries.sort(key=len)
        
        print(f"📋 Generated {len(unique_queries)} optimized queries")
        
        return unique_queries

    def worker_task(self, query: str) -> int:
        """Worker task - NO DUPLICATES"""
        total_found = 0
        offset = 0
        consecutive_empty = 0
        max_consecutive_empty = 2
        max_offset = 1000
        
        if len(query) > 10:
            return 0
        
        while consecutive_empty < max_consecutive_empty and offset < max_offset:
            institutions = self.make_api_request(query, offset, 100)
            
            if not institutions:
                consecutive_empty += 1
                offset += 100
                continue
            
            found = self.process_institutions(institutions, query)
            total_found += found
            
            if len(institutions) < 50:
                consecutive_empty += 1
            else:
                consecutive_empty = 0
            
            offset += 100
            time.sleep(0.1)
        
        return total_found

    def save_results(self) -> bool:
        """Save results - NO DUPLICATES"""
        try:
            if not self.institutions:
                print("❌ No institutions to save")
                return False
                
            # Convert dict values to list (already unique by ID)
            all_institutions = list(self.institutions.values())
            all_institutions_sorted = sorted(all_institutions,
                                           key=lambda x: str(x['name']).lower())
            
            with open(self.output_filename, 'w', encoding='utf-8') as f:
                json.dump(all_institutions_sorted, f, indent=2, ensure_ascii=True)
            
            print(f"\n💾 Saved {len(all_institutions_sorted)} UNIQUE schools/universities to: {self.output_filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False

    def print_statistics(self):
        """Print statistics"""
        print(f"\n📊 EXTRACTION STATISTICS - {self.country}")
        print(f"=" * 50)
        print(f"📞 Total API Requests: {self.stats.total_requests:,}")
        print(f"✅ Successful Requests: {self.stats.successful_requests:,}")
        print(f"🔍 Total Found: {self.stats.total_found:,}")
        print(f"🏫 Unique K-12 Schools: {self.stats.institutions_saved:,}")
        print(f"🚫 Filtered Out: {self.stats.filtered_out:,}")
        print(f"🔄 Duplicates Removed: {self.stats.duplicates_removed:,}")
        print(f"⚠️ Rate Limited: {self.stats.rate_limited:,}")
        print(f"❌ Errors: {self.stats.errors:,}")
        
        if self.institutions:
            print(f"\n🎯 SAMPLE UNIQUE K-12 INSTITUTIONS:")
            sample = list(self.institutions.values())[:10]
            for i, inst in enumerate(sample, 1):
                inst_type = inst.get('type', 'N/A')
                print(f"   {i:2}. {inst['name'][:40]} [{inst_type}]")

    def run_extraction(self, max_workers: int = 50):
        """MAIN EXTRACTION - NO DUPLICATES"""
        print(f"\n🚀 STARTING {self.country} K-12 SCHOOL EXTRACTION")
        print(f"👤 Author: Adeebaabkhan")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"🎯 Focus: K-12 SCHOOLS ONLY")
        print(f"🔄 Workers: {max_workers}")
        print(f"🚫 DUPLICATES: REMOVED")
        print(f"💾 Output: {self.output_filename}")
        
        queries = self.generate_queries_for_country()
        
        start_time = time.time()
        last_save = start_time
        
        print(f"\n⏱️ STARTING K-12 EXTRACTION...")
        print(f"🔤 Processing {len(queries)} queries with {max_workers} workers")
        
        completed_tasks = 0
        total_tasks = len(queries)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_query = {
                executor.submit(self.worker_task, query): query 
                for query in queries
            }
            
            for future in as_completed(future_to_query):
                completed_tasks += 1
                query = future_to_query[future]
                
                try:
                    found = future.result()
                    status = "✅" if found > 0 else "➖"
                except Exception as e:
                    found = 0
                    status = "❌"
                
                elapsed = time.time() - start_time
                progress = (completed_tasks / total_tasks) * 100
                current_count = self.stats.institutions_saved
                
                print(f"\r{status} {completed_tasks:3d}/{total_tasks} | 🏫 {current_count:4d} | ⏱️ {elapsed:3.0f}s | 📈 {progress:5.1f}% | 🔤 '{query}'", 
                      end='', flush=True)
                
                if time.time() - last_save > 20:
                    self.save_results()
                    last_save = time.time()
        
        self.save_results()
        self.print_statistics()
        
        elapsed = time.time() - start_time
        total_institutions = self.stats.institutions_saved
        print(f"\n🎉 EXTRACTION COMPLETED in {elapsed:.1f} seconds!")
        print(f"📊 Total UNIQUE K-12 SCHOOLS: {total_institutions:,}")
        if elapsed > 0:
            print(f"🚀 Speed: {(total_institutions / elapsed * 60):.0f}/minute")
        print(f"💾 Saved to: {self.output_filename}")

def get_country_selection():
    """Interactive country selection - U.S. only for K-12 extraction"""
    countries = {
        '1': ('US', 'United States')
    }

    print("\n🌍 SELECT COUNTRY FOR K-12 SCHOOL EXTRACTION")
    print("🏫 Extracts ONLY K-12 schools")
    print("🎓 Includes: Elementary, Middle, and High Schools")
    print("🚫 DUPLICATES: REMOVED")
    print("=" * 50)
    
    # Display in columns
    keys = sorted(countries.keys(), key=int)
    for i in range(0, len(keys), 3):
        line = ""
        for j in range(3):
            if i + j < len(keys):
                key = keys[i + j]
                code, name = countries[key]
                line += f"{key:>2}. {name:<18}"
        print(line)
    
    print("=" * 50)
    
    while True:
        try:
            choice = input(f"Enter country number (1-{len(countries)}): ").strip()
            
            if choice in countries:
                country_code, country_name = countries[choice]
                print(f"\n✅ Selected: {country_name} ({country_code})")
                print(f"🏫 Will extract ONLY K-12 schools")
                print(f"🚫 DUPLICATES will be REMOVED")
                
                confirm = input(f"Start extraction? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return country_code
                else:
                    print("Selection cancelled.\n")
                    continue
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(countries)}.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            exit(0)

def main():
    print(f"🚀 SheerID K-12 School Extractor")
    print(f"👤 Author: Adeebaabkhan")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"🏫 Extracts ONLY K-12 schools")
    print(f"🚫 DUPLICATES: REMOVED")

    country = get_country_selection()
    
    print(f"\n⚙️ EXTRACTION SETUP")
    print(f"=" * 30)
    
    workers = 50
    print(f"🔄 Workers: {workers}")
    
    print(f"\n🚀 STARTING EXTRACTION...")
    print(f"🌍 Country: {country}")
    print(f"🏫 Target: K-12 SCHOOLS ONLY")
    print(f"🚫 DUPLICATES: REMOVED")
    print(f"💾 Output: sheerid_{country.lower()}.json")
    
    for i in range(3, 0, -1):
        print(f"   Starting in {i}...", end='\r')
        time.sleep(1)
    
    print("   Starting NOW...")
    
    try:
        extractor = FastSchoolsUniversitiesExtractor(country)
        extractor.run_extraction(workers)
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Interrupted by user!")
        if 'extractor' in locals():
            extractor.save_results()
            print(f"💾 Progress saved!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if 'extractor' in locals():
            extractor.save_results()

if __name__ == '__main__':
    main()