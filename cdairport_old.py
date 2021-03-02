from locale import atoi
from lxml import html
from selenium import webdriver
import json
import time

etree = html.etree
# 记录爬取的数据列表，每天都刷新一次
cdairport_list = []
# 记录每次爬取的数据总数
cdairport_data = 0


# 获取爬取页面源码
def get_html(cdairport_url):
    browser = webdriver.PhantomJS(executable_path='phantomjs.exe')
    browser.get(cdairport_url)

    print("获取网页数据...")
    html_text = browser.page_source
    # print(html_text)
    return html_text


# 解析html源码页面得到关键数据
def parse_html(cdairport_html):
    global cdairport_data
    cdairport_html = etree.HTML(cdairport_html)
    air_list = cdairport_html.xpath("//table[@class='arlineta departab']//tbody//tr")
    info = cdairport_html.xpath('//*[@id="ctl00_ContentID_Pager"]/div[1]/text()')[0].strip()
    now_page_num = info.split("/")[0].split("：")[1]
    print("正在爬取的页面是：" + now_page_num)
    for air_item in air_list:
        item = {
            '航班': air_item.xpath(".//td//marquee/text()")[0],
            "始发地": air_item.xpath(".//td[2]/text()")[0],
            "目的地": air_item.xpath(".//td[3]/text()")[0],
            "经停": "" if not air_item.xpath(".//td[4]/text()") else air_item.xpath(".//td[4]/text()")[0],
            "计划起飞": air_item.xpath(".//td[5]/text()")[0],
            "航站楼": air_item.xpath(".//td[6]/text()")[0],
            "状态": air_item.xpath(".//td[7]/text()")[0]
        }
        cdairport_list.append(item)
        cdairport_data = cdairport_data + 1
    # print(cdairport_list)


# 获取航班信息总页数
def parse_html_for_loop(cdairport_html):
    html = etree.HTML(cdairport_html)
    all_pagenum_text = html.xpath('//*[@id="ctl00_ContentID_Pager"]/div[1]/text()')[0].strip()
    all_pagenum = atoi(all_pagenum_text.split(" ")[0].split("/")[1])
    return all_pagenum


# 获取航班信息记录总数
def parse_html_for_loop1(cdairport_html):
    html = etree.HTML(cdairport_html)
    all_data_text = html.xpath('//*[@id="ctl00_ContentID_Pager"]/div[1]/text()')[0].strip()
    all_datanum = atoi(all_data_text.split(" ")[1].split("：")[1])
    return all_datanum


# 打包成json文件
def to_json(cdairport):
    filename = "cdairport.json"
    with open(filename, 'w', encoding='utf-8') as file_obj:
        json.dump(cdairport, file_obj, ensure_ascii=False)


if __name__ == '__main__':
    # 爬取网页地址
    base_url = "http://www.cdairport.com/flightInfor.aspx"
    # 每天定时爬取
    while True:
        # 清空JSON文件
        json_file = open('cdairport.json', 'w', encoding='utf-8')
        json_file.truncate()
        # 初始化爬取记录总数
        cdairport_data = 0

        # 得到所有页面数
        html = get_html(base_url)
        all_page_num = parse_html_for_loop(html)
        all_data_num = parse_html_for_loop1(html)
        print("成都双流国际机场今天出港航班情况记录总页数为：" + str(all_page_num) + "，总记录数为：" + str(all_data_num))
        print("请输入从哪个页面开始爬取（正整数）：")
        start_str = input()
        while not start_str.isdigit():
            print("请输入合法的正整数")
            start_str = input()
        start = eval(start_str)

        print("输入爬取到哪一个页面（正整数）：")
        end_str = input()
        while not start_str.isdigit():
            print("请输入合法的正整数")
            end_str = input()
        end = eval(end_str)
        # print(end)

        # 输入的end比start小
        if start > end:
            mid = start
            start = end
            end = mid

        # 如果输入的较大值大于总页面数
        if end > all_page_num:
            end = all_page_num

        for i in range(start, end + 1):
            url = base_url + "?page=" + str(i)
            # 获取html代码
            html = get_html(url)
            # 解析
            parse_html(html)
            # 输出成json文件
        to_json(cdairport_list)
        print("\n" + "爬取完成！本次共爬取数据数为：" + str(cdairport_data))
        # 每天定时爬取
        time.sleep(86400)
