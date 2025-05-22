import requests
import sys
import uuid
from datetime import datetime
import time

class CybersecurityAITester:
    def __init__(self, base_url="https://70106ba4-0800-4fb1-89ef-077b4db4d7b7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                    return False, response.json() if response.text else {}
                except:
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
            
    def test_person_search(self, name):
        """Test person search API"""
        print(f"\n🔍 Testing Person Search API for '{name}'...")
        success, response = self.run_test(
            f"Person Search for '{name}'",
            "POST",
            "search/person",
            200,
            data={"name": name}
        )
        
        if not success:
            return False
        
        # Check if response has the expected structure
        if 'personal_info' not in response:
            print("❌ Failed - Response missing 'personal_info' section")
            return False
        
        # Check if personal_info has the expected fields
        personal_info = response['personal_info']
        expected_fields = ['name', 'summary']
        for field in expected_fields:
            if field not in personal_info:
                print(f"❌ Failed - 'personal_info' missing '{field}' field")
                return False
        
        # Check if the response has the expected sections
        expected_sections = [
            'personal_info',
            'social_profiles',
            'professional_info',
            'articles',
            'mentions'
        ]
        
        for section in expected_sections:
            if section in response:
                print(f"✅ Section '{section}' found in response")
            else:
                print(f"⚠️ Section '{section}' not found in response")
        
        # Check if personal_info has the expected subsections
        expected_subsections = [
            'possible_locations',
            'possible_occupations',
            'possible_education',
            'possible_social_media',
            'possible_emails',
            'possible_websites',
            'possible_phone_numbers'
        ]
        
        for subsection in expected_subsections:
            if subsection in personal_info:
                print(f"✅ Subsection '{subsection}' found in personal_info")
                if isinstance(personal_info[subsection], list) and len(personal_info[subsection]) > 0:
                    print(f"  - Contains {len(personal_info[subsection])} items")
            else:
                print(f"⚠️ Subsection '{subsection}' not found in personal_info")
        
        # Print a sample of the data
        print("\n📊 Sample of person search results:")
        print(f"Name: {personal_info.get('name', 'N/A')}")
        print(f"Summary: {personal_info.get('summary', 'N/A')[:200]}...")
        
        if 'possible_locations' in personal_info and personal_info['possible_locations']:
            print(f"Locations: {', '.join(personal_info['possible_locations'][:3])}")
        
        if 'possible_occupations' in personal_info and personal_info['possible_occupations']:
            print(f"Occupations: {', '.join(personal_info['possible_occupations'][:3])}")
        
        return True

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )

    def test_status_endpoint(self):
        """Test the status endpoint"""
        return self.run_test(
            "Status Endpoint",
            "GET",
            "status",
            200
        )

    def test_create_status_check(self):
        """Test creating a status check"""
        client_name = f"test_client_{uuid.uuid4().hex[:8]}"
        return self.run_test(
            "Create Status Check",
            "POST",
            "status",
            200,
            data={"client_name": client_name}
        )

    def test_get_status_checks(self):
        """Test getting status checks"""
        return self.run_test(
            "Get Status Checks",
            "GET",
            "status/checks",
            200
        )

    def test_get_datasets(self):
        """Test getting datasets"""
        return self.run_test(
            "Get Datasets",
            "GET",
            "datasets",
            200
        )

    def test_upload_dataset(self):
        """Test uploading a dataset"""
        # Create a simple test file
        test_file_path = "/tmp/test_dataset.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test dataset file for testing purposes.")
        
        # Prepare form data
        data = {
            "name": f"Test Dataset {uuid.uuid4().hex[:8]}",
            "description": "This is a test dataset for API testing"
        }
        
        files = {
            "file": ("test_dataset.txt", open(test_file_path, "rb"), "text/plain")
        }
        
        return self.run_test(
            "Upload Dataset",
            "POST",
            "dataset/upload",
            200,
            data=data,
            files=files
        )

    def test_web_search(self):
        """Test web search"""
        return self.run_test(
            "Web Search",
            "POST",
            "search/web",
            200,
            data={"query": "cybersecurity best practices"}
        )

    def test_person_search(self):
        """Test person search"""
        return self.run_test(
            "Person Search",
            "POST",
            "search/person",
            200,
            data={"name": "John Smith"}
        )

    def test_chat(self):
        """Test chat endpoint"""
        return self.run_test(
            "Chat",
            "POST",
            "chat",
            200,
            data={"message": "What are common cybersecurity threats?"}
        )

    def test_telegram_config(self):
        """Test Telegram configuration (with invalid token to avoid actual changes)"""
        return self.run_test(
            "Telegram Config",
            "POST",
            "config/telegram",
            200,
            data={"token": "invalid_token_for_testing_only"}
        )

    def test_openai_config(self):
        """Test OpenAI configuration (with invalid key to avoid actual changes)"""
        return self.run_test(
            "OpenAI Config",
            "POST",
            "config/openai",
            200,
            data={"api_key": "invalid_key_for_testing_only"}
        )

def main():
    # Setup
    tester = CybersecurityAITester()
    
    # Run tests
    tester.test_root_endpoint()
    status_success, status_data = tester.test_status_endpoint()
    
    if status_success:
        print(f"\nStatus Data: {status_data}")
    
    tester.test_create_status_check()
    tester.test_get_status_checks()
    tester.test_get_datasets()
    
    # Test dataset upload
    upload_success, upload_data = tester.test_upload_dataset()
    if upload_success:
        print(f"\nUploaded Dataset: {upload_data}")
        # Wait a moment for processing
        time.sleep(2)
        # Check datasets again to see the uploaded one
        tester.test_get_datasets()
    
    # Test search functionality
    web_search_success, web_search_data = tester.test_web_search()
    if web_search_success:
        print(f"\nWeb Search Results: {len(web_search_data.get('results', []))} items found")
    
    person_search_success, person_search_data = tester.test_person_search()
    if person_search_success:
        print(f"\nPerson Search Results for: {person_search_data.get('name', 'Unknown')}")
    
    # Test chat
    chat_success, chat_data = tester.test_chat()
    if chat_success:
        print(f"\nChat Response: {chat_data.get('response', 'No response')[:100]}...")
    
    # Test configuration endpoints
    tester.test_telegram_config()
    tester.test_openai_config()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())