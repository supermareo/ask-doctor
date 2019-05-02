CREATE TABLE `hospital_department` (
  `id` int(11) NOT NULL COMMENT '科室编号',
  `name` varchar(50) NOT NULL COMMENT '科室名称',
  `url` varchar(100) NOT NULL COMMENT '科室url',
  `level` int(10) NOT NULL COMMENT '科室等级-1级科室还是2级科室',
  `pid` int(10) DEFAULT NULL COMMENT '二级科室的所属科室'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `index` (
  `word` varchar(20) NOT NULL COMMENT '关键词',
  `qid` int(11) NOT NULL COMMENT '问题id',
  UNIQUE KEY `index` (`word`,`qid`) USING BTREE COMMENT '唯一索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `question` (
  `id` int(11) NOT NULL COMMENT '问题编号',
  `question` text COMMENT '问题详情',
  `answer` text,
  `url` varchar(100) DEFAULT NULL COMMENT '问题详情页url',
  `did` int(11) DEFAULT NULL COMMENT '所属科室id',
  `time` bigint(20) DEFAULT NULL COMMENT '收录时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `rank` (
  `qid` int(11) NOT NULL COMMENT '问题编号',
  `count` int(11) DEFAULT NULLCOMMENT '被查看次数',
  PRIMARY KEY (`qid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;