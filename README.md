# QuizBot telegram/vk.com
The project makes a telegram/vk.com quiz bots.
Examples [Telegram bot](https://t.me/grandisima_bot) and [Vk.com bot](https://vk.com/im?media=&sel=-198053823)
)
## Description
With the code you can make quiz bots in telegram/vk.com.

The project uses:   
 * [Telegram](https://telegram.org)
 * [Vk.com](https://vk.com/)
  

## Requirements
Python >=3.7  
Registered bot on  [Telegram](https://t.me/botfather).  
Registered account and created public on [vk.com](https://vk.com/).  
Registered account and created database on [Redis](https://redislabs.com/).  

 
Create file '.env' and add the code:
```
TELEGRAM_TOKEN=your_telegram_token
REDIS_HOST=your_redis_host
REDIS_PASS=your_redis_database_password
VK_TOKEN=chat_token_vk
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Install requirements modules:
```
pip install -r requirements.txt	
```


Get key for vk bot: Create public -> Manage -> Api usage -> Create 'Access token'.



### How to use

Install requirements. 

Open and run 'tg_bot.py' or/and 'vk_bot.py'.
```
python tg_bot.py
python vk_bot.py
```

### Program example
![tg bot](https://dvmn.org/filer/canonical/1569215494/324/)

![vk bot](https://dvmn.org/filer/canonical/1569215498/325/)

## Project goal
The code was written for educational purpose on online course for Api developers [Devman](http://dvmn.org). 
