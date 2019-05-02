# coding=utf-8
# 爬虫相关操作服务
import requests
from bs4 import BeautifulSoup
import time

from utils.COMMON import BASE_URL, DEPARTMENT_LIST_URL, COMMON_HEADER, COMMON_BS4_PARSER
from utils.Util import department_real_url, department_id
from models.Model import Department, Question, MySqlOp
from service.IndexService import build_index

sql_op = MySqlOp('ask39')


# 获取页面数据，转化为soup
def get_page_to_soup(url):
    html = requests.get(url, headers=COMMON_HEADER).text
    return BeautifulSoup(html, COMMON_BS4_PARSER)


# 爬取所有科室列表
def crawler_all_departments():
    soup = get_page_to_soup(DEPARTMENT_LIST_URL)
    container = soup.select('div.J_first_screen')[0]
    container = container.select('div.J_classify_nav')
    departments = []
    for div in container[0:4]:
        a = div.select('a')[0]
        href = a['href']
        name = a.text
        url = department_real_url(href)
        id = department_id(href)
        departments.append(Department(id, name, url))
    for a in container[4].select('a')[1:]:
        href = a['href']
        name = a.text
        url = department_real_url(href)
        id = department_id(href)
        departments.append(Department(id, name, url))

    container = soup.select('div.J_classify_box')[0]
    container = container.select('div.J_classify_content')[4].select('div.page-subclassify-box')
    for div in container:
        a = div.select('div.page-subclassify-title>a')[0]
        href = a['href']
        name = a.text
        url = department_real_url(href)
        id = department_id(href)
        departments.append(Department(id, name, url))
    return departments


# 获取一级科室下所有二级科室列表
def crawler_all_secondary_departments(department):
    result = []
    pid = department.id
    level = 2
    url = department.url
    soup = get_page_to_soup(url)
    lis = soup.select('ol>li')
    if len(lis) > 1:
        for li in lis[1:]:
            name = li.text.strip()
            url = li['onclick'].replace('javascript:location.href=', '').replace('\'', '')
            id = department_id(url)
            url = BASE_URL[:-1] + url
            result.append(Department(id, name, url, level, pid))
    # 如果只有一个，是全部二级科室
    else:
        result.append(Department(pid, department.name, department.url, level, pid))
    return result


def get_total_pages(department):
    url = BASE_URL + 'news/' + str(department["id"]) + '-' + str(1) + '.html'
    soup = get_page_to_soup(url)
    pages_span = soup.select('span.pages')
    # 如果没有页数标签，说明这个页面不正确，不继续爬取，返回结果
    if len(pages_span) == 0:
        return 0
    last_page = soup.select('span.pages>span.pgleft>a')[-1]
    total_pages = last_page['href'].split('-')[1].split('.')[0]
    return int(total_pages)


# 爬取问答详情
def crawler_question_answer_detail(did, qid, url):
    try:
        print(f'爬取问答对:{url}')
        soup = get_page_to_soup(url)
        question_content = soup.select('p.txt_ms')[0].text.strip()
        answer_content = soup.select('p.sele_txt')[0].text.strip()
        question = Question(qid, question_content.replace(',', '，'), answer_content.replace(',', '，'), url, did,
                            int(round(time.time() * 1000)))
        sql_op.insert('question', question.__dict__)
        indexes = build_index(question.id, question.question)
        indexes = list(map(lambda x: x.__dict__, indexes))
        sql_op.insert_batch('`index`', indexes)
    except Exception as e:
        print(f'爬取问答对:{url}失败,e={e}')


# 爬取二级科室所有问答并入库
def crawler_secondary_department_qa(department):
    total_pages = get_total_pages(department)
    if total_pages == 0:
        return

    id = department["id"]

    # 所有已经爬取入库的该科室的问题id，用于后面爬取时，该部分数据不入库
    all_questions_in_db = sql_op.query('question', target_fields=['id'], where='did=' + str(id))
    all_questions_in_db = list(map(lambda q: q['id'], all_questions_in_db))
    print(all_questions_in_db)

    page = total_pages
    while page > 0:
        print(f'爬取第{page}页问题列表')
        url = BASE_URL + 'news/' + str(id) + '-' + str(page) + '.html'
        page -= 1
        soup = get_page_to_soup(url)
        question_as = soup.select('p.p1>a')
        for a in question_as:
            href = a['href']
            qid = href.split('/')[2].split('.')[0]
            # 如果已经爬取过了，在数据库里了，不处理
            if int(qid) in all_questions_in_db:
                continue
            crawler_question_answer_detail(id, qid, BASE_URL[:-1] + href)


# 获取所有需要爬取的科室
def get_all_departments_for_crawler():
    # 先到数据库中查是否有科室存在
    all_departments = sql_op.query('hospital_department')
    # 如果没有，需要到网页上爬取并入库
    if len(all_departments) == 0:
        departments = crawler_all_departments()
        for department in departments:
            sql_op.insert('hospital_department', department.__dict__)
            secondary_departments = crawler_all_secondary_departments(department)
            for secondary_department in secondary_departments:
                sql_op.insert('hospital_department', secondary_department.__dict__)
    return sql_op.query('hospital_department', target_fields='*', where='level=2')


def start_crawler():
    print('获取所有需要爬取的科室')
    all_departments = get_all_departments_for_crawler()
    print(f'所有需要爬取的科室个数:{len(all_departments)}')
    for department in all_departments:
        print(f'爬取科室:{department["name"]}')
        crawler_secondary_department_qa(department)


if __name__ == '__main__':
    start_crawler()
