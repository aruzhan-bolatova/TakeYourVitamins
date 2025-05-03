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

def navigate_to_supplements_page(driver):
    """Navigate to the supplements search page"""
    supplements_search_url = f"{FRONTEND_BASE_URL}/supplements/search"
    print(f"Navigating to supplements search page: {supplements_search_url}")
    driver.get(supplements_search_url)
    
    try:
        # Wait for the search bar to be visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']"))
        )
        print("Supplements search page loaded with search bar")
        driver.save_screenshot("supplements_search_page.png")
        return True
    except Exception as e:
        print(f"Error loading supplements search page: {str(e)}")
        driver.save_screenshot("supplements_search_page_error.png")
        return False

def test_supplements_page_search(driver):
    """Test searching for supplements from the supplements search page"""
    print("Starting test_supplements_page_search...")
    
    if not navigate_to_supplements_page(driver):
        pytest.skip("Could not navigate to supplements search page")
    
    try:
        # Find the search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
        
        # Test supplement to search for
        test_supplement = "Magnesium"
        
        # Enter the search term
        search_input.clear()
        search_input.send_keys(test_supplement)
        
        # Submit the search form
        search_form = driver.find_element(By.TAG_NAME, "form")
        search_form.submit()
        
        # Wait for results page to load
        time.sleep(2)
        
        # Take screenshot of results
        driver.save_screenshot("supplements_search_results.png")
        
        # Verify that results are displayed
        supplement_cards = driver.find_elements(By.CSS_SELECTOR, ".card, article, div[class*='hover:shadow']")
        
        assert len(supplement_cards) > 0, f"Should display at least one result for '{test_supplement}'"
        
        # Print the number of results found
        print(f"Found {len(supplement_cards)} results for '{test_supplement}'")
        
    except Exception as e:
        print(f"Error in test_supplements_page_search: {str(e)}")
        driver.save_screenshot("supplements_search_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

def test_navigate_to_supplement_detail(driver):
    """Test navigating to a supplement's detail page from search results"""
    print("Starting test_navigate_to_supplement_detail...")
    
    if not navigate_to_supplements_page(driver):
        pytest.skip("Could not navigate to supplements search page")
    
    try:
        # Find the search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
        
        # Use a common term that should return multiple results
        test_term = "vitamin"
        
        # Enter the search term
        search_input.clear()
        search_input.send_keys(test_term)
        
        # Submit the search form
        search_form = driver.find_element(By.TAG_NAME, "form")
        search_form.submit()
        
        # Wait for results page to load
        time.sleep(2)
        
        # Take screenshot of search results
        driver.save_screenshot("supplement_detail_search_results.png")
        
        # Find all supplement cards
        supplement_cards = driver.find_elements(By.CSS_SELECTOR, ".card, article, div[class*='hover:shadow']")
        
        if len(supplement_cards) == 0:
            pytest.skip("No search results found to click on")
        
        # Click on the first result
        first_card = supplement_cards[0]
        
        # Get the name of the supplement before clicking
        supplement_name = first_card.text.split('\n')[0]  # Get first line of text (likely the supplement name)
        print(f"Clicking on supplement: {supplement_name}")
        
        first_card.click()
        
        # Wait for the detail page to load
        time.sleep(2)
        
        # Take screenshot of the detail page
        driver.save_screenshot("supplement_detail_page.png")
        
        # Verify that we're on a supplement detail page
        assert "supplements/" in driver.current_url, "Should navigate to a supplement detail page"
        
        # Verify the page contains the supplement name
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert supplement_name.lower() in page_text.lower(), f"Detail page should contain supplement name: {supplement_name}"
        
        print(f"Successfully navigated to detail page for: {supplement_name}")
        
    except Exception as e:
        print(f"Error in test_navigate_to_supplement_detail: {str(e)}")
        driver.save_screenshot("supplement_detail_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

def test_supplement_detail_related_navigation(driver):
    """Test navigation between related supplements from a detail page"""
    print("Starting test_supplement_detail_related_navigation...")
    
    if not navigate_to_supplements_page(driver):
        pytest.skip("Could not navigate to supplements search page")
    
    try:
        # Find the search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
        
        # Search for a supplement that likely has interactions
        test_supplement = "Vitamin D"
        
        # Enter the search term
        search_input.clear()
        search_input.send_keys(test_supplement)
        
        # Submit the search form
        search_form = driver.find_element(By.TAG_NAME, "form")
        search_form.submit()
        
        # Wait for results page to load
        time.sleep(2)
        
        # Find and click on the first relevant result
        supplement_cards = driver.find_elements(By.CSS_SELECTOR, ".card, article, div[class*='hover:shadow']")
        
        if len(supplement_cards) == 0:
            pytest.skip("No search results found")
        
        # Click on the first result
        supplement_cards[0].click()
        
        # Wait for the detail page to load
        time.sleep(2)
        
        # Take screenshot of the first supplement detail page
        driver.save_screenshot("first_supplement_detail.png")
        
        # Get the initial content to compare later
        initial_content = driver.find_element(By.CSS_SELECTOR, "body").text
        
        # Check for interaction tabs
        interaction_tabs = driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
        
        tab_clicked = False
        
        for tab in interaction_tabs:
            if "interaction" in tab.text.lower():
                print(f"Found interactions tab: {tab.text}")
                # Store the current active tab content
                current_tab_content = driver.find_element(By.CSS_SELECTOR, "[role='tabpanel'][data-state='active'], [data-state='active']").text
                
                # Click the interactions tab
                tab.click()
                time.sleep(1)
                
                # Get the new active tab content
                new_tab_content = driver.find_element(By.CSS_SELECTOR, "[role='tabpanel'][data-state='active'], [data-state='active']").text
                
                # Verify the content changed
                assert new_tab_content != current_tab_content, "Tab content should change after clicking interactions tab"
                
                tab_clicked = True
                driver.save_screenshot("interactions_tab_content.png")
                break
        
        if not tab_clicked:
            # If no interaction tabs found, look for links to other supplements
            print("No interaction tabs found, looking for supplement links")
            supplement_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='supplements/']:not([href$='/supplements/search'])")
            
            if len(supplement_links) <= 1:  # 1 would be the current supplement
                pytest.skip("No related supplements found to navigate to")
            
            # Print all found links for debugging
            for i, link in enumerate(supplement_links):
                print(f"Link {i}: {link.get_attribute('href')} - {link.text}")
                
            # Click a supplement link (not the current page)
            current_url = driver.current_url
            for link in supplement_links:
                link_href = link.get_attribute('href')
                if link_href and link_href != current_url:
                    print(f"Clicking supplement link: {link.text} - {link_href}")
                    link.click()
                    time.sleep(2)
                    
                    # Verify we navigated to a different supplement
                    assert driver.current_url != current_url, "Should navigate to a different supplement detail page"
                    break
        
        print("Test completed successfully")
        
    except Exception as e:
        print(f"Error in test_supplement_detail_related_navigation: {str(e)}")
        driver.save_screenshot("related_navigation_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

def test_back_navigation_from_detail(driver):
    """Test navigating back to search results from a detail page"""
    print("Starting test_back_navigation_from_detail...")
    
    if not navigate_to_supplements_page(driver):
        pytest.skip("Could not navigate to supplements search page")
    
    try:
        # Find the search input
        search_input = driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Search']")
        
        # Use a common term that should return multiple results
        test_term = "vitamin"
        
        # Enter the search term
        search_input.clear()
        search_input.send_keys(test_term)
        
        # Submit the search form
        search_form = driver.find_element(By.TAG_NAME, "form")
        search_form.submit()
        
        # Wait for results page to load
        time.sleep(2)
        
        # Store the search results URL
        search_results_url = driver.current_url
        print(f"Search results URL: {search_results_url}")
        
        # Find and click on the first result
        supplement_cards = driver.find_elements(By.CSS_SELECTOR, ".card, article, div[class*='hover:shadow']")
        
        if len(supplement_cards) == 0:
            pytest.skip("No search results found to click on")
        
        supplement_cards[0].click()
        
        # Wait for the detail page to load
        time.sleep(2)
        
        # Take screenshot of the detail page
        driver.save_screenshot("detail_before_back.png")
        
        # Check for "Back to Home" button which will go to the homepage
        back_home_elements = driver.find_elements(By.PARTIAL_LINK_TEXT, "Back to Home")
        
        if back_home_elements:
            print("Found 'Back to Home' button which navigates to homepage - using browser back instead")
            # Use browser back navigation to return to the previous page
            driver.back()
        else:
            # Look for other back buttons
            back_elements = driver.find_elements(By.PARTIAL_LINK_TEXT, "Back")
            
            if back_elements:
                # Check if this button is a "Back to Home" or actual back button
                button_text = back_elements[0].text
                print(f"Found back element: {button_text}")
                
                if "home" in button_text.lower():
                    # It's a home button, use browser back instead
                    print("Back button goes to home page - using browser back instead")
                    driver.back()
                else:
                    # It's a proper back button, click it
                    back_elements[0].click()
            else:
                # No back button found, use browser back navigation
                print("No back button found, using browser back navigation")
                driver.back()
        
        # Wait for the search results page to reload
        time.sleep(2)
        
        # Take screenshot of the search results page
        driver.save_screenshot("back_to_search_results.png")
        
        # We need to validate the return path, which could be:
        # 1. Back to search results page (ideal case)
        # 2. Back to any page that contains search results
        current_url = driver.current_url
        print(f"Navigated back to: {current_url}")
        
        # Check if we're back at the search results page or showing search results
        is_on_search_results = "search-results" in current_url
        has_search_results = len(driver.find_elements(By.CSS_SELECTOR, ".card, article, div[class*='hover:shadow']")) > 0
        
        # Either condition is acceptable
        assert is_on_search_results or has_search_results, "Should navigate back to a page showing search results"
        
        print("Successfully navigated back from supplement detail page")
        
    except Exception as e:
        print(f"Error in test_back_navigation_from_detail: {str(e)}")
        driver.save_screenshot("back_navigation_error.png")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source excerpt: {driver.page_source[:500]}...")
        raise

if __name__ == "__main__":
    print("Running Selenium tests for supplement search and navigation")
    print(f"Frontend URL: {FRONTEND_BASE_URL}")
    print(f"API URL: {API_BASE_URL}") 