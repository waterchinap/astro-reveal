from playwright.sync_api import sync_playwright
import json


def get_doc_arr():
    url = "https://channel.chinanews.com.cn/u/pic/news.shtml"
    output_file = "../src/assets/imgnews.json"

    with sync_playwright() as p:
        # 1. 启动 Chromium 浏览器 (无头模式，不显示浏览器窗口)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"正在访问 {url} ...")
        # 2. 访问页面
        page.goto(url)

        # 3. 等待页面加载完成，确保 JS 已执行
        # wait_for_load_state('networkidle') 会等待网络请求基本静止，比较稳妥
        page.wait_for_load_state("networkidle")
        print("页面加载完成。")

        # 4. 在浏览器上下文中执行 JS，直接获取全局变量 docArr
        # 这是最准确的方法，相当于在浏览器控制台输入 `docArr`
        try:
            doc_arr = page.evaluate("() => window.docArr")

            if doc_arr:
                print(f"成功提取！共获取到 {len(doc_arr)} 条新闻。")
                print("-" * 30)
                res = [{"title": d.get("title"), "img": d.get("img")} for d in doc_arr]
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(res, f, ensure_ascii=False, indent=2)
                # 打印第一条新闻的标题作为验证
                print("第一条新闻标题:", doc_arr[0]["title"])
                print("发布时间:", doc_arr[0]["pubtime"])
                return doc_arr
            else:
                print("错误：在页面中未找到 'docArr' 变量。")
                # 为了调试，我们可以打印出页面标题，确认是否访问了正确的页面
                print("当前页面标题为:", page.title())
                return None
        except Exception as e:
            print("执行 JavaScript 时出错:", e)
            return None
        finally:
            # 5. 关闭浏览器
            browser.close()


if __name__ == "__main__":
    get_doc_arr()
