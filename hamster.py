import asyncio
import httpx
import pytz
from datetime import datetime
from loguru import logger
import random
import time
import requests

API_TOKEN = '7451901357:AAGLeTL7hBU7onSvpzf87U9rcvCW1XN1haE'
CHAT_ID = -1002182785912
TELEGRAM_API_URL = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"

class TrainMiner:
    app_token = "82647f43-3f87-402d-88dd-09a90025313f"
    promo_id = "c4480ac7-e178-4973-8061-9ed5b2e17954"

class ChainKey:
    app_token = "d1690a07-3780-4068-810f-9b5bbf2931b2"
    promo_id = "b4170868-cef0-424f-8eb9-be0622e8e8e3"

class CloneKey:
    app_token = "74ee0b5b-775e-4bee-974f-63e7f4d5bacb"
    promo_id = "fe693b26-b342-4159-8808-15e3ff7f8767"

class BikeKey:
    app_token = "d28721be-fd2d-4b45-869e-9f253b554e50"
    promo_id = "43e35910-c168-4634-ad4f-52fd764a843f"

async def generate_promo_code(app_token, promo_id):
    logger.info("Starting generate promocode!")
    try:
        client_token = await login_client(app_token)
        await register_event(client_token, promo_id)
        promo_code = await create_code(client_token, promo_id)
        logger.success(f"Promocode: {promo_code} generated successfully.")
        return promo_code
    except Exception as error:
        logger.error(error)
        return None

async def login_client(app_token):
    logger.info("Login client...")
    client_id = f"{int(time.time())}-{random.randint(0, 999999999999999999)}"
    async with httpx.AsyncClient() as client:
        response = await client.post('https://api.gamepromo.io/promo/login-client', json={
            'appToken': app_token,
            'clientId': client_id,
            'clientOrigin': 'deviceid'
        })
        data = response.json()
        return data['clientToken']

async def register_event(client_token, promo_id):
    logger.info("Register event...")
    event_id = ''.join(random.choice('0123456789abcdef') if c == 'x' else '89ab'[random.randint(0, 3)] for c in 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx')
    async with httpx.AsyncClient() as client:
        response = await client.post('https://api.gamepromo.io/promo/register-event', json={
            'promoId': promo_id,
            'eventId': event_id,
            'eventOrigin': 'undefined'
        }, headers={'Authorization': f'Bearer {client_token}'})
        data = response.json()
        if not data.get('hasCode'):
            await asyncio.sleep(20)
            await register_event(client_token, promo_id)

async def create_code(client_token, promo_id):
    logger.info("Creating code....")
    async with httpx.AsyncClient() as client:
        response = await client.post('https://api.gamepromo.io/promo/create-code', json={
            'promoId': promo_id
        }, headers={'Authorization': f'Bearer {client_token}'})
        data = response.json()
        return data['promoCode']

async def send_promo_codes():
    while True:
        for key_class in [TrainMiner, BikeKey, ChainKey, CloneKey]:
            promo_code = None
            retries = 10  # Maksimal urinishlar soni
            
            for _ in range(retries):
                start = datetime.now(pytz.timezone("Asia/Tashkent"))
                promo_code = await generate_promo_code(key_class.app_token, key_class.promo_id)
                if promo_code:
                    end = datetime.now(pytz.timezone("Asia/Tashkent"))
                    duration = (end - start).seconds
                    
                    message = (
                        f"<blockquote><b>=============================\n"
                        f"🆕 New {key_class.__name__} Key‼️\n\n"
                        f"🔑 : <code>{promo_code}</code>\n"
                        f"⏱ Generated in {duration} seconds\n🖇️ Tags: #{key_class.__name__}\n"
                        f"=============================</b></blockquote>"
                    )
                    
                    send_message(message)
                    break  # Kod muvaffaqiyatli yaratildi, for siklidan chiqish
                else:
                    await asyncio.sleep(3)  # 5 soniya kutish va qayta urinish

            if promo_code is None:
                logger.error(f"{key_class.__name__} uchun promo kodni yaratib bo'lmadi.")

def send_message(message):
    try:
        response = requests.post(TELEGRAM_API_URL, json={
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'html'
        })
        response.raise_for_status()
        logger.success(f"Message sent successfully: {message}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message: {e}")

if __name__ == '__main__':
    logger.add("promocode_log.log", rotation="100 MB")
    asyncio.run(send_promo_codes())