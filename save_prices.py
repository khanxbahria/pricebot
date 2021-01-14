import csv
import time
import unicodedata

from selfbot import SelfBot
from settings import Settings

sb = SelfBot()


settings = Settings()


def find_item_price(msg):
    nums = '1234567890'

    msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode().strip()



    msg = msg.replace('*',' ')
    msg = msg.replace('_',' ')
    msg = msg.replace('~', ' ')    
    msg = msg.replace('-', ' ')
    msg = msg.replace('>', ' ')
    msg = msg.replace('<', ' ')
    msg = msg.replace('!', ' ')
    msg = msg.replace(',', ' ')

    msg = msg.replace('usd', '$')
    msg = msg.replace('USD', '$')
    words = msg.split()
    msg = ' '.join(words)

    msg = max(msg.split("#"), key=len)


    parts = msg.split(':')
    for i in range(1,len(parts),2):
        part = parts[i]
        if i!=len(parts)-1 and '$' not in part and not ' ' in part:
            parts[i] = ''
    msg = ''.join(parts)

    words = msg.split()
    for word in words:
        if 'sold' == word.lower():
            return '', ''
    for i in range(len(words)):
        word = words[i]
        if '$' in word and len(word)>1:
            price = word
            break
    else:
        num_words = []
        for i in range(len(words)):
            word = words[i]
            if any(num in word for num in nums) and not 'x' in word and not len(word)>4:
                num_words.append((word,i))
        if not num_words:
            return '', ''
        else:
            price, i = sorted(num_words, key=lambda k: k[0], reverse=True)[0]
    price=price.strip()
    if not any(num in price for num in nums):
        price= 99999999
    else:
        price = price.replace('$','')
        try:
            price = float(price)
        except:
            price = 99999999

    # english_chars = 'abcdefghijklmnopqrstuvwxyz)'
    # word = words[i-1]
    # if any(english_char in word.lower() for english_char in english_chars):
    #     item = " ".join(words[:i])
    # else:
    #     item = " ".join(words[:i-1])

    # if not item:
    #     return None,None
    # for j in reversed(range(len(item))):
    #     if item[j].lower() in english_chars or item[j] in nums:
    #         break
    # item = item[:j+1]

    # for j in range(len(item)):
    #     if item[j].lower() in english_chars or item[j] in nums:
    #         break
    # item = item[j:]
    # item += " " + " ".join(words[i+1:])
    # if item.lower().endswith('for'):
    #     item = item[:-3]
    # if not item:
    #     return None,None

    item = msg



    return item, price

# msg_jsons=[{'id':234,'content':'asds'},{'id':67,'content':'asds'}]

def parse_msg_jsons(msg_jsons):
    # new_msg_jsons = []
    # for msg_json in msg_jsons:
    #     if not any(new_msg_json['content'] == msg_json['content'] for new_msg_json in new_msg_jsons):
    #         new_msg_jsons.append(msg_json)
    # msg_jsons = new_msg_jsons

    price_dicts = []
    for msg_json in msg_jsons:
        price_dict = {}
        timestamp = msg_json['edited_timestamp'] or msg_json['timestamp']
        price_dict['time'] = timestamp[:-13]
        price_dict['channel_id'] = msg_json['channel_id']
        price_dict['msg_id'] = msg_json['id']
        author_dict = msg_json['author']
        price_dict['seller_tag'] = author_dict['username']+'#'+author_dict['discriminator']
        try:
            price_dict['seller_avipart'] = author_dict['id']+'/'+author_dict['avatar']
        except TypeError:
            price_dict['seller_avipart'] = ''

        msg_content = msg_json['content']
        for line in msg_content.split("\n"):
            item,price = find_item_price(line)
            if not item:
                continue
            already_exists = False
            for x in price_dicts:
                if item == x.get('item') and price_dict['seller_tag'] == x.get('seller_tag') and x.get('price') == price:
                    if x['time'] < price_dict['time']:
                        x['time'] = price_dict['time']
                    already_exists = True
                    break
            if not already_exists:
                price_dict = price_dict.copy()
                price_dict['item'] = item
                price_dict['price'] = price
            price_dicts.append(price_dict)
    return price_dicts




def main():
    msg_jsons = []
    for channel in settings.channels:
        channel_msg_jsons = sb.get_msgs(channel,limit=settings.messages_each)
        if len(channel_msg_jsons) < 10:
            print("ERROR",channel_msg_jsons,channel)
            continue
        for msg_json in channel_msg_jsons:
            msg_json['channel_id'] = channel
        msg_jsons += channel_msg_jsons
        time.sleep(1)

    price_dicts = parse_msg_jsons(msg_jsons)
    price_dicts = sorted(price_dicts, key=lambda k: k['time'], reverse=True) 


    with open('prices.csv', mode='w') as f:
        fieldnames = ['time', 'channel_id', 'msg_id', 'item', 'price', 'seller_tag','seller_avipart']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for price_dict in price_dicts:
            writer.writerow(price_dict)


if __name__ == '__main__':
    main()


# [{'id': '775508116275068929', 'type': 0, 'content': '**Quitting and selling EVERYTHING on my account.** Message me if interested in anything in the video. \n\n**Will also sell this entire inventory + a bunch of moles not pictured + gem storeboughts + 200+ extra rares on another account + 500 gems (through gifting) for 600 USD. In game MPA/coin value at least 3.8 billion, actual value most likely a lot more as there are a lot of uncommon smalls and newer items.** Note I will have to offer these onto your account using autoclicker instead of selling the account, as I do not want randoms knowing my emails If you cannot be patient/trusting that I will send everything over, I can screenshare with you while I offer. \n\nMessage if interested so I can provide updated contents as well; I only take Paypal FNF and have proof + have middlemanned for trusted sellers before!\n \nhttps://drive.google.com/file/d/1q_hlz8_B056hWkqA6k8LltXNVhkZ4bTp/view?usp=sharing', 'channel_id': '748301638397067395', 'author': {'id': '754061488351871027', 'username': '413x', 'avatar': '936845e6e38abe9942f005a561fad20f', 'discriminator': '7105', 'public_flags': 0}, 'attachments': [], 'embeds': [{'type': 'link', 'url': 'https://drive.google.com/file/d/1q_hlz8_B056hWkqA6k8LltXNVhkZ4bTp/view?usp=sharing', 'title': 'entire inventory; if interested ONLY MESSAGE 413x#7105 on Discord.mp4', 'provider': {'name': 'Google Drive', 'url': None}, 'thumbnail': {'url': 'https://lh5.googleusercontent.com/7HJZZaIz0geTLjepq4aK4x6RVbGBEFdFTrc-t6NVWNuMT4x0loWv6g0DygQ7hrQ=w1200-h630-p', 'proxy_url': 'https://images-ext-2.discordapp.net/external/M-nUA-Yn5ih6GdAe6edWltQag2PRRC_-2EYC3lIGhMg/https/lh5.googleusercontent.com/7HJZZaIz0geTLjepq4aK4x6RVbGBEFdFTrc-t6NVWNuMT4x0loWv6g0DygQ7hrQ%3Dw1200-h630-p', 'width': 1200, 'height': 630}}], 'mentions': [], 'mention_roles': [], 'pinned': False, 'mention_everyone': False, 'tts': False, 'timestamp': '2020-11-09T23:52:23.164000+00:00', 'edited_timestamp': None, 'flags': 0}]
