import curl_cffi
import json
from pathlib import Path
from dataclasses import dataclass
import typer


from loguru import logger

app = typer.Typer()


@dataclass
class JsonInfo:
    name: str
    url: str


url_map = {
    "index_perf": "https://www.csindex.com.cn/csindex-home/data-service/indexPerformance"
}
url = "https://www.csindex.com.cn/csindex-home/data-service/sector-change"


def get_a_json(data: JsonInfo):
    r = curl_cffi.get(data.url, impersonate="chrome")
    fn = Path(__file__).parent.parent / "src" / "assets" / (data.name + ".json")
    with open(fn, "w") as f:
        json.dump(r.json(), f, ensure_ascii=False, indent=4)

    logger.info(f"get json: {fn}")


@app.command()
def get_json(name: str):
    item = JsonInfo(name=name, url=url_map[name])
    get_a_json(item)


if __name__ == "__main__":
    app()
