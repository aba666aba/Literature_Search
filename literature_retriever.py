"""
Literature Retrieval Application
This script crawls academic papers from Springer and ScienceDirect based on article names.
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
import pandas as pd
import argparse
import logging
from urllib.parse import urljoin, quote


class LiteratureRetriever:
    def __init__(self, headless=True, download_dir=None, browser='edge'):
        """
        Initialize the literature retriever with browser options
        :param headless: Whether to run browser in headless mode
        :param download_dir: Directory to save downloaded PDFs
        :param browser: Browser to use ('edge' or 'chrome')
        """
        self.headless = headless
        # Save directly in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.download_dir = download_dir or script_dir
        os.makedirs(self.download_dir, exist_ok=True)
        self.browser = browser
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('retriever.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize browsers
        self.springer_driver = self._init_browser()
        self.sciencedirect_driver = self._init_browser()
    
    def _init_browser(self):
        """Initialize an Edge browser with appropriate options"""
        edge_options = EdgeOptions()
        if self.headless:
            edge_options.add_argument("--headless")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)
        
        # Set download directory preferences for Edge
        # Edge uses different preferences format than Chrome
        edge_options.add_argument(f'--download.default_directory={self.download_dir}')
        edge_options.add_argument('--disable-extensions')
        edge_options.add_argument('--profile.default_content_settings.popups=0')
        edge_options.add_argument('--disable-plugins-discovery')
        
        # Initialize the Edge driver
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=edge_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    def search_springer(self, article_title):
        """
        Search for an article on Springer
        :param article_title: The title of the article to search for
        :return: URL of the article page or None if not found
        """
        self.logger.info(f"Searching Springer for: {article_title}")
        
        try:
            # Navigate to Springer
            self.springer_driver.get("https://link.springer.com/")
            time.sleep(2)
            
            # Find search input and enter the article title
            search_box = WebDriverWait(self.springer_driver, 10).until(
                EC.presence_of_element_located((By.ID, "query"))
            )
            search_box.clear()
            search_box.send_keys(article_title)
            
            # Click search button
            search_button = self.springer_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
            
            # Wait for results
            time.sleep(3)
            
            # Look for the article in search results
            results = self.springer_driver.find_elements(By.CSS_SELECTOR, "a[data-track-action='search result clicking']")
            
            for result in results:
                result_title = result.text.lower()
                if article_title.lower() in result_title:
                    article_url = result.get_attribute("href")
                    if not article_url.startswith("http"):
                        article_url = urljoin("https://link.springer.com", article_url)
                    self.logger.info(f"Found article on Springer: {article_url}")
                    return article_url
            
            self.logger.info("Article not found on Springer")
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching Springer: {str(e)}")
            return None
    
    def search_sciencedirect(self, article_title):
        """
        Search for an article on ScienceDirect
        :param article_title: The title of the article to search for
        :return: URL of the article page or None if not found
        """
        self.logger.info(f"Searching ScienceDirect for: {article_title}")
        
        try:
            # Navigate to ScienceDirect
            self.sciencedirect_driver.get("https://www.sciencedirect.com/")
            time.sleep(2)
            
            # Find search input and enter the article title
            search_box = WebDriverWait(self.sciencedirect_driver, 10).until(
                EC.presence_of_element_located((By.ID, "search-input"))
            )
            search_box.clear()
            search_box.send_keys(article_title)
            
            # Click search button
            search_button = self.sciencedirect_driver.find_element(By.CSS_SELECTOR, "button.HeaderSearchButton")
            search_button.click()
            
            # Wait for results
            time.sleep(3)
            
            # Look for the article in search results
            results = self.sciencedirect_driver.find_elements(By.CSS_SELECTOR, "h2 a")
            
            for result in results:
                result_title = result.text.lower()
                if article_title.lower() in result_title:
                    article_url = result.get_attribute("href")
                    if not article_url.startswith("http"):
                        article_url = urljoin("https://www.sciencedirect.com", article_url)
                    self.logger.info(f"Found article on ScienceDirect: {article_url}")
                    return article_url
            
            self.logger.info("Article not found on ScienceDirect")
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching ScienceDirect: {str(e)}")
            return None
    
    def download_pdf_springer(self, article_url):
        """
        Download PDF from Springer article page
        :param article_url: URL of the article page
        :return: Path to downloaded file or None if failed
        """
        self.logger.info(f"Attempting to download PDF from Springer: {article_url}")
        
        try:
            self.springer_driver.get(article_url)
            time.sleep(3)
            
            # Look for PDF download button
            pdf_button = None
            try:
                # Try multiple selectors for PDF download
                selectors = [
                    "a[data-track-action='pdf download']",
                    ".c-pdf-download__link",
                    "a[href*='/content/pdf']",
                    ".pdf-download"
                ]
                
                for selector in selectors:
                    try:
                        pdf_button = WebDriverWait(self.springer_driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        break
                    except:
                        continue
                
                if pdf_button:
                    # Get the PDF URL
                    pdf_url = pdf_button.get_attribute("href")
                    if not pdf_url.startswith("http"):
                        pdf_url = urljoin(article_url, pdf_url)
                    
                    # Download the PDF using requests to have more control
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        # Extract filename from URL
                        filename = pdf_url.split("/")[-1]
                        if not filename.endswith(".pdf"):
                            filename += ".pdf"
                        
                        filepath = os.path.join(self.download_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        self.logger.info(f"Successfully downloaded PDF: {filepath}")
                        return filepath
                    else:
                        self.logger.error(f"Failed to download PDF, status code: {response.status_code}")
                        return None
                        
            except Exception as e:
                self.logger.error(f"Error finding PDF button: {str(e)}")
                
            # If direct PDF download failed, try alternative method
            # Look for "Download PDF" link
            try:
                download_link = self.springer_driver.find_element(By.CSS_SELECTOR, "a[title='Download this article in PDF format']")
                download_link.click()
                time.sleep(5)  # Wait for download to start
                
                # For now, just return success since we can't determine exact filename
                self.logger.info("PDF download initiated from Springer")
                return True
                
            except:
                self.logger.error("Could not find PDF download link on Springer")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading PDF from Springer: {str(e)}")
            return None
    
    def download_pdf_sciencedirect(self, article_url):
        """
        Download PDF from ScienceDirect article page
        :param article_url: URL of the article page
        :return: Path to downloaded file or None if failed
        """
        self.logger.info(f"Attempting to download PDF from ScienceDirect: {article_url}")
        
        try:
            self.sciencedirect_driver.get(article_url)
            time.sleep(3)
            
            # Look for PDF download button
            try:
                # Try multiple selectors for PDF download
                selectors = [
                    "a[target='_blank'][href*='/pdf']",
                    "button[data-testid='pdf-download']",
                    "a.download-button-link",
                    "span.pdf-download-link a"
                ]
                
                pdf_button = None
                for selector in selectors:
                    try:
                        pdf_button = WebDriverWait(self.sciencedirect_driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        break
                    except:
                        continue
                
                if pdf_button:
                    # Get the PDF URL
                    pdf_url = pdf_button.get_attribute("href")
                    if not pdf_url.startswith("http"):
                        pdf_url = urljoin(article_url, pdf_url)
                    
                    # Extract filename from URL or article title
                    filename = pdf_url.split("/")[-1]
                    if not filename.endswith(".pdf"):
                        # Generate filename from article title
                        title_element = self.sciencedirect_driver.find_element(By.CSS_SELECTOR, "h1#title")
                        title = title_element.text.replace("/", "_").replace(":", "_").replace("*", "_")
                        filename = f"{title[:50]}.pdf".replace(" ", "_")  # Limit length and replace special chars
                    
                    filepath = os.path.join(self.download_dir, filename)
                    
                    # Download the PDF using requests
                    response = requests.get(pdf_url)
                    if response.status_code == 200:
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        self.logger.info(f"Successfully downloaded PDF: {filepath}")
                        return filepath
                    else:
                        self.logger.error(f"Failed to download PDF, status code: {response.status_code}")
                        return None
                        
            except Exception as e:
                self.logger.error(f"Error finding PDF button: {str(e)}")
                
            # Alternative method: try clicking the PDF button directly
            try:
                pdf_button = self.sciencedirect_driver.find_element(By.CSS_SELECTOR, "button[data-testid='pdf-download']")
                pdf_button.click()
                time.sleep(5)  # Wait for download to start
                
                self.logger.info("PDF download initiated from ScienceDirect")
                return True
                
            except:
                self.logger.error("Could not find PDF download button on ScienceDirect")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading PDF from ScienceDirect: {str(e)}")
            return None
    
    def retrieve_article(self, article_title):
        """
        Retrieve an article from either Springer or ScienceDirect
        :param article_title: Title of the article to retrieve
        :return: Path to downloaded file or None if failed
        """
        self.logger.info(f"Starting retrieval for: {article_title}")
        
        # Try Springer first
        springer_url = self.search_springer(article_title)
        if springer_url:
            return self.download_pdf_springer(springer_url)
        
        # If not found on Springer, try ScienceDirect
        sciencedirect_url = self.search_sciencedirect(article_title)
        if sciencedirect_url:
            return self.download_pdf_sciencedirect(sciencedirect_url)
        
        self.logger.warning(f"Could not find article '{article_title}' on either Springer or ScienceDirect")
        return None
    
    def retrieve_from_file(self, file_path):
        """
        Retrieve articles from a file containing article titles (one per line)
        :param file_path: Path to file with article titles
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            article_titles = [line.strip() for line in f if line.strip()]
        
        results = []
        for i, title in enumerate(article_titles):
            self.logger.info(f"Processing ({i+1}/{len(article_titles)}): {title}")
            result = self.retrieve_article(title)
            results.append({
                'title': title,
                'status': 'success' if result else 'failed',
                'path': result if result and isinstance(result, str) else None
            })
            # Add a delay to be respectful to the servers
            time.sleep(5)
        
        return results
    
    def close(self):
        """Close all browser instances"""
        if hasattr(self, 'springer_driver'):
            self.springer_driver.quit()
        if hasattr(self, 'sciencedirect_driver'):
            self.sciencedirect_driver.quit()


def main():
    parser = argparse.ArgumentParser(description="Retrieve academic papers from Springer and ScienceDirect")
    parser.add_argument("articles", nargs='*', help="Article titles to retrieve (or use -f to specify a file)")
    parser.add_argument("-f", "--file", help="File containing article titles (one per line)")
    parser.add_argument("-d", "--download-dir", help="Directory to save downloaded PDFs", 
                        default=os.path.dirname(os.path.abspath(__file__)))
    parser.add_argument("--no-headless", action="store_true", help="Run browser in visible mode")
    
    args = parser.parse_args()
    
    # Initialize retriever with Edge browser
    retriever = LiteratureRetriever(headless=not args.no_headless, download_dir=args.download_dir, browser='edge')
    
    try:
        if args.file:
            # Process articles from file
            results = retriever.retrieve_from_file(args.file)
            print("\nDownload Summary:")
            for result in results:
                status = "SUCCESS" if result['status'] == 'success' else "FAILED"
                path = result['path'] if result['path'] else "N/A"
                print(f"{status}: {result['title']} -> {path}")
        elif args.articles:
            # Process articles from command line arguments
            for article in args.articles:
                print(f"\nRetrieving: {article}")
                result = retriever.retrieve_article(article)
                if result:
                    print(f"Successfully downloaded: {result}")
                else:
                    print(f"Failed to retrieve: {article}")
        else:
            print("Please specify articles to retrieve or provide a file with article titles.")
            print("Usage: python literature_retriever.py 'Article Title 1' 'Article Title 2'")
            print("Or: python literature_retriever.py -f articles.txt")
    
    finally:
        retriever.close()


if __name__ == "__main__":
    main()