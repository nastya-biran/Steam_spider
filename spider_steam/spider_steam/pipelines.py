# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import re


class SpiderSteamPipeline:
    def open_spider(self, spider):
        self.file = open("items.json", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        year = re.search(r'\d{4}', item['release_date'])[0]
        print(year)
        if year >= "2000":
            line = json.dumps(ItemAdapter(item).asdict()) + '\n'
            self.file.write(line)
        return item
