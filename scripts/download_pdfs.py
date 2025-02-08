import requests
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, unquote
from pathlib import Path
import json
from datetime import datetime
import time
import hashlib


class PDFDownloader:
    def __init__(self, output_dir="../data/downloaded_pdfs", max_workers=10):
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.setup_logging()
        self.setup_directories()
        self.results = {"successful": [], "failed": []}

    def setup_logging(self):
        """Configure logging with both file and console handlers"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(f"logs/pdf_downloader_{timestamp}.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def setup_directories(self):
        """Create necessary directories"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output directory set to: {self.output_dir}")

    def generate_filename(self, url, content):
        """Generate a unique filename based on URL and content hash"""

        parsed_url = urlparse(url)
        original_name = unquote(os.path.basename(parsed_url.path))

        content_hash = hashlib.md5(content).hexdigest()[:8]

        base_name = os.path.splitext(original_name)[0]
        return f"{base_name}_{content_hash}.pdf"

    def download_pdf(self, url):
        """Download a single PDF file"""
        try:
            start_time = time.time()
            self.logger.info(f"Starting download: {url}")

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()
            if "application/pdf" not in content_type:
                raise ValueError(f"Not a PDF file. Content-Type: {content_type}")

            filename = self.generate_filename(url, response.content)
            filepath = self.output_dir / filename

            with open(filepath, "wb") as f:
                f.write(response.content)

            download_time = time.time() - start_time
            file_size = len(response.content) / 1024

            self.logger.info(f"Successfully downloaded: {url}")
            self.logger.info(f"Saved as: {filename}")
            self.logger.info(f"Download time: {download_time:.2f}s")
            self.logger.info(f"File size: {file_size:.2f}KB")

            return {
                "url": url,
                "status": "success",
                "filename": filename,
                "size_kb": file_size,
                "download_time": download_time,
            }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download {url}: {str(e)}")
            return {"url": url, "status": "failed", "error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error downloading {url}: {str(e)}")
            return {"url": url, "status": "failed", "error": str(e)}

    def download_all(self, urls):
        """Download multiple PDFs using thread pool"""
        total_urls = len(urls)
        self.logger.info(
            f"Starting download of {total_urls} PDFs with {self.max_workers} workers"
        )

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {
                executor.submit(self.download_pdf, url): url for url in urls
            }

            for i, future in enumerate(as_completed(future_to_url), 1):
                result = future.result()
                if result["status"] == "success":
                    self.results["successful"].append(result)
                else:
                    self.results["failed"].append(result)

                self.logger.info(
                    f"Progress: {i}/{total_urls} ({(i/total_urls)*100:.1f}%)"
                )

        total_time = time.time() - start_time
        self.log_summary(total_time)
        self.save_results()

    def log_summary(self, total_time):
        """Log summary of the download operation"""
        successful = len(self.results["successful"])
        failed = len(self.results["failed"])
        total = successful + failed

        self.logger.info("\n=== Download Summary ===")
        self.logger.info(f"Total time: {total_time:.2f} seconds")
        self.logger.info(f"Total PDFs: {total}")
        self.logger.info(f"Successfully downloaded: {successful}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Success rate: {(successful/total)*100:.1f}%")

        if successful > 0:
            avg_size = (
                sum(r["size_kb"] for r in self.results["successful"]) / successful
            )
            avg_time = (
                sum(r["download_time"] for r in self.results["successful"]) / successful
            )
            self.logger.info(f"Average file size: {avg_size:.2f}KB")
            self.logger.info(f"Average download time: {avg_time:.2f}s")

    def save_results(self):
        """Save download results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = Path(f"download_results_{timestamp}.json")

        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        self.logger.info(f"Results saved to: {results_file}")


if __name__ == "__main__":

    with open("../data/pdf_links.json", "r") as f:
        urls = json.load(f)

    downloader = PDFDownloader(output_dir="../data/downloaded_pdfs", max_workers=6)

    downloader.download_all(urls)
