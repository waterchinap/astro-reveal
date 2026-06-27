import akshare as ak
import pandas as pd
from loguru import logger

emnews = ak.stock_info_global_em()
emnews.to_json('../src/assets/emnews.json', force_ascii=False)
logger.info('json saved')


