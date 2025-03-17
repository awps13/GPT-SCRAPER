from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
import time
from json import dumps
from bs4 import BeautifulSoup # type: ignore

def scrape(url, timeout=1000, headless=False):
    # Headless browser
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome() if not headless else webdriver.Chrome(options=options)
    
    driver.get(url)
    max_retries = 3
    retries = 0
    
    user_chat = []
    assistant_chat = []
    assistant_chat_raw = []
    
    while retries <= max_retries and not user_chat:
        try:
            # Wait until chat elements have been loaded
            WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-message-author-role="user"]'))
            )
            WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-message-author-role="assistant"]'))
            )
            print("Page loaded")
            
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Get all chat elements with user and assistant roles
            user_chat_elements = soup.find_all('div', attrs={'data-message-author-role': 'user'})
            assistant_chat_elements = soup.find_all('div', attrs={'data-message-author-role': 'assistant'})
            
            user_chat = [chat.get_text() for chat in user_chat_elements]
            assistant_chat = [str(chat) for chat in assistant_chat_elements]
            assistant_chat_raw = [chat.get_text() for chat in assistant_chat_elements]
            
            if not user_chat and retries < max_retries:
                print(f"No chats found. Retrying... {retries + 1}")
                time.sleep(2)
                retries += 1
            else:
                break
                
        except Exception as e:
            print(f"Error: {e}")
            if retries < max_retries:
                print(f"Retrying... {retries + 1}")
                time.sleep(2)
                retries += 1
            else:
                break
    
    # Close the browser after all attempts
    driver.quit()
    
    return user_chat, assistant_chat, assistant_chat_raw

if __name__ == '__main__':
  url = "https://chatgpt.com/share/67b5c1df-0848-8010-991c-261f15462e5a"

  user_chat, assitant_chat = scrape(url)

  print(f"User chat: (total: {len(user_chat)})")
  for chat in user_chat:
    # print(chat)
    pass

  print(f"Assistant chat: (total: {len(assitant_chat)})")
  for chat in assitant_chat:
    # print(chat)
    pass

  result = []
  for i in range(len(user_chat)):
    result.append({"role": "user", "text": user_chat[i]})
    if i < len(assitant_chat):
      result.append({"role": "assistant", "text": assitant_chat[i]})
    
  print(dumps(result, ensure_ascii=False))