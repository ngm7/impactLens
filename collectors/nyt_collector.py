"The NYT collector of everyday's articles"
import logging
import os
import configparser
import requests
import pyjq
import asyncio
from newspaper import Article
import datetime
import attr

from collectors.collector import Collector
from commons.datamodel import DataModel
from attr import attrib

logger = logging.getLogger(__name__)

NYT_SECTION = "NYT"


@attr.s
class NytCollector(Collector):
    key = attrib(default="")
    url = attrib(default="")
    datapath = attrib(default=".")
    last_refresh = attrib(default=datetime.datetime.now())

    def run(self, loop):
        asyncio.set_event_loop(loop)
        logger.info(f"current loop time: {loop.time()}. Scheduling data gathering callback for {self.frequency}")
        loop.call_soon(self.gather_data, loop)
        try:
            loop.run_forever()
        finally:
            loop.close()

    def build_config(self, config_file="./config/prod.ini"):
        cparser = configparser.ConfigParser()
        cparser.read(config_file)

        for section in cparser.sections():
            if section == NYT_SECTION:
                self.key = cparser[section]['key']
                self.url = cparser[section].get('url')
                self.datapath = cparser[section]['datapath']
                self.frequency = int(cparser[section]['frequency'])
                self.download_fresh = cparser[section].getboolean('download_fresh')
                break
        logger.info(f"Loaded configuration for NYT collector: {self}")

    def gather_data(self, loop):
        dataArr = []
        logger.info(f"Entering gather_data. download_fresh: {self.download_fresh}")
        if not self.download_fresh:
            logger.info(f"Current time is: {datetime.datetime.now().strftime('%c')}")
            logger.info("Building Dataset Building test dataset from NYT's archive of 12/2018.")
            logger.info(f"Loading articles from f{self.datapath}")
            files = os.listdir(self.datapath)
            files = [os.path.join(self.datapath, f) for f in files]
            files.sort(key=lambda x: os.path.getmtime(x))
            for i, file in enumerate(files):
                with open(file, "r") as f:
                    dataArr.append(f.read())
                    if len(dataArr[i]) > 10:
                        self.data.id.append(dataArr[i][0:100])  # first hundred characters of the file are the ID
                    else:
                        self.data.id.append(f'NA-article {i}')
            self.last_refresh = datetime.datetime.now()
            self.data.id = []
            self.data.setDocuments(dataArr)
            loop.call_later(self.frequency, self.gather_data, loop)
        else:
            logger.info(f"Current time is: {datetime.datetime.now().strftime('%c')}")
            logger.info("Building Dataset from NYT's archive of 12/2018. Downloading ...")

            url = self.url + "?&api-key=" + self.key
            logger.info(f"url: {url}")
            r = requests.get(url)
            logger.info(f"Downloaded {len(r.text)} bytes of data")
            json_data = r.json()

            url_jq = f".response .docs [] | .web_url"
            url_out = pyjq.all(url_jq, json_data)

            headline_jq = f".response .docs [] | .headline .main"
            headline_out = pyjq.all(headline_jq, json_data)

            # some URLs are empty, clean up
            self.last_refresh = datetime.datetime.now()
            self.data.id = headline_out
            self.build_datamodel(id=url_out, metadata=headline_out)
            loop.call_later(self.frequency, self.gather_data, loop)

    def build_datamodel(self, id, metadata) -> DataModel:
        """build datamodel for each Collector's collected data"""
        count = 0
        dataArr = []

        logger.info(f"Attempting to download articles from individual links")
        for i, url in enumerate(id):
            if count > 100:  # if you don't want to download 6200 articles
                break
            if not url:
                continue
            a = Article(url=url)
            try:
                a.download()
                a.parse()
            except Exception as ex:
                logger.error(f"caught {ex} continuing")
            if len(a.text):
                logger.info(f"{len(dataArr)} - downloaded {len(a.text)} bytes")
                dataArr.append(a.text)
                self.data.id.append(id[i])
                self.data.meta.append(metadata[i])
                with open(self.datapath + "/" + f"{count}.txt", "w") as f:
                    f.write(a.text)
                count += 1

        logger.info(f"working with {len(dataArr)} articles")
        self.data.setDocuments(dataArr)

