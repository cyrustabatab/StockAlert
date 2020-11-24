import requests,os,pyperclip,json,datetime as dt
import time
from twilio.rest import Client



def send_message(stock,topic,pct_change,title=None,description=None):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    
    client = Client(account_sid, auth_token)
    pct_change = round(pct_change,2)
    emoji = u'\U0001F53A' if pct_change > 0 else u'\U0001F53B'
    message = client.messages \
                    .create(
                            body=f"{topic} {emoji} {pct_change}%" + ((f"\nHEADLINE: {title}\nBrief: {description}") if title is not None else ''),
                         from_=os.environ.get('FROM_PHONE'), # replace with twilio phone number
                         to=os.environ.get('TO_PHONE')# replace with phone number
                     )

    print(message.status)

def get_news(stock,topic,pct_change):

    url = 'http://newsapi.org/v2/top-headlines'

    params = {'q': topic,'apiKey': os.environ.get("NEWS_API_KEY"),'language': 'en'}

    response = requests.get(url,params=params)
    
    data = response.json()
    articles = data['articles']
    top_three_articles = articles[:3]
    
    if top_three_articles:
        for article in top_three_articles:
            send_message(stock,topic,pct_change,article['title'],article['description'])
    else:
        send_message(stock,topic,pct_change)

    print(data)



STOCKS = ["TSLA","U","PLAY","AAPL","FB","MSFT","NFLX","SIX","FIT","AMC","SPOT","AMZN","EA","DIS","DKNG","SNAP"]
NAMES = ["TESLA","UNITY SOFTWARE","DAVE AND BUSTERS","APPLE","FACEBOOK","MICROSOFT","NETFLIX","SIX FLAGS","FITBIT","AMC","SPOTIFY","AMAZON","ELECTRONIC ARTS","DISNEY","DRAFTKINGS","SNAPCHAT"]


## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY') 

url = 'https://www.alphavantage.co/query'


for i,(STOCK,NAME) in enumerate(zip(STOCKS,NAMES)):
    params = {'function': 'TIME_SERIES_DAILY','symbol': STOCK,'apikey': ALPHA_VANTAGE_API_KEY,'outputsize':'compact'}
    
    print(STOCK,NAME)
    response = requests.get(url,params=params)

    data = response.json()
    pyperclip.copy(json.dumps(data))

    daily = data['Time Series (Daily)']

    now = dt.datetime.now()

    if now.weekday() not in (5,6):
        delta = 1
        if now.weekday() == 0:
            delta = 3

        yesterday= now - dt.timedelta(days=delta)

        now_string = now.strftime('%Y-%m-%d')
        yesterday_string = yesterday.strftime('%Y-%m-%d')
        now_string = "2020-11-23"
        yesterday_string = "2020-11-20"


        todays_price = float(daily[now_string]['4. close'])
        yesterdays_price= float(daily[yesterday_string]['4. close'])

        pct_change = ((todays_price - yesterdays_price) / yesterdays_price) * 100
        if abs(pct_change) >= 5:
            get_news(STOCK,NAME,pct_change)

    if (i + 1) % 5 == 0:
        time.sleep(60)









#pyperclip.copy(json.dumps(data))


#with open('test.csv','wb') as f:
#    f.write(response.content)





## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

