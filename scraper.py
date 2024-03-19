import asyncio
import csv

from lxml.html import fromstring
from playwright.async_api import Playwright, async_playwright


async def extract_data(page):
    """
    Extracts data from the TikTok page and writes it to a CSV file.

    Args:
        page: The Playwright page object representing the TikTok page.
    """
    usernames = await extract_text(page, 'h3[data-e2e="video-author-uniqueid"]')
    descriptions = await extract_text(page, 'div[data-e2e="video-desc"]')
    likes = await extract_text(page, 'strong[data-e2e="like-count"]')
    comments = await extract_text(page, 'strong[data-e2e="comment-count"]')
    shares = await extract_text(page, 'strong[data-e2e="share-count"]')
    others = await extract_text(page, 'strong[data-e2e="undefined-count"]')

    write_to_csv([usernames, descriptions, likes, comments, shares, others])


async def extract_text(page, selector):
    """
    Extracts text content from elements matching the given CSS selector on the page.

    Args:
        page: The Playwright page object representing the TikTok page.
        selector: CSS selector string.

    Returns:
        A list of texts extracted from the elements.
    """
    elements = await page.query_selector_all(selector)
    texts = []
    for element in elements:
        texts.append(await element.inner_text() if element else "")
    return texts


def write_to_csv(data_lists):
    """
    Writes the extracted data to a CSV file.

    Args:
        data_lists: A list of lists containing the extracted data.
    """
    headers = ["Username", "Description", "Likes", "Comments", "Shares", "Others"]
    filename = "instagram_extracted_data.csv"
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in zip(*data_lists):
            writer.writerow(row)


async def run(playwright: Playwright) -> None:
    """
    Launches a Chromium browser and extracts data from TikTok.

    Args:
        playwright: The Playwright instance.
    """
    browser = await playwright.chromium.launch(
        headless=False, proxy={"server": "172.16.244.221:20071"}
    )
    context = await browser.new_context()
    # Open new page
    page = await context.new_page()

    await page.goto(
        "https://www.tiktok.com/foryou", timeout=120000, wait_until="networkidle"
    )
    await page.locator('//div[@id="loginContainer"]').wait_for()
    await page.get_by_role("link", name="Continue as guest").click()
    await page.wait_for_timeout(2000)
    await extract_data(page)
    await context.close()
    await browser.close()


async def main() -> None:
    """
    Main entry point of the program.
    """
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
