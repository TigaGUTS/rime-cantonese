#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from itertools import chain
import json
import os
import re
from sortedcontainers import SortedKeyList

from LSHK字音表 import LSHK字音表
from 粵音小鏡 import 粵音小鏡
from 廣州話正音字典 import 廣州話正音字典
from 常用字廣州話讀音表 import 常用字廣州話讀音表
from 粵語審音配詞字庫 import 粵語審音配詞字庫

LSHK字音表()
粵音小鏡()
廣州話正音字典()
常用字廣州話讀音表()
粵語審音配詞字庫()

if not os.path.exists('build/single-char/final.txt'):
	with open('build/single-char/data/0-Unihan.json') as unihan, open('build/single-char/data/1-LSHK字音表.csv') as LSHK字音表, open('build/single-char/data/1-粵音小鏡.csv') as 粵音小鏡, open('build/single-char/data/1-廣州話正音字典.csv') as 廣州話正音字典, open('build/single-char/data/1-常用字廣州話讀音表.csv') as 常用字廣州話讀音表, open('build/single-char/data/1-粵語審音配詞字庫.csv') as 粵語審音配詞字庫, open('build/single-char/final.txt', 'w') as fout:
		pattern = re.compile(r'(?P<字>.),(?P<粵拼讀音>.+)\n')
		d = defaultdict(set)
		for line in chain(LSHK字音表, 粵音小鏡, 廣州話正音字典, 常用字廣州話讀音表, 粵語審音配詞字庫):
			match = pattern.match(line)
			字, 粵拼讀音 = match['字'], match['粵拼讀音']
			d[字].add(粵拼讀音)

		lis = json.load(unihan)

		final = SortedKeyList(key=lambda t: t[1])

		for li in lis:  # 對於 Unihan 中的某個字
			char, kCantonese = li['char'], li['kCantonese']

			assert len(kCantonese) != 0
			if len(kCantonese) == 1:  # 若只有一音 -> 收錄
				final.add((char, kCantonese[0]))
			else:  # 若有多個音
				res = d.get(char)
				if res is not None:  # 若五份資料中任意一份有此字
					cnt = 0
					for pronunciation in kCantonese:  # 若其中某幾個發音見於五份資料中任意一份 -> 收錄這幾個發音
						if pronunciation in res:
							final.add((char, pronunciation))
							cnt += 1
					if cnt == 0:  # 若每個音都不見於五份資料中任意一份 -> Unihan 和五份資料中的發音均收錄
						for pronunciation in chain(kCantonese, res):
							final.add((char, pronunciation))
				else:  # 若五份資料中每份均無此字 -> 全部收錄
					for pronunciation in kCantonese:
						final.add((char, pronunciation))

		for char, pronunciation in final:
			print(f'{char}\t{pronunciation}', file=fout)