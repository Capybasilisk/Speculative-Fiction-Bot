import requests
import bs4
import clevercsv
import re




def catalog():
    
    """Scrapes metadata of science fiction and fantasy literary works 
    from The Internet Speculative Fiction Database and stores them in 
    a CSV file. If site structure changes significantly, code may stop 
    functioning properly.
    """

    card = 0
    
    for entry in range(199000):
        
        try:
        
            card += 1

            
            page = requests.get(
                f"http://www.isfdb.org/cgi-bin/title.cgi?{card}")
            parsed = bs4.BeautifulSoup(
                page.content, 
                "html.parser")
            content = parsed.find(
                id = "content").text.split("\n")
            content_string = "##".join(content)

            
            content_title = re.search(
                "Title:\s+[^#]+", content_string).group(0)
            title = content_title.split(": ")[1] 

            content_author = re.search(
                "Author:##[^#]+", content_string).group(0)
            author = content_author.split("##")[1]

            content_date = re.search(
                "Date:\s+\d+\-\d+\-\d+", content_string).group(0)
            pubdate = content_date.split("  ")[1]

            content_type = re.search(
                "Type:\s+[^#]+", content_string).group(0)
            booktype = content_type.split(": ")[1]


            accepted_booktype = [
                "NOVEL",  
                "SHORTFICTION", 
                "COLLECTION", 
                "ANTHOLOGY", 
                "OMNIBUS", 
                "POEM",
                "NONFICTION", 
                "ESSAY"]


            with open(
                "SFF_Dataset.csv", "a", encoding="UTF-8") as sff:
                dataset = clevercsv.writer(sff)

                if sff.tell() == 0:
                    
                    dataset.writerow(
                        ["Title",
                        "Author", 
                        "Publication Date", 
                        "Type"])

                if booktype in accepted_booktype:

                    dataset.writerow(
                        [title, 
                        author, 
                        pubdate,
                        booktype])


        except:

            print(
                f"Skipping entry no. {card}: Empty article.", "\n" *4)

            continue  



if __name__ == "__main__":

    catalog()




    
