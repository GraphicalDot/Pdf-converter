#!/usr/bin/env python
import copy, sys
from pyPdf import PdfFileWriter, PdfFileReader
import math


def into_half(src, dst):
	_src = file(src, 'rb')
	_dst = file(dst, 'wb')
	
	
	
	input = PdfFileReader(_src)

	output = PdfFileWriter()
	
	for i in range(input.getNumPages()):
		
		p = input.getPage(i)
		q = copy.copy(p)
		q.mediaBox = copy.copy(p.mediaBox)

		#x1, x2 = p.mediaBox.lowerLeft
		#x3, x4 = p.mediaBox.upperRight
		(w, h) = p.mediaBox.upperRight
		
		print w, h
		
		p.mediaBox.upperRight = (w/2, h)
		q.mediaBox.upperLeft = (w/2, h)

		output.addPage(p)
		output.addPage(q)

	output.write(_dst)
	_src.close()
	_dst.close()




if __name__ == "__main__":
	print sys.argv[1], sys.argv[2]
	into_half(sys.argv[1], sys.argv[2])
	
