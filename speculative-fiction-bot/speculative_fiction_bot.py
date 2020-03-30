
import praw
import clevercsv
import subprocess 
import youtube_dl
import json
import pendulum 
import loguru
import time
import collections




def speculative():
    
    """Uses scraped data from the Internet Speculative Fiction Database to search 
    YouTube for SF/Fantasy audiobooks. Title/author pairs read 
    from "isfdb_catalog.csv" file.    
    """
    
    
    bot = praw.Reddit(
            client_id = "client_id",
            client_secret = "client_secret",
            username = "username",
            password = "password",
            user_agent = "user_agent")
                       
    
    comments = bot.subreddit("all").stream.comments(skip_existing = True)

    responded = collections.deque(maxlen = 100)

    with open("isfdb_catalog.csv", "r", encoding = "UTF-8") as isfdb_catalog: 
      isfdb_catalog = clevercsv.reader(isfdb_catalog)

      catalog = [[row[0],row[1]] for row in isfdb_catalog if len(row) > 1]
    
    
    for comment in comments:
        text = comment.body.lower().replace(".", "")
        
        for card in catalog:
            
            if (
                card[0].lower() in text and card[1].lower() in text
                and not comment.submission.id in responded
                and not comment.subreddit.user_is_banned):
        
                info = subprocess.check_output(
                    ["youtube-dl", "-i", "-j", 
                    f"ytsearch: {card[0]} {card[1]} audiobook"])
                
                jdict = json.loads(info)

                audio = ["audiobook", "audio book"]

                author_format = [
                name.lower() for name in card[1].split(" ") if len(name) >= 3]

                if (
                    jdict["duration"] > 10800 
                    and card[0].lower() in jdict["title"].lower()
                    and any(
                        item in jdict["title"].lower() for item in audio)
                    and all(
                        item in jdict["title"].lower() for item in author_format)):

                    
                    signature = ("""[^(Source Code)](https://github.com/capybasilisk/"""
                                 """speculative-fiction-bot) ^| [^(Feedback)](https"""
                                 """://www.reddit.com/message/compose?to=Capybasilisk&"""
                                 """subject=Robot) ^| [^(Programmer)](https://reddit.com"""
                                 """/u/capybasilisk) ^| ^Downvote ^To ^Remove ^| """
                                 """^Version ^1.4.0 ^| ^(Support Robot Rights!)""")


                    comment.reply(
                        f"Hi. You just mentioned *{card[0]}* by " 
                        f"{card[1]}.\n\nI've found an audiobook of "   
                        "that novel on YouTube. You can listen to it here:"
                        f"\n\n[YouTube | {jdict['title']}]"
                        f"({jdict['webpage_url']})\n\n*I\'m a bot that " 
                        "searches YouTube for science fiction and fantasy "  
                        f"audiobooks.*\n***\n{signature}")

                    
                    responded.append(comment.submission.id)

                    with open("activity.csv", "a", encoding = "UTF-8") as actlog:
                        activity = clevercsv.writer(actlog)
                        
                        if actlog.tell() == 0:
                            activity.writerow(
                                ["Book",
                                "Comment", 
                                "Author", 
                                "Thread", 
                                "Subreddit", 
                                "Time"])

                        activity.writerow(
                            [f"{card[0]} by {card[1]}",
                            f"{comment.body}",
                            f"{comment.author}",
                            f"{comment.submission.title}",
                            f"{comment.subreddit}",
                            f"{pendulum.now().to_datetime_string()}"])
                    
                    break        

        if pendulum.now().to_time_string().endswith("0:00"):
            replies = bot.user.me().comments.new(limit=100)
            
            for reply in replies:
                if reply.score < 0:
                    
                    with open("deleted.csv", "a", encoding = "UTF-8") as removed:
                        deleted = clevercsv.writer(removed)
                        
                        if removed.tell() == 0:
                           deleted.writerow(
                            ["Comment", 
                            "Parent",  
                            "Thread", 
                            "Subreddit", 
                            "Time", 
                            "Score"])
                        
                        deleted.writerow(
                            [f"{reply.body}", 
                             f"{reply.parent().body}", 
                             f"{reply.submission.title}", 
                             f"{reply.subreddit}", 
                             f"{pendulum.from_timestamp(reply.created_utc)}", 
                             f"{reply.score}"])

                    reply.delete()

            time.sleep(1)



def eventlogger(event):
    
    eventlogger = loguru.logger

    eventlogger.add(
        sink = "events.log", 
        level = "WARNING", 
        format = "\n\n\n\n{level} {time: {time:DD-MM-YYYY HH:mm:ss}}\n"
                 "Elapsed Time: {elapsed}\n"
                 "File: {file}\n"
                 "Message: {message}")
    
    eventlogger.exception(event)


            
if __name__ == "__main__":

    while True:

        try:

            speculative()

        except Exception as event:

            eventlogger(event)
            time.sleep(600)
            continue




            
