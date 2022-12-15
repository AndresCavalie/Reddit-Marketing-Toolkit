#RMT : REDDIT MARKETING TOOLKIT
#this function is the api that connects to reddits servers
#takes a comma separated list of subreddits with no spaces , a comma separated list of keywords, and how far back you want to search in epoch 
#timesince = 1.21e+6 --> 1.21e+6 = two weeks, so this would search in the past two weeks
def search(subreddits,keywords,timesince):
    import pandas as pd

    import time
    import datetime
    
    import requests
    from dotenv import load_dotenv, find_dotenv
    import os
    load_dotenv(find_dotenv())
    
    RMT_CLIENT_ID = os.getenv('RMT_CLIENT_ID')
    RMT_SECRET_KEY = os.getenv('RMT_SECRET_KEY')
    
    REDDIT_USER = os.getenv('REDDIT_USER')
    REDDIT_PWD = os.getenv('REDDIT_PWD')
    
    auth = requests.auth.HTTPBasicAuth(RMT_CLIENT_ID, RMT_SECRET_KEY)

    data = {
        'grant_type': 'password',
        'username': f'{REDDIT_USER}',
        'password': f'{REDDIT_PWD}'
    }

    headers = {'User-Agent': 'MarketingToolkit'} 

    req = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth,
                        data=data,
                        headers=headers
                        )

    TOKEN = req.json()['access_token']

    headers['Authorization'] = f'bearer {TOKEN}'
    df = pd.DataFrame()


    for subreddit in subreddits:
        print("searching"+subreddit)
        time.sleep(2.4)
        output = requests.get('https://oauth.reddit.com/r/'+subreddit+'/new', headers=headers , params={'limit':'100'})
        inrange = True
        while(inrange==True):
            for post in output.json()['data']['children']:
                if time.time() - post['data']['created_utc'] < timesince:
                    inrange = True
                   
                    finalkeywords = ""
                    count = 0
                    for keyword in keywords:
                        
                        date = datetime.datetime.fromtimestamp(post['data']['created_utc'])
                        date = date.strftime( "%m/%d/%Y  %H:%M")
                        postcontent = post['data']['title']+" "+ post['data']['selftext']
                        postcontent = str(postcontent).lower()
                        keyword = keyword.lower()
                        
                        
                        if keyword in postcontent:
                            if count==0:
                                finalkeywords = keyword
                            else:
                                finalkeywords = finalkeywords + ", " + keyword 
                            count += 1
                    if count > 0:
                        df.loc[len(df), ['title','selftext','date','realdate','keyword','subreddit', 'permalink']] = post['data']['title'], post['data']['selftext'], date, post['data']['created_utc'],finalkeywords,subreddit,post['data']['permalink']    
            inrange=False
    if len(df)>0:
        print(df)
        df = df.sort_values(by=['realdate'], ascending=False)
        df = df[:10]
        df = df.reset_index(drop=True)
    return(df)
    


# if __name__ == '__main__':
#     search()

    




