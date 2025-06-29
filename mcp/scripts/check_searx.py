from tqdm import tqdm
from langchain.utilities import SearxSearchWrapper


host_list = [
    "https://so.ddns-ip.net",
    "https://seek.nuer.cc",
    "https://sousuo.emoe.top",
    "https://searxng.ctbot.tech",
    "https://searxng.jethrowang.cn",
    "https://aimonitor.xiaocg.xyz",
    "https://search.fatgpt.cn",
    "https://searxng.narasaka.dev",
    "https://search.songai.icu",
    "https://searxng.ddaodan.cc",
    "https://sg.goyor.com",
    "https://search.infinityf4p.com",
    "https://s.yyy.earth",
    "https://ss.helper5210.top",
    "https://search.no-code.gdn",
    "https://search.corrently.cloud",
    "https://search.jakespeed.org",
    "https://searxng.fly2me.cc",
    "https://searxng.stardream.online",
    "https://search.lucathomas.de",
    "https://negativenull.com",
    "https://searx.yorgis.net",
    "https://search.mixel.cloud",
    "https://xng.huidaolasa.xyz",
    "https://searxng-pilot.jitera.app",
    "https://searxng.vyro.ai",
    "https://martechia.online",
    "https://search.chgr.cc",
    "https://websearch.nwt.de",
    "https://s.arson.pw",
    "https://s.gottsnack.net",
    "https://srx.zebralab.io",
    "https://search.the8.dev",
    "https://search.nicolasallemand.com",
    "https://search.aidoing.de",
    "https://search.f-ws.net",
    "https://searxng.ai.flagbit.de",
    "https://searxng.asudox.dev",
    "https://searxng.k3s.koski.co",
    "https://mfood3.hongquantrader.com",
    "https://searx.privhub.space",
    "https://search.muellers-software.org",
    "https://searxng.lmdr.io",
    "https://uwg8swww0o0cw4osg4okc4gs.phytertek.com",
    "https://searxng.sbbz-ilvesheim.de",
    "https://search.soulrend.net",
    "https://searxng.core.sciling.com",
    "https://searxng.springbokagency.com",
    "https://seachx.lunarfire.home64.de",
    "https://cari.aeenquran.id",
]

alive_list = []

for host in tqdm(host_list, desc="Checking searx hosts"):
    try:
        search = SearxSearchWrapper(searx_host=host)
        if len(search.results("你是谁", num_results=10)) > 0:
            alive_list.append(host)
    except:
        pass


print(alive_list)