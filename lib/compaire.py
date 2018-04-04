#!/usr/bin/python
# -*- coding: UTF-8 -*-

def canonize(source):
	stop_symbols = '.,!?:;-\n\r()"«»'

	stop_words = ('это', 'как', 'так',
	'и', 'в', 'над',
	'к', 'до', 'не',
	'на', 'но', 'за',
	'то', 'с', 'ли',
	'а', 'во', 'от',
	'со', 'для', 'о',
	'же', 'ну', 'вы',
	'бы', 'что', 'кто',
	'он', 'она')

	return ( [x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x and (x not in stop_words)] )

def genshingle(source):
	import binascii
	shingleLen = 2 #длина шингла
	out = [] 
	for i in range(len(source)-(shingleLen-1)):
		out.append (binascii.crc32(' '.join( [x for x in source[i:i+shingleLen]] )))	#.encode('utf-8')))
	return out

def compaire (source1,source2):
	same = 0
	for i in range(len(source1)):
		if source1[i] in source2:
			same = same + 1
	return same*2/float(len(source1) + len(source2))*100

if __name__ == '__main__':
	text1 = '''Nimrod - язык программирования, сочетающий ''
	""в себе наилучшие черты различных стилей программирования.
	 первой статье был представлен общий обзор этого языка. 
	о второй статье описываются лексические элементы языка и основные типы данных.'''

	text2 = '''язык программирования ''
	, сочетающий в себе наилучшие черты различных стилей программирования.
    В первой статье был представлен общий обзор этого языка. Во второй статье описываются лексические элементы языка и основные типы данных.'''

	cmp1 = genshingle(canonize(text1))
	for j in range(0, len(text2), 2):
		test = text2[j:]
		print j, test
		cmp2 = genshingle(canonize(test))
		print compaire(cmp1,cmp2)
	'''
	'''
