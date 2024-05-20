from pathlib import Path

import scrapy
import io
import json
import scrapy.selector
import re

class ReviewsSpider(scrapy.Spider):
    name = "reviews"

    def start_requests(self):


        urls_uk = []


        """urls_us = ["https://www.tripadvisor.co.uk/Restaurant_Review-g60763-d613504-Reviews-Darbar-New_York_City_New_York.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g56003-d946189-Reviews-Starport_Cafe_NASA_s_Johnson_Space_Center_s_Cafeteria-Houston_Texas.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g56003-d484577-Reviews-Tia_Maria_s_Mexican_Restaurant-Houston_Texas.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g56003-d15779264-Reviews-Wendy_s-Houston_Texas.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g56003-d4195283-Reviews-Taco_Bell-Houston_Texas.html"]
        """

        """urls_us = ["https://www.tripadvisor.co.uk/Restaurant_Review-g50267-d4955870-Reviews-Taco_Bell-Delaware_Ohio.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g50267-d4947342-Reviews-Whit_s_Frozen_Custard_of_Delaware-Delaware_Ohio.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g50267-d539819-Reviews-Hamburger_Inn_Diner-Delaware_Ohio.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g50226-d826694-Reviews-Sushi_En_Columbus-Columbus_Ohio.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g50463-d4979642-Reviews-McDonald_s-Hudson_Ohio.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g51013-d2005192-Reviews-Nervous_Dog_Coffee_Bar-Stow_Ohio.html"
                   ]"""

        urls_uk = ["https://www.tripadvisor.co.uk/Restaurant_Review-g186254-d1229430-Reviews-KFC_Exeter-Exeter_Devon_England.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g186254-d23373767-Reviews-German_Doner_Kebab-Exeter_Devon_England.html",
                   "https://www.tripadvisor.co.uk/Restaurant_Review-g190832-d12672339-Reviews-KFC_Seaham-Durham_County_Durham_England.html" ,
                    "https://www.tripadvisor.com/Restaurant_Review-g616275-d4136078-Reviews-or45-The_French_Deli-Stourbridge_West_Midlands_England.html",
                    "https://www.tripadvisor.com/Restaurant_Review-g8572481-d3572945-Reviews-Beaufort_Arms-Stoke_Gifford_Gloucestershire_England.html",
                    "https://www.tripadvisor.co.uk/Restaurant_Review-g186254-d7591146-Reviews-The_Victoria_Inn-Exeter_Devon_England.html",
                    "https://www.tripadvisor.co.uk/Restaurant_Review-g186254-d4523219-Reviews-Brody_s_Breakfast_Bistro-Exeter_Devon_England.html",
                    "https://www.tripadvisor.co.uk/Restaurant_Review-g186254-d2510993-Reviews-Georges_Meeting_House-Exeter_Devon_England.html",
                    "https://www.tripadvisor.co.uk/Restaurant_Review-g186254-d8530714-Reviews-Frankie_Benny_s-Exeter_Devon_England.html"]





        # For each top URL
        for url in urls_uk:

            # Generate the subpage urls
            url_pages = [url]
            page_count = 15
            for _ in range(10):
                # Define the regex pattern to find the correct insertion point
                pattern = re.compile(r'(Reviews)')

                # Replace the pattern with page selector
                page_selector = r'\1-or' + str(page_count)
                modified_url = re.sub(pattern, page_selector, url)
                page_count += 15

                url_pages.append(modified_url)

            for url_page in url_pages:
                try:
                    yield scrapy.Request(url=url_page, callback=self.parse)
                finally:
                    print("bruh")


    #def parse(self, response):
    #    page = response.url.split("/")[-2]
    #    print(page)
    #    filename = f"reviews-{page}.html"
    #    Path(filename).write_bytes(response.body)
    #    self.log(f"Saved file {filename}")

    def parse(self, response):

        # Select the review containers using XPath
        review_containers = response.xpath('//div[contains(@class, "mobile-more")]')

        for review in review_containers:
            # Extract paragraphs with the class name "partial_entry"
            review_text = review.xpath('.//p[contains(@class, "partial_entry")]/text()').extract_first()
            #print(paragraphs)

            # Get the column containing the review stars
            quote_container = review.xpath('.//div[contains(@class, "quote")]')

            # Get the column containing the review stars (quote_container) and then select its parent div
            parent_div = quote_container.xpath('..')

            # Get first item in parent div, this will be the star review span
            first_item_in_parent = parent_div.xpath('./*[1]')


            review_class = first_item_in_parent.xpath('./@class').extract_first()

            star = 0
            if review_class == "ui_bubble_rating bubble_50":
                star = 5
            elif review_class == "ui_bubble_rating bubble_40":
                star = 4
            elif review_class == "ui_bubble_rating bubble_30":
                star = 3
            elif review_class == "ui_bubble_rating bubble_20":
                star = 2
            elif review_class == "ui_bubble_rating bubble_10":
                star = 1

            # Save the paragraphs to a JSON file
            #print(review_text)
            #print(star)

            # Check the review has been done properly
            if star == 0 or review_text == None or review_text == "null":
                print("Review couldn't be parsed")
            else:
                self.save_to_jsonl(review_text, star)


    def save_to_jsonl(self, review_text, star_rating):
        # Define the output file path
        output_file = 'reviews_UK.jsonl'

        # Create a dictionary to represent the review and its star rating
        review_data = {
            "review": review_text,
            "stars": star_rating
        }

        try:
            # Append the review data to the JSONL file with UTF-8 encoding
            with io.open(output_file, 'a', encoding='utf-8') as f:
                # Dump the dictionary as a JSON string and append a newline character
                f.write(json.dumps(review_data, ensure_ascii=False) + '\n')

            #self.log(f'Appended review to {output_file}')

        except Exception as e:
            self.log(f"Error during saving to JSONL: {str(e)}")