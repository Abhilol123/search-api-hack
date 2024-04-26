import asyncio
import logging
import re
import time

import uvicorn
from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)


app = FastAPI()


def get_text_from_html(html: str) -> str:
    """
    Clean up the HTML content and keep only the relevant content
    """
    # Remove new lines
    html = html.replace("\n", " ")
    # Remove extra spaces
    html = " ".join(html.split())
    # Remove script tags
    html = html.replace("<script>", "").replace("</script>", "")
    # Remove style tags
    html = html.replace("<style>", "").replace("</style>", "")
    # Remove comments
    html = re.sub(r"<!--(.*?)-->", "", html)
    # Remove all the tags
    html = re.sub(r"<.*?>", "", html)
    # Remove extra spaces
    html = " ".join(html.split())
    # Return the cleaned up content
    return html


def search_google(query):
    # Configure Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    # Set up the WebDriver
    driver = webdriver.Chrome(options=options)

    # Open Google
    driver.get("https://www.google.com")

    # Find the search box
    search_box = driver.find_element(By.NAME, "q")

    # Send the search query
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    # Wait for the results to load
    asyncio.run(asyncio.sleep(1))

    # Find search results
    results = driver.find_elements(By.CSS_SELECTOR, "div.g")

    # Print the title and URL for each result
    for result in results:
        title = result.find_element(By.TAG_NAME, "h3")
        if title:
            logging.info(title.text)
        link = result.find_element(By.TAG_NAME, "a")
        logging.info(link.get_attribute("href"))

    # create a json with results
    results_json = []
    for result in results:
        title = result.find_element(By.TAG_NAME, "h3")
        link = result.find_element(By.TAG_NAME, "a")
        results_json.append({"title": title.text, "url": link.get_attribute("href")})
    # results_json as json
    logging.info(results_json)

    # go to each result and get the content
    for i, result in enumerate(results_json):
        try:
            driver.get(result["url"])
            asyncio.run(asyncio.sleep(1))
            content = driver.find_element(By.TAG_NAME, "body")
            logging.info(content.text)
            # clean up htm and keep only relevant content
            cleaned_content = get_text_from_html(content.text)
            logging.info(cleaned_content)
            results_json[i]["content"] = cleaned_content
        except Exception as e:
            logging.error("Error while getting content from URL")
            logging.error(e)

    # Close the driver
    driver.quit()
    return results_json


@app.get("/{search_query}")
def search_google_resource(search_query: str):
    results_json = search_google(search_query)
    return results_json


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
