
from app.service.listscraper.instance_class import ScrapeInstance
from pandas import DataFrame as df

def scrape_movies(listURL, output_name, concat = True, pages = "*", output_path = "app/service/data", output_file_extension = ".csv", file = None, quiet = False, threads = 4):
    """
    Starts the program and prints some text when finished.
    """

    # Welcome message
    print("=============================================")
    print("           Letterboxd-List-Scraper           ")
    print("=============================================")

    LBscraper = ScrapeInstance(listURL, pages, output_name, output_path, output_file_extension, file, concat, quiet, threads)    
    
    # # End message
    print(f"\nProgram successfully finished! Your {LBscraper.output_file_extension}(s) can be found in ./{LBscraper.output_path}/.")
    print(f"    Total run time was {LBscraper.endtime - LBscraper.starttime :.2f} seconds.")

    return LBscraper.scraped_movies