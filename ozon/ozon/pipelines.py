import uuid
import pandas as pd


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SmartphoneOsPipeline:
    def process_item(self, item, spider):
        self.os_list.append(item)

    def open_spider(self, spider):
        self.os_list = []

    def close_spider(self, spider):
        df = pd.DataFrame(self.os_list)
        group_by_os = df.groupby("os_version", as_index=False)["os_version"].value_counts(dropna=False)
        group_by_os = group_by_os.sort_values(by=["count"], ascending=False)
        df_text = group_by_os.to_string(header=False, index=False)
        with open(f'ozon_smartphones_{uuid.uuid4().hex}.txt', "w") as f:
            f.write(df_text)
