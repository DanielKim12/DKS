from bs4 import BeautifulSoup
from time import sleep
import time
import requests
from random import randint
import json
import re
import csv

USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

class SearchEngine:
    @staticmethod
    def search(query, sleep_flag=True):
        if sleep_flag:
            # Shorter random sleep interval: random between 7 to 13 seconds
            sleep_time = randint(7, 13)  
            time.sleep(sleep_time)

        temp_url = '+'.join(query.split())  # Adds + between words for the query
        #change to bing
        url = 'http://www.bing.com/search?q=' + temp_url + "&count=30"
        response = requests.get(url, headers=USER_AGENT)
        soup = BeautifulSoup(response.text, "html.parser")
        new_results = SearchEngine.scrape_search_result(soup)
        return new_results

    @staticmethod
    def scrape_search_result(soup):
        #bing url
        raw_results = soup.find_all("li", attrs = {"class" : "b_algo"})
        results = []
        found = set() #to keep track of duplicate links using set
        for result in raw_results:
            link = result.find('a').get('href')
            #append only unique links to the results that are not already in the set
            if link not in found:
                results.append(link)
                found.add(link) 
            #break if 10 results are found
            if len(results) == 10:
                break
        return results

class Comparison:
    def __main__(self):
        query_file = "./100QueriesSet1.txt"
        hw1_json = "./hw1.json"
        hw1_csv = "./hw1.csv"
        google_json = "./google.json"

        # Read all the queries from the file
        queries = []
        with open(query_file, 'r') as f:
            queries = f.readlines()

        # Commented out the code to save to hw1.json
        # search_results = {}  # Dictionary to hold the results

        # Loop through all the queries and search
        # for idx, query in enumerate(queries):
        #     query = query.strip()  # Remove any extra spaces/newlines
        #     results = SearchEngine.search(query)
        #     search_results[query] = results  # Add the results for this query, using the query itself as the key

        # print(f"Results saved to {hw1_json}")

        with open(hw1_json, 'r') as f:
            main_results = json.load(f)

        # Compare search results
        comparison_results = []
        # Init for comparison
        with open(google_json, 'r') as f:
            google_results = json.load(f)
    
        sum_overlaps, sum_percent, sum_rho = 0, 0, 0

        # Comparison for hw1.json and google.json
        for idx, query in enumerate(queries):
            main_urls = main_results[query]
            ref_urls = google_results[query]

            # Map URLs for their position based on their ranks 
            main_urls_map = {}
            for rank, val in enumerate(main_urls):
                val = self.trimUrl(val)
                main_urls_map[val] = rank

            overlaps, sum = 0, 0
            match = False 
            for rank, val in enumerate(ref_urls):
                val = self.trimUrl(val)
                if val in main_urls_map:
                    overlaps += 1
                    # Calculate Spearman's rank correlation
                    sum += abs(main_urls_map[val] - rank) ** 2
                    # If match is found, set match to true
                    match = (rank == main_urls_map[val])

            # Calculate Spearman's rank correlation
            rho = 0 if overlaps == 0 else (1 if overlaps == 1 and match else (0 if match else 1 - (6 * sum) / (overlaps * (overlaps ** 2 - 1))))
            # Calculate overlap percentage
            percent = (overlaps / 10) * 100
            # Append to comparison results
            comparison_results.append({"query": query.strip(), "overlap": overlaps, "percent": percent, "rho": rho, "match": match})
            # Sum for average
            sum_overlaps += overlaps
            sum_percent += percent
            sum_rho += rho

        # Write to CSV 
        with open(hw1_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Queries", "No of Overlapping Results", "Percent Overlap", "Spearman Coefficient"])
            writer.writerows([[res["query"], res["overlap"], res["percent"], res["rho"]] for res in comparison_results])
            writer.writerow(["Averages", sum_overlaps/len(queries), sum_percent/len(queries), sum_rho/len(queries)])

    # Normalizing URLs
    def trimUrl(self, url):
        # Normalizes URLs by trimming HTTP/HTTPS, www., and trailing slashes.
        url = re.sub(r'^(http://|https://)?(www\.)?', '', url)
        url = url.rstrip('/')
        return url

# Run the main function
Comparison.__main__()

