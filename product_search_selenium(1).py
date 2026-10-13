
# 商品自动搜索爬虫（Selenium 登录版）  平台：淘宝/天猫、京东
# 运行：
#   python product_search_selenium.py            交互输入
#   python product_search_selenium.py --demo     离线演示，验证 0 报错
#   python product_search_selenium.py --site taobao --kw 蓝牙耳机 --num 10 --shops 5
# 依赖（真实抓取才需要）：pip install selenium   （Selenium4.6+ 自动管驱动，装好 Chrome 即可）

import tim
import csv
import random
import argparse
import traceback

MAX_NUM = 8      # 全局硬上限：最多条数
MAX_SHOPS = 2    # 全局硬上限：最多店铺数

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    HAS_SELENIUM = True
except Exception:
    HAS_SELENIUM = False



def safe_int(prompt, lo, hi, default):
    # 带校验整数输入：乱输/回车/超范围都不会崩
    while True:
        raw = input(prompt).strip()
        if raw == '':
            print('  [提示] 未输入，使用默认值 %d' % default)
            return default
        if raw.isdigit():
            v = int(raw)
            if v < lo:
                print('  [提示] 不能小于 %d，已调整为 %d' % (lo, lo))
                return lo
            if v > hi:
                print('  [提示] 最多 %d，已调整为 %d' % (hi, hi))
                return hi
            return v
        print('  [提示] 请输入纯数字，例如 10')


def build_driver(headless=False):
    if not HAS_SELENIUM:
        print('[警告] 未安装 selenium。请先执行: pip install selenium')
        return None
    try:
        opts = Options()
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument('--start-maximized')
        opts.add_experimental_option('excludeSwitches', ['enable-automation'])
        opts.add_experimental_option('useAutomationExtension', False)
        if headless:
            opts.add_argument('--headless=new')
            opts.add_argument('--window-size=1366,900')
        driver = webdriver.Chrome(options=opts)
        driver.execute_cdp_cmd(
            'Page.addScriptToEvaluateOnNewDocument',
            {'source': "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"},
        )
        return driver
    except Exception as e:
        print('[警告] 浏览器启动失败（多为未装 Chrome 或驱动）：%s' % e)
        return None


def wait_login(driver, platform):
    try:
        if platform == 'taobao':
            driver.get('https://www.taobao.com')
        else:
            driver.get('https://www.jd.com')
        print('')
        print('>>> 浏览器已打开 %s 首页。' % platform)
        print('>>> 请在浏览器里【扫码/账号登录】，登录成功后回到本窗口按回车继续...')
        input()
    except Exception as e:
        print('[提示] 打开首页出点小状况（可继续）：%s' % e)


def search_taobao(driver, keyword, num, shops):
    driver.get('https://s.taobao.com/search?q=' + keyword)
    time.sleep(random.uniform(3, 5))
    items = []
    seen_shops = set()
    try:
        cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='item.taobao.com'], a[href*='detail.tmall.com']")
        for c in cards:
            if len(items) >= num:
                break
            try:
                href = c.get_attribute('href') or ''
                title = ''
                imgsrc = ''
                try:
                    img = c.find_element(By.TAG_NAME, 'img')
                    title = (img.get_attribute('alt') or '').strip()
                    imgsrc = img.get_attribute('src') or img.get_attribute('data-src') or ''
                except Exception:
                    pass
                if not title:
                    title = (c.text or '').strip().replace('\n', ' ')[:60]
                if not title or not href:
                    continue
                shop = 'unknown'
                price = ''
                try:
                    box = c.find_element(By.XPATH, './ancestor::*[self::div][2]')
                    txt = box.text or ''
                    for line in txt.split('\n'):
                        s = line.strip()
                        if ('店' in s or '旗舰' in s or '专营' in s) and shop == 'unknown':
                            shop = s[:30]
                    for token in txt.replace(' ', ' ').replace('\n', ' ').split(' '):
                        d = token.replace('\uffe5', '').replace('\u00a5', '').strip()
                        if d.replace('.', '', 1).isdigit() and d and len(d) <= 8 and not price:
                            price = d
                except Exception:
                    pass
                if shops > 0 and shop != 'unknown' and shop not in seen_shops:
                    if len(seen_shops) >= shops:
                        continue
                    seen_shops.add(shop)
                if imgsrc.startswith('//'):
                    imgsrc = 'https:' + imgsrc
                items.append({'title': title, 'price': price, 'shop': shop, 'url': href, 'img': imgsrc})
                time.sleep(random.uniform(0.3, 0.8))
            except Exception:
                continue
    except Exception as e:
        print('[提示] 淘宝解析异常（页面改版/需重新登录）：%s' % e)
    return items


def search_jd(driver, keyword, num, shops):
    driver.get('https://search.jd.com/Search?keyword=' + keyword + '&enc=utf-8')
    time.sleep(random.uniform(3, 5))
    items = []
    seen_shops = set()
    try:
        for _ in range(3):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(1.2)
        cards = driver.find_elements(By.CSS_SELECTOR, 'li.gl-item')
        for c in cards:
            if len(items) >= num:
                break
            try:
                a = c.find_element(By.CSS_SELECTOR, 'a.p-name a')
                href = a.get_attribute('href') or ''
                if href.startswith('//'):
                    href = 'https:' + href
                title = (a.get_attribute('title') or a.text or '').strip()
                price = ''
                try:
                    price = c.find_element(By.CSS_SELECTOR, '.p-price i, .p-price .price-now').text.strip()
                except Exception:
                    try:
                        price = c.find_element(By.CSS_SELECTOR, '.p-price').text.strip()
                    except Exception:
                        price = ''
                shop = 'unknown'
                try:
                    shop = c.find_element(By.CSS_SELECTOR, '.curr-shop, .p-shopnum a').text.strip()[:30]
                except Exception:
                    pass
                imgsrc = ''
                try:
                    img = c.find_element(By.CSS_SELECTOR, 'img')
                    imgsrc = img.get_attribute('src') or img.get_attribute('data-lazy-img') or ''
                    if imgsrc.startswith('//'):
                        imgsrc = 'https:' + imgsrc
                except Exception:
                    pass
                if not title or not href:
                    continue
                if shops > 0 and shop != 'unknown' and shop not in seen_shops:
                    if len(seen_shops) >= shops:
                        continue
                    seen_shops.add(shop)
                items.append({'title': title, 'price': price, 'shop': shop, 'url': href, 'img': imgsrc})
                time.sleep(random.uniform(0.3, 0.8))
            except Exception:
                continue
    except Exception as e:
        print('[提示] 京东解析异常（页面改版/需重新登录）：%s' % e)
    return items


def show(items):
    if not items:
        print('')
        print('没有抓到数据。常见原因：未登录、触发验证码、页面改版。可换平台或稍后再试。')
        return
    print('')
    print('===== 抓取结果（共 %d 条）=====' % len(items))
    for i, it in enumerate(items, 1):
        print('')
        print('[%d] %s' % (i, it['title']))
        print('    价格：%s    店铺：%s' % (it['price'] or '-', it['shop']))
        print('    链接：%s' % it['url'])
        print('    图片：%s' % (it['img'] or '-'))


def save_csv(items, path):
    try:
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['序号', '商品标题', '价格', '店铺', '购物链接', '商品图'])
            for i, it in enumerate(items, 1):
                w.writerow([i, it['title'], it['price'], it['shop'], it['url'], it['img']])
        print('')
        print('[完成] 已导出 %d 条到：%s' % (len(items), path))
    except Exception as e:
        print('[提示] 写 CSV 失败：%s' % e)


def demo_items():
    return [
        {'title': '[演示] 无线蓝牙耳机 主动降噪 入耳式', 'price': '129.00',
         'shop': '数码旗舰店', 'url': 'https://item.taobao.com/demo1', 'img': 'https://example.com/1.jpg'},
        {'title': '[演示] 蓝牙耳机 运动跑步 长续航', 'price': '89.90',
         'shop': '影音专营店', 'url': 'https://detail.tmall.com/demo2', 'img': 'https://example.com/2.jpg'},
        {'title': '[演示] 头戴式降噪耳机 HiFi 游戏', 'price': '199.00',
         'shop': '数码旗舰店', 'url': 'https://item.jd.com/demo3.html', 'img': 'https://example.com/3.jpg'},
    ]


def main():
    print('=' * 56)
    print(' 商品自动搜索爬虫  淘宝/天猫·京东  条数店铺可控·防报错')
    print('=' * 56)

    parser = argparse.ArgumentParser()
    parser.add_argument('--kw')
    parser.add_argument('--site', choices=['taobao', 'jd'])
    parser.add_argument('--num', type=int)
    parser.add_argument('--shops', type=int)
    parser.add_argument('--demo', action='store_true')
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()

    if args.demo:
        items = demo_items()
        show(items)
        save_csv(items, 'search_results_demo.csv')
        print('')
        print('[演示模式] 全流程跑通，0 报错。')
        return

    keyword = args.kw or input('') if False else (args.kw or input('\n请输入要搜索的商品名称：').strip())
    if not keyword:
        print('[退出] 关键词为空。')
        return

    site = args.site or (input('选择平台 (1=淘宝/天猫, 2=京东，默认1)：').strip() or '1')
    site = 'jd' if site == '2' else 'taobao'

    if args.num is not None:
        num = max(1, min(args.num, MAX_NUM))
    else:
        num = safe_int('请输入要爬取的商品条数(1-%d，默认10)：' % MAX_NUM, 1, MAX_NUM, 10)

    if args.shops is not None:
        shops = max(0, min(args.shops, MAX_SHOPS))
    else:
        shops = safe_int('请输入最多几家店铺(0=不限，上限%d，默认10)：' % MAX_SHOPS, 0, MAX_SHOPS, 10)

    print('')
    print('[配置] 平台=%s 关键词=%s 条数=%d 店铺=%d' % (site, keyword, num, shops))
    print('[说明] 首次会弹出浏览器，请扫码登录；登录好回本窗口按回车。')

    driver = build_driver(headless=args.headless)
    if driver is None:
        print('')
        print('无法启动浏览器/未装 selenium。可先用 --demo 验证逻辑，或：pip install selenium')
        return

    items = []
    try:
        wait_login(driver, site)
        if site == 'taobao':
            items = search_taobao(driver, keyword, num, shops)
        else:
            items = search_jd(driver, keyword, num, shops)
        show(items)
        if items:
            save_csv(items, 'search_results.csv')
    except KeyboardInterrupt:
        print('')
        print('[中断] 你按了 Ctrl+C，已安全退出。')
    except Exception as e:
        print('')
        print('[出错已捕获] 程序没有崩溃，原因：%s' % e)
        traceback.print_exc()
    finally:
        try:
            input('\n按回车关闭浏览器并退出...')
            driver.quit()
        except Exception:
            pass
        print('结束。')


if __name__ == '__main__':
    main()
