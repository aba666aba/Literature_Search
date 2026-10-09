import os
import sys
import time
from literature_retriever import LiteratureRetriever

def test_article_download():
    """Test downloading a specific article"""
    print("Starting test for article: 'Screening and evaluation of prebiotic exopolysaccharide of Lactobacillus plantarum on treating IBD in mice'")
    
    # Create retriever with Edge browser
    retriever = LiteratureRetriever(headless=False, browser='edge')  # Using visible mode for testing
    
    article_title = "Screening and evaluation of prebiotic exopolysaccharide of Lactobacillus plantarum on treating IBD in mice"
    
    try:
        print(f"Searching for: {article_title}")
        result = retriever.retrieve_article(article_title)
        
        if result:
            print(f"Successfully downloaded: {result}")
        else:
            print(f"Failed to retrieve the article: {article_title}")
            
    except Exception as e:
        print(f"Error occurred during retrieval: {str(e)}")
    finally:
        retriever.close()

if __name__ == "__main__":
    test_article_download()