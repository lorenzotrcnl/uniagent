from src.utils.scraper_utils import crawl_and_download_pdfs


def run(url_path, output_folder):
    crawl_and_download_pdfs(url_path, output_folder)


if __name__ == "__main__":
    run("https://web.unisa.it", "results")
