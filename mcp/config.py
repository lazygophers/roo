app_name = "lazygophers"

http_port = 14000

proxies = {"http": "http://127.0.0.1:7890", "https": "https://127.0.0.1:7890"}

searx_hosts = [
    "https://so.ddns-ip.net",
    "https://seek.nuer.cc",
    "https://sousuo.emoe.top",
    "https://searxng.ddaodan.cc",
    "https://ss.helper5210.top",
    "https://search.no-code.gdn",
    "https://search.corrently.cloud",
    "https://search.jakespeed.org",
    "https://searxng.fly2me.cc",
    "https://searxng.stardream.online",
    "https://search.lucathomas.de",
    "https://negativenull.com",
    "https://searx.yorgis.net",
    "https://searxng-pilot.jitera.app",
    "https://searxng.vyro.ai",
    "https://martechia.online",
    "https://s.gottsnack.net",
    "https://srx.zebralab.io",
    "https://search.nicolasallemand.com",
    "https://search.aidoing.de",
    "https://searxng.k3s.koski.co",
    "https://mfood3.hongquantrader.com",
    "https://searx.privhub.space",
    "https://search.muellers-software.org",
    "https://searxng.sbbz-ilvesheim.de",
    "https://searxng.core.sciling.com",
    "https://searxng.springbokagency.com",
    "https://seachx.lunarfire.home64.de",
]

import os
import appdirs

models_path = os.path.join(appdirs.user_config_dir(appname=app_name), "models")


for key in proxies:
    os.environ["{}_PROXY".format(key.upper())] = proxies[key]
os.environ["COQUI_TOS_AGREED"] = "1"
