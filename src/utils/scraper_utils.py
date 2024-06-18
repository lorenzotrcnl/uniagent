import os
import re
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def is_valid_url(url):
    """
    Check if the URL is valid.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_links(url, visited):
    """
    Get all links from a given URL.
    """
    try:
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        urls = set()
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            if href in visited:
                continue
            if is_valid_url(href):
                urls.add(href)
        return urls
    except requests.exceptions.RequestException as e:
        return set()


def download_pdf(url, folder="pdfs"):
    """
    Download a single PDF.
    """
    response = requests.get(url, verify=False)
    if response.status_code == 404:
        pattern = r"(https://[^/]+).*?(/uploads)"
        url = re.sub(pattern, r"\1\2", url)
        response = requests.get(url, stream=True, verify=False)

    file_name = "_".join(url[: url.find(".pdf") + len(".pdf")].split("/"))
    if len(file_name) > 240:
        diff = len(file_name) - 240
        file_name = file_name[diff:]
    local_path = os.path.join(folder, file_name)
    with open(local_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print(f"Downloaded: {url}")


def crawl_and_download_pdfs(start_url, output_folder):
    """
    Crawl the website starting from start_url and download all PDFs.
    """
    os.makedirs(output_folder, exist_ok=True)

    visited_urls = set()
    urls_to_visit = get_all_links(start_url, visited_urls)

    while urls_to_visit:
        current_url = urls_to_visit.pop()
        if current_url not in visited_urls:
            visited_urls.add(current_url)
            if ".pdf" in current_url:
                download_pdf(current_url, output_folder)
            else:
                new_links = get_all_links(current_url, visited_urls)
                urls_to_visit.update(new_links - visited_urls)
