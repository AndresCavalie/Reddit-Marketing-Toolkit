from . import scheduler
from .models import Search, Post, User , Info
from . import db, rmt
import os
from sqlalchemy import and_
import datetime
import time
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

rows=db.session.query(Info).count()
print(rows)
if rows == 0:
    info = Info(running = False)
    db.session.add(info)
    db.session.commit()
    print("added row")
rows=db.session.query(Info).count()
print("WE HAVE" , rows)
info = db.session.query(Info).first()
info.running = False
db.session.commit()
print(info.running)
SERVER_EMAIL = os.getenv('SERVER_EMAIL')
SERVER_EMAIL_PWD = os.getenv('SERVER_EMAIL_PWD')



def emailNewDB(search,user):
    titles = ""
    lastEmail = search.lastemail
    lastEmail = (int)(lastEmail.timestamp())
    for post in search.posts:
        if post.realdate > lastEmail:
            titles +=    """<div class = "post" style ="background-color:rgb(241, 241, 241);width: 50em; margin: auto; padding:2em; border-radius: .5em;">
    <table style=" width: 40em; ">
        <tr>
            <td><p style ="display: inline; width:30em;">r/"""+post.subreddit+""" &#x2022; """+post.date+"""</p></td>
            
        </tr>
        <tr>
          <td></br><a class = "postlink" href="https://www.reddit.com"""+post.permalink+"""" ><h1 style ="display: inline;">"""+post.title+"""</h1></a></td>
        
        </tr>
        <tr>
          <td></br><p style ="display: inline; font-size:larger word-break: break-all;
            white-space: normal;">"""+post.selftext+"""</p></td>
         
        </tr>
        <tr>
            <td></br><p style ="display: inline;">keyword(s):"""+post.keyword+"""</p></td>
           
          </tr>
      </table>
</div></br></br>"""
            
            
            
            

            
            
    msg = EmailMessage()
    msg['Subject'] = 'New Posts in &nbsp;' + search.name
    msg['From'] = SERVER_EMAIL
    msg['To'] = user.email

    msg.add_alternative("""\
    <!DOCTYPE html>
    <html>
    <head>
    <style>.postlink:hover {color: rgb(109, 109, 109);}
      .postlink { color: black;}</style>
    <head>
        <body>
            </br>""" + titles + """\
        </body>
    </html>
    """, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SERVER_EMAIL, SERVER_EMAIL_PWD)
        smtp.send_message(msg)

@scheduler.task(
    trigger = "interval",
    id= "job_1",
    minutes = 2,
    max_instances=1
)
def task1():
    with scheduler.app.app_context():
        print("CHECKER")
        for user in db.session.query(User).join(Search).filter(Search.user_id == User.id).all(): #query all users with a search
            print("searching" + user.first_name)
            for search in db.session.query(Search).filter(Search.user_id==user.id).all(): #query all searches for the user found above
                #open blank posttittles variable
                if search.frequency == 'everypost':
                        titles = ""
                #get last check timestamp time
                lasttime = search.lastcheck
                #turn timestamp time into epoch
                lasttime = (int)(lasttime.timestamp())
                
                #get current time in epoch
                currenttime =(int)(time.time()) 
                
                #find difference between current time and last check
                timesince = currenttime-lasttime
                
                #turn comma separated list into python list
                subreddits = (search.subreddits).split(',') 
                keywords = (search.keywords).split(',')
                
                #do RMT Search for current search in range of timesince          
               # while(__init__.running == True):
               #     time.sleep(3)
               #    print("waiting on CREATE")
               # __init__.running = True
                state= False
                
                info = db.session.query(Info).first()
                db.session.refresh(info) 
                if info.running == True:
                    state = True   
                while(state == True):
                    time.sleep(1)
                    db.session.refresh(info)
                    print(info.running)
                    if info.running == False:
                        state = False
                    print("WAITING ON VIEWS")
                
                info.running = True
                db.session.commit()
                
                print("SCHEDULER SWITCH TO TRUE")
                print("views should be paused")
                
                df = rmt.search(subreddits=subreddits, keywords= keywords, timesince=timesince)
                print("rmt is done adding 5 extra seconds of Sched True")
                time.sleep(5)
                
                info.running = False
                db.session.commit()
                info =  db.session.query(Info).first()
                print(info.running)
                print("VIEWS SHOULD RUN NOW")
                time.sleep(20)
                
                #add in range searches to db
                for i in range(len(df)):
                    title = df.loc[i, "title"]
                    selftext = df.loc[i, "selftext"]
                    date = df.loc[i, "date"]
                    realdate = df.loc[i, "realdate"]
                    keyword = df.loc[i, "keyword"]
                    subreddit = df.loc[i, "subreddit"]
                    permalink = df.loc[i, "permalink"]
                    newPost = Post(search_id=search.id,title=title,selftext=selftext,date=date,realdate=realdate,keyword=keyword,subreddit=subreddit,permalink=permalink)
                    db.session.add(newPost)
                    db.session.commit()
                    #add each post title to title string
                    if search.frequency == 'everypost':
                        titles += """<div class = "post" style ="background-color:rgb(241, 241, 241);width: 50em; margin: auto; padding:2em; border-radius: .5em;">
    <table style=" width: 40em; ">
        <tr>
            <td><p style ="display: inline; width:30em;">r/"""+subreddit+""" &#x2022; """+date+"""</p></td>
            
        </tr>
        <tr>
          <td></br><a class = "postlink" href="https://www.reddit.com"""+permalink+"""" ><h1 style ="display: inline;">"""+title+"""</h1></a></td>
        
        </tr>
        <tr>
          <td></br><p style ="display: inline; font-size:larger word-break: break-all;
            white-space: normal;">"""+selftext+"""</p></td>
         
        </tr>
        <tr>
            <td></br><p style ="display: inline;">keyword(s):"""+keyword+"""</p></td>
           
          </tr>
      </table>
</div></br></br>"""
                    
                
                #change lastcheck date for search
                search.lastcheck = datetime.datetime.now()
                db.session.commit()
                #if there are new posts and this search has 'everypost' frequency
                if search.frequency == 'everypost' and len(df) > 0:
                    
                    msg = EmailMessage()
                    msg['Subject'] = 'New Posts in' + search.name
                    msg['From'] = SERVER_EMAIL
                    msg['To'] = user.email
                    
                    msg.add_alternative("""\
                    <!DOCTYPE html>
                    <html>
                        <body>
                            </br>""" + titles + """\
                        </body>
                    </html>
                    """, subtype='html')
                    
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(SERVER_EMAIL, SERVER_EMAIL_PWD)
                        smtp.send_message(msg)
                    
                    #update last email date in case of user changing search frequency
                    search.lastemail = datetime.datetime.now()
                    db.session.commit()
            
@scheduler.task(
    trigger="cron",
    id='Daily Email',
    hour=12
    )
def task1():
    
    with scheduler.app.app_context():
        print("DAILY")
        for user in db.session.query(User).join(Search).filter(Search.frequency=="daily").all():
            print("searching" + user.first_name)
            for search in db.session.query(Search).filter(and_(Search.user_id==user.id,Search.frequency=="daily")):
                emailNewDB(search = search,user = user)
                
@scheduler.task(
    trigger="cron",
    id='Semiweekly Email',
    day_of_week='mon,thu',
    hour=8
    )
def task1():
    
    with scheduler.app.app_context():
        print("semiweekly")
        for user in db.session.query(User).join(Search).filter(Search.frequency=="semiweekly").all():
            print("searching" + user.first_name)
            for search in db.session.query(Search).filter(and_(Search.user_id==user.id,Search.frequency=="semiweekly")):
                emailNewDB(search = search,user = user)

@scheduler.task(
    trigger="cron",
    id='Weekly Email',
    day_of_week='mon',
    hour=8
    )
def task1():
    
    with scheduler.app.app_context():
        print("weekly")
        for user in db.session.query(User).join(Search).filter(Search.frequency=="weekly").all():
            print("searching" + user.first_name)
            for search in db.session.query(Search).filter(and_(Search.user_id==user.id,Search.frequency=="weekly")):
                emailNewDB(search = search, user = user)
            
               
               