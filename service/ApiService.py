# coding=utf-8
# API相关操作服务

from models.Model import MySqlOp
from service.IndexService import split_sentence
from utils.Util import sentences_similarity


# 5个最多搜索的问题
# [{
# 	'qid': 58043452,
# 	'count': 6,
# 	'question': '明天要进行动脉导管未闭的手术，有一些害怕，像这种手术需要进行全麻吗，会不会有醒不过来的这种情况发生呢，应该怎么样去避免一些不良症状的出现？',
# 	'department': '心血管内科'
# }, {
# 	'qid': 58043372,
# 	'count': 5,
# 	'question': '左肩拉伤现在疼痛难受',
# 	'department': '心血管内科'
# }, {
# 	'qid': 58043345,
# 	'count': 4,
# 	'question': '我妈妈昨天情绪激动说话嘴角有淤血是为什么',
# 	'department': '心血管内科'
# }, {
# 	'qid': 58042766,
# 	'count': 3,
# 	'question': '男性左侧下腹与肚脐平位置隐隐阵疼痛怎么回事',
# 	'department': '心血管内科'
# }, {
# 	'qid': 58042716,
# 	'count': 2,
# 	'question': '母亲69岁，用电子血压计测量，高压178，低压78，偶尔心跳加快两下，晚上偶尔盗汗。',
# 	'department': '心血管内科'
# }]
def top5questions():
    sql_op = MySqlOp('ask39')
    top_5_qids = sql_op.query('rank', target_fields=['qid', 'count'], where=None, order='count DESC', limit=5)
    result = []
    if len(top_5_qids) == 0:
        return []
    for rank in top_5_qids:
        qid = rank['qid']
        count = rank['count']
        question_and_department = sql_op.raw_query(
            'SELECT question,name FROM question '
            'LEFT JOIN hospital_department ON question.did=hospital_department.id '
            'WHERE question.id=' + str(qid)
        )[0]
        result.append(
            {
                'qid': str(qid),
                'count': count,
                'question': question_and_department['question'],
                'department': question_and_department['name']
            }
        )
    return result


# 获取最新收录的问题
# [{
# 	'qid': 58042652,
# 	'question': '我的邻居胃痛7年了,主要胃脘胀痛,两肋胀痛,胸闷气短,肚子里老是有气,嗳气,请问胃脘胁肋胀痛怎么治疗比较好呢？',
# 	'department': '心血管内科'
# }, {
# 	'qid': 58042716,
# 	'question': '母亲69岁，用电子血压计测量，高压178，低压78，偶尔心跳加快两下，晚上偶尔盗汗。',
# 	'department': '心血管内科'
# }, {
# 	'qid': 58042766,
# 	'question': '男性左侧下腹与肚脐平位置隐隐阵疼痛怎么回事',
# 	'department': '心血管内科'
# }, {
# 	'qid': 58043345,
# 	'question': '我妈妈昨天情绪激动说话嘴角有淤血是为什么',
# 	'department': '心血管内科'
# }, {
# 	'qid': 58043372,
# 	'question': '左肩拉伤现在疼痛难受',
# 	'department': '心血管内科'
# }]
def latest5questions():
    sql_op = MySqlOp('ask39')
    result = []
    question_and_departments = sql_op.raw_query(
        'SELECT question.id,question.question,hospital_department.name FROM question '
        'LEFT JOIN hospital_department ON question.did=hospital_department.id '
        'ORDER BY time DESC LIMIT 5;'
    )
    for qad in question_and_departments:
        result.append(
            {
                'qid': str(qad['id']),
                'question': qad['question'],
                'department': qad['name']
            }
        )
    return result


# 输入句子进行问题检索
def sentence_search(sentence):
    sql_op = MySqlOp('ask39')
    # 分词
    words = split_sentence(sentence)
    if len(words) == 0:
        return []

    sql_word = '("' + '","'.join(words) + '")'
    # 到索引表中查找
    sql = f'SELECT qid FROM `index` WHERE word IN {sql_word}'
    qids = sql_op.raw_query(sql)
    qids = list(map(lambda q: str(q['qid']), qids))
    # 查找出所有问题详情
    sql_qids = '("' + '","'.join(qids) + '")'
    sql = 'SELECT question.id,question.question,hospital_department.name FROM question ' \
          'LEFT JOIN hospital_department ON question.did=hospital_department.id ' \
        f'WHERE question.id IN {sql_qids};'
    question_and_departments = sql_op.raw_query(sql)
    # 根据相似度排序
    question_and_departments = sorted(question_and_departments,
                                      key=lambda qad: sentences_similarity(sentence, qad['question']))
    question_and_departments = list(map(lambda q: {
        'qid': str(q['id']),
        'question': q['question'],
        'department': q['name']
    }, question_and_departments))
    print(question_and_departments)
    return question_and_departments


# 查找问答详情
def get_question_detail(qid):
    sql_op = MySqlOp('ask39')
    qads = sql_op.raw_query(
        'SELECT question.id,question.question,question.answer,hospital_department.name FROM question '
        'LEFT JOIN hospital_department ON question.did=hospital_department.id '
        'WHERE question.id=' + str(qid)
    )
    if len(qads) == 0:
        return None
    increase_rank(qid)
    qad = qads[0]
    question = qad['question']
    return {
        'qid': qad['id'],
        'question': question,
        'title': question if len(question) < 30 else (question[0:30] + '...'),
        'department': qad['name'],
        'answer': qad['answer']
    }


# 获取问答总条数
def get_total_questions():
    sql_op = MySqlOp('ask39')
    return sql_op.raw_query('SELECT COUNT(1) AS total FROM question')[0]['total']


# 每搜索一次问答详情，评分加一
def increase_rank(qid):
    sql_op = MySqlOp('ask39')
    sql = f'INSERT INTO rank(qid,count) VALUES({qid},1) ON DUPLICATE KEY UPDATE count=count+1;'
    sql_op.raw_insert(sql)

# if __name__ == '__main__':
#     print(top5questions())
#     print(latest5questions())
#     print(get_question_detail(58042652))
#     increase_rank(58042652)
#     increase_rank(58042652)
#     increase_rank(58042652)
