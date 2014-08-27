#!/usr/bin/env python
##Reference: http://stackoverflow.com/questions/22898145/how-to-extract-text-and-text-coordinates-from-a-pdf-file?rq=1


from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
import sys

TEXT_HEIGHTS = list()
FINAL_LIST = list()
QUESTION_DISTANCE = list()


def to_bytestring (s, enc='utf-8'):
	"""Convert the given unicode string to a bytestring, using the standard encoding,
	unless it's already a bytestring"""
	if s:
		if isinstance(s, str):
			return 
		else:
			return s.encode(enc)




def update_page_text_hash (h, lt_obj, pct=0.15):
	"""Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""
	x0 = lt_obj.bbox[0]
	x1 = lt_obj.bbox[1]
	x2 = lt_obj.bbox[2]
	x3 = lt_obj.bbox[3]
	key_found = False

	h[(x0,x2, x1, x3)] = [to_bytestring(lt_obj.get_text())]
	
	"""
	for k, v in h.items():
		hash_x0 = k[0]
		
		if x0 >= ((hash_x0*(1.0-pct)) -2) and (hash_x0 * (1.0 - pct) +2) <= x0:
				# the text inside this LT* object was positioned at the same
				# width as a prior series of text, so it belongs together
				key_found = True
				v.append(to_bytestring(lt_obj.get_text()))
				h[k] = v
	if not key_found:
		# the text, based on width, is a new series,
		# so it gets its own series (entry in the hash)
		h[(x0,x1)] = [to_bytestring(lt_obj.get_text())]
	"""
	return h





def parse_page(document, images_folder):
	# Check if the document allows text extraction. If not, abort.
	if not document.is_extractable:
		raise PDFTextExtractionNotAllowed
	print dir(document)
	# Create a PDF resource manager object that stores shared resources
	rsrcmgr = PDFResourceManager()
	
	# Create a PDF device object.
	device = PDFDevice(rsrcmgr)

	# BEGIN LAYOUT ANALYSIS
	# Set parameters for analysis.
	laparams = LAParams()

	# Create a PDF page aggregator object.
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)

	# Create a PDF interpreter object.
	interpreter = PDFPageInterpreter(rsrcmgr, device)

	text_content = list()
	page_count = 0
	for i, page in enumerate(PDFPage.create_pages(document)):
		# read the page into a layout object
		interpreter.process_page(page)
		layout = device.get_result()
		# extract text from this object
		if page_count == 2:
			break
		return parse_lt_objs(layout._objs, (i+1), images_folder)
		#text_content.append(parse_lt_objs(layout._objs, (i+1), images_folder))
		page_count += 1



def remove_headings(lt_obj):
	"""
	This function removes the heading and topics or also if possible the footer from the pdf file
	Use pdf query to parse objects on the basis of regular expressions if required
	
	
	Use pypdf2 to add meta data to the questions
	"""

	pass


def parse_lt_objs_children(child, index):
	"""
	All the children will have the same index
	"""
	print "Now parsing the fucking children"		
	print "hdistance==%s"%child.hdistance
	print "vdistance==%s"%child.vdistance 
	print "height==%s"%child.height 
	print "width==%s"%child.width 
	print "bbox0==%s"%child.bbox[0] 
	print "bbox1==%s"%child.bbox[1] 
	print "bbox2==%s"%child.bbox[2] 
	print "bbox3==%s"%child.bbox[3] 
	print "index==%s"%index
	try:
		QUESTION_DISTANCE.append({"distance": child.vdistance(FINAL_LIST[-1]["object"]), "text": child.get_text(),
			"x0": child.x0, "x1": child.x1, "y0": child.y0, "y1": child.y1})
	except IndexError:
		pass
	TEXT_HEIGHTS.append(child.height)
	FINAL_LIST.append({"object": child, "height": child.height, "is_child": True, "text": child.get_text()})
	print "\n\n"



def rearrange_on_the_basis_of_y0():
	newlist = sorted(QUESTION_DISTANCE, key=lambda k: k['y0'], reverse=True) 	
	return newlist

def parse_lt_objs (lt_objs, page_number, images_folder):
	"""Iterate through the list of LT* objects and capture the text or image data contained in each
	bbox[0] is the starting x coordinate, bbox[1] is the starting y coordinate, bbox[2] is the ending x coordinate, 
	and bbox[3] is the ending y coordinate.
	"""
	text_heights = list()

	text_content = list()
	page_text = dict()

	for lt_obj in lt_objs:
		#print lt_obj, lt_obj.bbox[0], lt_obj.bbox[1], lt_obj.bbox[2], lt_obj.bbox[3]
		if isinstance(lt_obj, pdfminer.layout.LTTextBox) or isinstance(lt_obj, pdfminer.layout.LTTextLine):
			if len(lt_obj._objs) > 1:
				for element in lt_obj._objs:
					parse_lt_objs_children(element, lt_obj.index)
			else:
				print "objs==%s"%lt_obj._objs
				try:
					QUESTION_DISTANCE.append({"distance": lt_obj.vdistance(FINAL_LIST[-1]["object"]), "text": lt_obj.get_text(),
						"x0": lt_obj.x0, "x1": lt_obj.x1, "y0": lt_obj.y0, "y1": lt_obj.y1 })
				except IndexError:
					pass
				print "vdistance==%s"%lt_obj.vdistance 
				print "height==%s"%lt_obj.height 
				print "width==%s"%lt_obj.width 
				print "bbox0==%s"%lt_obj.bbox[0] 
				print "bbox1==%s"%lt_obj.bbox[1] 
				print "bbox2==%s"%lt_obj.bbox[2] 
				print "bbox3==%s"%lt_obj.bbox[3] 
				print "index==%s"%lt_obj.index
				TEXT_HEIGHTS.append(lt_obj.height)
				FINAL_LIST.append({"object": lt_obj, "height": lt_obj.height, "is_child": False, "text": lt_obj.get_text()})

				print "\n\n"
				#lt_obj.bbox[0], lt_obj.bbox[1], lt_obj.bbox[2], lt_obj.bbox[3], lt_obj.get_text()
				#page_text = update_page_text_hash(page_text, lt_obj)
		
		elif isinstance(lt_obj, pdfminer.layout.LTImage):
			# an image, so save it to the designated folder, and note it's place in the text 
			saved_file = save_image(lt_obj, page_number, images_folder)
			
			if saved_file:
				# use html style <img /> tag to mark the position of the image within the text
				text_content.append('<img src="'+os.path.join(images_folder, saved_file)+'" />')
			
			else:
				print >> sys.stderr, "Error saving image on page", page_number, lt_obj.__repr__
		elif isinstance(lt_obj, pdfminer.layout.LTFigure):
			print "entered in lt figure"
			# LTFigure objects are containers for other LT* objects, so recurse through the children
			#text_content.append(parse_lt_objs(lt_obj.objs, page_number, images_folder, text_content))

		elif isinstance(lt_obj, pdfminer.layout.LTLine):
			print "goootaaaa"
			#print dir(lt_obj), lt_obj.linewidth




	"""
		elif isinstance(lt_obj, pdfminer.layout.LTCurve):
			print dir(lt_obj)

		elif isinstance(lt_obj, pdfminer.layout.LTRect):
			print dir(lt_obj)
		
		elif isinstance(lt_obj, pdfminer.layout.LTLine):
			print dir(lt_obj)


	for k, v in sorted([(key,value) for (key,value) in page_text.items()]):
		# sort the page_text hash by the keys (x0,x1 values of the bbox),
		# which produces a top-down, left-to-right sequence of related columns
		text_content.append('\n'.join(v))

	
	return "\n".join(text_content)
	"""
	AVERAGE_HEIGHT = (sum(TEXT_HEIGHTS)/len(TEXT_HEIGHTS))



	another_list = list()
	
	for elem in FINAL_LIST :
		if elem.get("height") >= int(AVERAGE_HEIGHT+1):
			print elem.get("height"), "is child %s"%elem.get("is_child"), elem.get("text")
			another_list.append(elem)
		else:
			break



	without_heading = [element for element in FINAL_LIST if element not in another_list]


	vdistance = list()
	i = 0
	for element in QUESTION_DISTANCE:
		print element.get("distance"), element.get("text")
		vdistance.append(element.get("distance"))

	average_vdist = sum([i for i in vdistance if i != 0])/len([i for i in vdistance if i != 0])


	print average_vdist


	final_list = [str()]


	SORTED_QUESTION_DISTANCE = rearrange_on_the_basis_of_y0()

	for element in SORTED_QUESTION_DISTANCE:
		
		if element.get("distance") <= average_vdist:
			final_list[-1] = "\t".join([final_list[-1], element.get("text")])
		else:
			final_list.append(element.get("text"))
		print element



	for nn in final_list:
		print nn

	print final_list
	print "average vertical distance %s"%(sum(vdistance)/int(len(QUESTION_DISTANCE)))
	return



def run(filename):
	# Open a PDF file.
	fp = open(filename, 'rb')

	# Create a PDF parser object associated with the file object.
	parser = PDFParser(fp)

	# Create a PDF document object that stores the document structure.
	# Password for initialization as 2nd parameter
	document = PDFDocument(parser)
	return parse_page(document, "images")


if __name__ == "__main__":
	run(sys.argv[1])

