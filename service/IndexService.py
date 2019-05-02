# coding=utf-8
# 索引相关操作
from utils.Util import split_sentence
from models.Model import Index


# 建立索引 关键词->问题id
def build_index(qid, question):
    result = []
    # 分词
    words = split_sentence(question)
    for word in words:
        result.append(Index(word, qid))
    return result

# if __name__ == '__main__':
#     print(split_sentence('你就是一个就是大沙雕！哈哈'))
#     print(filter_stop_words(split_sentence('你就是一个就是大杀掉！哈哈')))
