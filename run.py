# -*- coding: utf-8 -*-

import os
import logging
from colorama import Fore
from pymongo import MongoClient
from dotenv import load_dotenv

from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.Webhook import Webhook
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.classes.Matrix import Matrix
from TwitchChannelPointsMiner.classes.Pushover import Pushover
from TwitchChannelPointsMiner.classes.Gotify import Gotify
from TwitchChannelPointsMiner.classes.Settings import Priority, Events, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings

load_dotenv()

twitch_miner = TwitchChannelPointsMiner(
    username=os.getenv('TWITCH_USERNAME', ''),                  
    password=os.getenv('TWITCH_PASSWORD', ''),                  
    claim_drops_startup=False,                                  
    priority=[                                                  
        Priority.STREAK,                                        
        Priority.DROPS,                                         
        Priority.ORDER                                          
    ],
    enable_analytics=False,                                     
    disable_ssl_cert_verification=False,                        
    disable_at_in_nickname=False,                               
    logger_settings=LoggerSettings(
        save=True,                                              
        console_level=logging.INFO,                             
        console_username=False,                                 
        auto_clear=True,                                        
        time_zone="",                                           
        file_level=logging.DEBUG,                               
        emoji=True,                                             
        less=False,                                             
        colored=True,                                           
        color_palette=ColorPalette(                             
            STREAMER_online="GREEN",                            
            streamer_offline="red",                             
            BET_wiN=Fore.MAGENTA                                
        ),
        telegram=Telegram(
            chat_id=123456789,
            token="123456789:shfuihreuifheuifhiu34578347",
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, Events.BET_LOSE, Events.CHAT_MENTION],
            disable_notification=True,
        ),
        discord=Discord(
            webhook_api="https://discord.com/api/webhooks/0123456789/0a1B2c3D4e5F6g7H8i9J",
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, Events.BET_LOSE, Events.CHAT_MENTION],
        ),
        webhook=Webhook(
            endpoint="https://example.com/webhook",
            method="GET",
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, Events.BET_LOSE, Events.CHAT_MENTION],
        ),
        matrix=Matrix(
            username="twitch_miner",
            password="...",
            homeserver="matrix.org",
            room_id="...",
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, Events.BET_LOSE],
        ),
        pushover=Pushover(
            userkey="YOUR-ACCOUNT-TOKEN",
            token="YOUR-APPLICATION-TOKEN",
            priority=0,
            sound="pushover",
            events=[Events.CHAT_MENTION, Events.DROP_CLAIM],
        ),
        gotify=Gotify(
            endpoint="https://example.com/message?token=TOKEN",
            priority=8,
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, Events.BET_LOSE, Events.CHAT_MENTION], 
        )
    ),
    streamer_settings=StreamerSettings(
        make_predictions=True,
        follow_raid=True,
        claim_drops=True,
        claim_moments=True,
        watch_streak=True,
        community_goals=False,
        chat=ChatPresence.ONLINE,
        bet=BetSettings(
            strategy=Strategy.SMART,
            percentage=5,
            percentage_gap=20,
            max_points=50000,
            stealth_mode=True,
            delay_mode=DelayMode.FROM_END,
            delay=6,
            minimum_points=20000,
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,
                where=Condition.LTE,
                value=800
            )
        )
    )
)

streamers_list = [
    Streamer("streamer-username01", settings=StreamerSettings(make_predictions=True  , follow_raid=False , claim_drops=True  , watch_streak=True , community_goals=False , bet=BetSettings(strategy=Strategy.SMART      , percentage=5 , stealth_mode=True,  percentage_gap=20 , max_points=234   , filter_condition=FilterCondition(by=OutcomeKeys.TOTAL_USERS,      where=Condition.LTE, value=800 ) ) )),
    Streamer("streamer-username02", settings=StreamerSettings(make_predictions=False , follow_raid=True  , claim_drops=False ,                                            bet=BetSettings(strategy=Strategy.PERCENTAGE , percentage=5 , stealth_mode=False, percentage_gap=20 , max_points=1234  , filter_condition=FilterCondition(by=OutcomeKeys.TOTAL_POINTS,     where=Condition.GTE, value=250 ) ) )),
    Streamer("streamer-username03", settings=StreamerSettings(make_predictions=True  , follow_raid=False ,                     watch_streak=True , community_goals=True  , bet=BetSettings(strategy=Strategy.SMART      , percentage=5 , stealth_mode=False, percentage_gap=30 , max_points=50000 , filter_condition=FilterCondition(by=OutcomeKeys.ODDS,             where=Condition.LT,  value=300 ) ) )),
    Streamer("streamer-username04", settings=StreamerSettings(make_predictions=False , follow_raid=True  ,                     watch_streak=True ,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      )),
    Streamer("streamer-username05", settings=StreamerSettings(make_predictions=True  , follow_raid=True  , claim_drops=True ,  watch_streak=True , community_goals=True  , bet=BetSettings(strategy=Strategy.HIGH_ODDS  , percentage=7 , stealth_mode=True,  percentage_gap=20 , max_points=90    , filter_condition=FilterCondition(by=OutcomeKeys.PERCENTAGE_USERS, where=Condition.GTE, value=300 ) ) )),
    Streamer("streamer-username06"),
    Streamer("streamer-username07"),
    Streamer("streamer-username08"),
    "streamer-username09",
    "streamer-username10",
    "streamer-username11"
]

client = MongoClient(os.getenv('MONGO_URI', 'mongodb://mongodb:27017/'))
db = client['twitch_miner_web']
twitch_data_collection = db['twitch_data']

for streamer in streamers_list:
    channel_name = streamer.username if isinstance(streamer, Streamer) else streamer
    if not twitch_data_collection.find_one({"channel_name": channel_name}):
        twitch_data_collection.insert_one({
            "channel_name": channel_name,
            "history": [0]
        })

twitch_miner.mine(
    streamers_list,
    followers=False,
    followers_order=FollowersOrder.ASC
)
