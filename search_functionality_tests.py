import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5001")

# Test user data (if needed for authenticated tests)
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "enock@gmail.com")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "enock")

@pytest.fixture
def driver():
    print("Setting up WebDriver...")
    # Initialize Chrome options
    chrome_options = Options()
    # Uncomment for headless mode in production
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # Set logging preferences
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    # Set up the ChromeDriver service
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("WebDriver setup complete")
    
    yield driver
    
    # Teardown
    print("Tearing down WebDriver...")
    driver.quit()

def navigate_to_home(driver):
    """Navigate to the home page where search functionality is available"""
    home_url = FRONTEND_BASE_URL
    print(f"Navigating to home page: {home_url}")
    driver.get(home_url)
    
    try:
        # Wait for the search bar to be visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']"))
        )
        print("Home page loaded with search bar")
        return True
    except Exception as e:
        print(f"Error loading home page: {str(e)}")
        driver.save_screenshot("home_page_error.png")
        return False

def test_empty_search(driver):
    """Test searching with an empty query"""
    print("Starting test_empty_search...")
    
    if not navigate_to_home(driver):
        pytest.skip("Could not navigate to home page")
    
    try:
        # Find the search form
        search_form = driver.find_element(By.TAG_NAME, "form")
        
        # Click the search button without entering a query
        search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_button.click()
        
        # Wait for results page to load
        time.sleep(2)
        
        # Take screenshot of results
        driver.save_screenshot("empty_search_results.png")
        
        # Check if we're on the search results page
        assert "search-results" in driver.current_url, "Should navigate to search results page"
        
        # Verify that an appropriate message is displayed for empty search
        message_elements = driver.find_elements(By.CSS_SELECTOR, ".text-center")
        
        empty_search_message_found = False
        for elem in message_elements:
            if "enter a search term" in elem.text.lower():
                empty_search_message_found = True
                break
        
        assert empty_search_message_found, "Should display message about empty search"
        
    except Exception as e:
        print(f"Error in test_empty_search: {str(e)}")
        driver.save_screenshot("empty_search_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

def test_no_results_search(driver):
    """Test searching for a term that returns no results"""
    print("Starting test_no_results_search...")
    
    if not navigate_to_home(driver):
        pytest.skip("Could not navigate to home page")
    
    try:
        # Find the search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
        
        # Enter a search term that likely won't return results
        nonsense_query = "xyznonexistentsupplement123456789"
        search_input.clear()
        search_input.send_keys(nonsense_query)
        
        # Submit the search form
        search_form = driver.find_element(By.TAG_NAME, "form")
        search_form.submit()
        
        # Wait for results page to load
        time.sleep(2)
        
        # Take screenshot of results
        driver.save_screenshot("no_results_search.png")
        
        # Check if we're on the search results page with the correct query
        assert "search-results" in driver.current_url, "Should navigate to search results page"
        assert f"q={nonsense_query}" in driver.current_url, "URL should contain the search query"
        
        # Verify that a "no results" message is displayed
        message_elements = driver.find_elements(By.CSS_SELECTOR, ".text-center")
        
        no_results_message_found = False
        for elem in message_elements:
            if "no supplements found" in elem.text.lower():
                no_results_message_found = True
                break
        
        assert no_results_message_found, "Should display 'no supplements found' message"
        
    except Exception as e:
        print(f"Error in test_no_results_search: {str(e)}")
        driver.save_screenshot("no_results_search_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

def test_exact_match_search(driver):
    """Test searching for a supplement by its exact name"""
    print("Starting test_exact_match_search...")
    
    if not navigate_to_home(driver):
        pytest.skip("Could not navigate to home page")
    
    # Test supplement to search for
    test_supplement = "Vitamin D"
    
    try:
        # Find the search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
        
        # Enter the exact supplement name
        search_input.clear()
        search_input.send_keys(test_supplement)
        
        # Submit the search form
        search_form = driver.find_element(By.TAG_NAME, "form")
        search_form.submit()
        
        # Wait for results page to load
        time.sleep(2)
        
        # Take screenshot of results
        driver.save_screenshot("exact_match_search.png")
        
        # Check if we're on the search results page with the correct query
        assert "search-results" in driver.current_url, "Should navigate to search results page"
        assert f"q={test_supplement.replace(' ', '+')}" in driver.current_url, "URL should contain the search query"
        
        # Verify that results are displayed and include our search term
        supplement_cards = driver.find_elements(By.CSS_SELECTOR, ".card, article, div[class*='hover:shadow']")
        
        assert len(supplement_cards) > 0, "Should display at least one result"
        
        # Check if at least one result contains our search term
        result_found = False
        for card in supplement_cards:
            if test_supplement.lower() in card.text.lower():
                result_found = True
                break
        
        assert result_found, f"Should display a result for '{test_supplement}'"
        
    except Exception as e:
        print(f"Error in test_exact_match_search: {str(e)}")
        driver.save_screenshot("exact_match_search_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

def test_partial_match_search(driver):
    """Test searching for supplements by partial name"""
    print("Starting test_partial_match_search...")
    
    if not navigate_to_home(driver):
        pytest.skip("Could not navigate to home page")
    
    # Test partial search term that should match multiple supplements
    test_partial_term = "vitamin"
    
    try:
        # Find the search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
        
        # Enter the partial search term
        search_input.clear()
        search_input.send_keys(test_partial_term)
        
        # Submit the search form
        search_form = driver.find_element(By.TAG_NAME, "form")
        search_form.submit()
        
        # Wait for results page to load
        time.sleep(2)
        
        # Take screenshot of results
        driver.save_screenshot("partial_match_search.png")
        
        # Check if we're on the search results page with the correct query
        assert "search-results" in driver.current_url, "Should navigate to search results page"
        assert f"q={test_partial_term}" in driver.current_url, "URL should contain the search query"
        
        # Verify that multiple results are displayed
        supplement_cards = driver.find_elements(By.CSS_SELECTOR, ".card, article, div[class*='hover:shadow']")
        
        assert len(supplement_cards) > 1, "Should display multiple results for a partial match"
        
        # Print the number of results found
        print(f"Found {len(supplement_cards)} results for partial search term '{test_partial_term}'")
        
        # Check if all results contain our search term (case insensitive)
        for i, card in enumerate(supplement_cards):
            print(f"Result {i+1} text: {card.text[:50]}...")
            assert test_partial_term.lower() in card.text.lower(), f"Result {i+1} should contain the search term"
        
    except Exception as e:
        print(f"Error in test_partial_match_search: {str(e)}")
        driver.save_screenshot("partial_match_search_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

def test_autocomplete_functionality(driver):
    """Test the autocomplete functionality of the search bar"""
    print("Starting test_autocomplete_functionality...")
    
    if not navigate_to_home(driver):
        pytest.skip("Could not navigate to home page")
    
    # Test term that should trigger autocomplete
    test_term = "vitamin"
    
    try:
        # Find the search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
        
        # Enter the partial search term
        search_input.clear()
        search_input.send_keys(test_term)
        
        # Wait for autocomplete suggestions to appear
        time.sleep(2)
        
        # Take screenshot of autocomplete
        driver.save_screenshot("autocomplete_suggestions.png")
        
        # Check if autocomplete suggestions are displayed
        autocomplete_elements = driver.find_elements(By.CSS_SELECTOR, "ul li, .autocomplete, [role='listbox'] [role='option']")
        
        assert len(autocomplete_elements) > 0, "Should display autocomplete suggestions"
        
        # Print the suggestions found
        print(f"Found {len(autocomplete_elements)} autocomplete suggestions for '{test_term}'")
        for i, suggestion in enumerate(autocomplete_elements):
            print(f"Suggestion {i+1}: {suggestion.text}")
            
        # Test clicking on the first autocomplete suggestion
        if len(autocomplete_elements) > 0:
            autocomplete_elements[0].click()
            
            # Wait for navigation to supplement detail page
            time.sleep(2)
            
            # Take screenshot of the result
            driver.save_screenshot("autocomplete_navigation.png")
            
            # Verify we've navigated to a supplement detail page
            assert "supplements/" in driver.current_url, "Should navigate to a supplement detail page after clicking suggestion"
            
    except Exception as e:
        print(f"Error in test_autocomplete_functionality: {str(e)}")
        driver.save_screenshot("autocomplete_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

def test_search_keyboard_navigation(driver):
    """Test keyboard navigation in search autocomplete"""
    print("Starting test_search_keyboard_navigation...")
    
    if not navigate_to_home(driver):
        pytest.skip("Could not navigate to home page")
    
    # Test term that should trigger autocomplete
    test_term = "vitamin"
    
    try:
        # Find the search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
        
        # Enter the partial search term
        search_input.clear()
        search_input.send_keys(test_term)
        
        # Wait for autocomplete suggestions to appear
        time.sleep(2)
        
        # Check if autocomplete suggestions are displayed
        autocomplete_elements = driver.find_elements(By.CSS_SELECTOR, "ul li, .autocomplete, [role='listbox'] [role='option']")
        
        if len(autocomplete_elements) > 1:
            # Press down arrow to select the first item
            search_input.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)
            driver.save_screenshot("keyboard_nav_first_item.png")
            
            # Press down arrow again to select the second item
            search_input.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)
            driver.save_screenshot("keyboard_nav_second_item.png")
            
            # Press Enter to select the highlighted item
            search_input.send_keys(Keys.ENTER)
            
            # Wait for navigation to supplement detail page
            time.sleep(2)
            
            # Take screenshot of the result
            driver.save_screenshot("keyboard_nav_result.png")
            
            # Verify we've navigated to a supplement detail page
            assert "supplements/" in driver.current_url, "Should navigate to a supplement detail page after using keyboard navigation"
        else:
            print("Not enough autocomplete suggestions to test keyboard navigation")
            pytest.skip("Not enough autocomplete suggestions to test keyboard navigation")
            
    except Exception as e:
        print(f"Error in test_search_keyboard_navigation: {str(e)}")
        driver.save_screenshot("keyboard_nav_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

if __name__ == "__main__":
    print("Running Selenium tests for search functionality")
    print(f"Frontend URL: {FRONTEND_BASE_URL}")
    print(f"API URL: {API_BASE_URL}") 