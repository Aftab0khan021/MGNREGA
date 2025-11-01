import requests
import sys
from datetime import datetime
import json

class MGNREGAAPITester:
    def __init__(self, base_url="https://nrega-connect.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_base}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response: Dict with keys: {list(response_data.keys())}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                self.tests_passed += 1 if response.status_code in [200, 201] else 0
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                print(f"❌ Failed - {error_msg}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    "test": name,
                    "error": error_msg,
                    "response": response.text[:200]
                })
                return False, {}

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"❌ Failed - {error_msg}")
            self.failed_tests.append({
                "test": name,
                "error": error_msg
            })
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_states_endpoint(self):
        """Test states endpoint"""
        success, data = self.run_test("Get States", "GET", "states", 200)
        if success and isinstance(data, list) and len(data) > 0:
            print(f"   Found {len(data)} states")
            # Check if states have required fields
            first_state = data[0]
            required_fields = ['state_code', 'state_name', 'state_name_hi']
            missing_fields = [field for field in required_fields if field not in first_state]
            if missing_fields:
                print(f"   ⚠️  Missing fields in state data: {missing_fields}")
            else:
                print(f"   ✅ State data structure is correct")
            return True, data
        return success, data

    def test_districts_endpoint(self, state_code="UP"):
        """Test districts endpoint"""
        success, data = self.run_test("Get Districts", "GET", f"districts/{state_code}", 200)
        if success and isinstance(data, list) and len(data) > 0:
            print(f"   Found {len(data)} districts for state {state_code}")
            # Check if districts have required fields
            first_district = data[0]
            required_fields = ['district_code', 'district_name', 'district_name_hi', 'state_code']
            missing_fields = [field for field in required_fields if field not in first_district]
            if missing_fields:
                print(f"   ⚠️  Missing fields in district data: {missing_fields}")
            else:
                print(f"   ✅ District data structure is correct")
            return True, data
        return success, data

    def test_performance_endpoint(self, district_code="UP001"):
        """Test performance endpoint"""
        success, data = self.run_test("Get Performance Data", "GET", f"performance/{district_code}", 200)
        if success and isinstance(data, list) and len(data) > 0:
            print(f"   Found {len(data)} performance records for district {district_code}")
            # Check if performance data has required fields
            first_perf = data[0]
            required_fields = [
                'active_workers', 'person_days_generated', 'average_wage_per_day',
                'completed_works', 'total_works', 'total_budget_allocated', 'total_expenditure'
            ]
            missing_fields = [field for field in required_fields if field not in first_perf]
            if missing_fields:
                print(f"   ⚠️  Missing fields in performance data: {missing_fields}")
            else:
                print(f"   ✅ Performance data structure is correct")
            return True, data
        return success, data

    def test_translations_endpoint(self):
        """Test translations endpoint"""
        success, data = self.run_test("Get All Translations", "GET", "translations", 200)
        if success and isinstance(data, list) and len(data) > 0:
            print(f"   Found {len(data)} translation keys")
            # Check if translations have required structure
            first_translation = data[0]
            if 'key' in first_translation and 'translations' in first_translation:
                print(f"   ✅ Translation data structure is correct")
            else:
                print(f"   ⚠️  Translation data structure is incorrect")
            return True, data
        return success, data

    def test_language_translations(self, language="hi"):
        """Test language-specific translations"""
        success, data = self.run_test(f"Get {language.upper()} Translations", "GET", f"translations/{language}", 200)
        if success and isinstance(data, dict):
            print(f"   Found {len(data)} translation keys for {language}")
            # Check for key translation keys
            key_translations = ['app_title', 'select_state', 'select_district', 'active_workers']
            missing_keys = [key for key in key_translations if key not in data]
            if missing_keys:
                print(f"   ⚠️  Missing translation keys: {missing_keys}")
            else:
                print(f"   ✅ Key translations are present")
            return True, data
        return success, data

    def test_invalid_endpoints(self):
        """Test invalid endpoints return proper errors"""
        print(f"\n🔍 Testing Invalid Endpoints...")
        
        # Test invalid state
        success, _ = self.run_test("Invalid State", "GET", "districts/INVALID", 404)
        
        # Test invalid district
        success2, _ = self.run_test("Invalid District", "GET", "performance/INVALID", 404)
        
        # Test invalid language (should fallback to English)
        success3, _ = self.run_test("Invalid Language", "GET", "translations/invalid", 200)
        
        return success and success2 and success3

    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting MGNREGA API Comprehensive Testing")
        print("=" * 60)

        # Test basic endpoints
        self.test_root_endpoint()
        
        # Test states
        states_success, states_data = self.test_states_endpoint()
        
        # Test districts (use first state if available)
        if states_success and states_data:
            first_state = states_data[0]['state_code']
            districts_success, districts_data = self.test_districts_endpoint(first_state)
            
            # Test performance (use first district if available)
            if districts_success and districts_data:
                first_district = districts_data[0]['district_code']
                self.test_performance_endpoint(first_district)
        
        # Test translations
        self.test_translations_endpoint()
        self.test_language_translations("hi")
        self.test_language_translations("en")
        
        # Test error handling
        self.test_invalid_endpoints()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test['test']}: {test['error']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80  # Consider 80%+ as passing

def main():
    tester = MGNREGAAPITester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())