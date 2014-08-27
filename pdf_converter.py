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




class PDFConverter:

	def __init__(self, document, encoding=None, pages=None, images_folder=None):
		"""
		Points to remember:
			1. bbox[0] is the starting x coordinate, bbox[1] is the starting y coordinate, bbox[2] is the ending x coordinate 
			and bbox[3] is the ending y coordinate.

		Args:
			encoding: DEFAULT: "utf-8"
				
				Encoding of the text to be taken into account, otherwise it will raise ascii encoding error.
				If its still gives ascii encoding error, try to change encoding 

			pages: DEAFULT: ALl the pages present in the pdf given
				Number of the pages you want to convert from the total pages of the file,
				This argument is genrally been used for testing,

			Document: DEAFULT: None
				pdf document to be converted
		
			images_folder: DEAFULT: None
				Need to be provided if the document also has the images attached to it

		How it works??
			# Create a PDF parser object associated with the file object.
			self.parser = PDFParser(pdf_file)
			# Create a PDF document object that stores the document structure.
			# Password for initialization as 2nd parameter
			#TODO if password is required
			document = PDFDocument(parser)
			# Check if the document allows text extraction. If not, abort.
			if not document.is_extractable:
				raise StandardError("Document cannot be extracted")
		
		
		#TODO : metadata of the pdf page
		"""

		self.objects_heights = list()
		self.whole_objects_list = list()
		self.objects_respective_vertical_distance = list()
		
		if encoding:
			self.encoding = "utf-8"	
		else:
			self.encoding = encoding
	
		if pages:
			self.pages = pages
		else:
			self.pages = None

		if images_folder:
			self.images_folder = images_folder
		else:
			self.images_folder = None



		try:
			pdf_file = open(filename, 'rb')
		except:
			raise StandardError("This file cannot be opened")

		self.parser = PDFParser(pdf_file)
		self.document = PDFDocument(self.parser)
		if not self.document.is_extractable:
			raise StandardError("Document cannot be extracted")

	
	def parse_page(self):
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
		
		for i, page in enumerate(PDFPage.create_pages(self.document)):
			# read the page into a layout object
			interpreter.process_page(page)
			layout = device.get_result()
			
			if self.pages:
				if page_count == self.pages:
					break
			page_count += 1
			self.parse_layout_objects(layout._objs, (i+1))


	def to_bytestring (self, s):
		"""Convert the given unicode string to a bytestring, using the standard encoding,
		unless it's already a bytestring"""
		if s:
			if isinstance(s, str):
				return 
			else:
				return s.encode(self.encoding)

	
	def parse_layout_objects_children(self, child, index):
		"""
		All the children will have the same index
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
		"""
		try:
			self.whole_objects_list.append({
							"object": 
								child,
							"vertical_distance_with_object_above": 
											child.vdistance(self.whole_objects_list[-1]["object"]), 
							"height":
								child.height,
							"text": 
								child.get_text(), 
							"x0": 
								child.x0, 
							"x1": 	
								child.x1, 
							"y0": 
								child.y0, 
							"y1": 
								child.y1,
							"is_child": 
								True,})
		except IndexError:
			print "index error occurred"
			pass
	
	
	def parse_layout_objects(self, layout_objects, page_number):
		"""
		This method iterates over the layout object present in the page
		"""
		
		for layout_object in layout_objects:
			if isinstance(layout_object, pdfminer.layout.LTTextBox) or isinstance(layout_object, pdfminer.layout.LTTextLine):
				if len(layout_object._objs) > 1:
					for child in layout_object._objs:
						self.parse_layout_objects_children(child, layout_object.index)
				
				else:
					try:
						self.whole_objects_list.append({
							"object": 
								layout_object,
							"vertical_distance_with_object_above": 
											layout_object.vdistance(self.whole_objects_list[-1]["object"]), 
							"height":
								layout_object.height,
							"text": 
								layout_object.get_text(), 
							"x0": 
								layout_object.x0, 
							"x1": 	
								layout_object.x1, 
							"y0": 
								layout_object.y0, 
							"y1": 
								layout_object.y1,
							"is_child": 
								False,})

					except IndexError:
						print "index error occurred"
						pass
					
			
			elif isinstance(layout_object, pdfminer.layout.LTImage):
				# an image, so save it to the designated folder, and note it's place in the text 
				saved_file = save_image(lt_obj, page_number, images_folder)
				
				if saved_file:
					# use html style <img /> tag to mark the position of the image within the text
					text_content.append('<img src="'+os.path.join(images_folder, saved_file)+'" />')
				
				else:
					print >> sys.stderr, "Error saving image on page", page_number, lt_obj.__repr__
			
			elif isinstance(layout_object, pdfminer.layout.LTFigure):
				print "This instance belongs to pdfminer.layout.LTFigure"
	
			
			elif isinstance(layout_object, pdfminer.layout.LTLine):
				print "This instance belongs to pdfminer.layout.LTLine"
	

		
		print self.whole_objects_list
		all_objects_heights = [element.get("height") for element in self.whole_objects_list]
		print all_objects_heights
		AVERAGE_HEIGHT = (sum(all_objects_heights)/len(all_objects_heights))
	
	
		"""
		If you want to delete the heading of the pdf presented to you
		another_list = list()
		
		for elem in FINAL_LIST:
			if elem.get("height") >= int(AVERAGE_HEIGHT+1):
				print elem.get("height"), "is child %s"%elem.get("is_child"), elem.get("text")
				another_list.append(elem)
			else:
				break
	
	
	
		without_heading = [element for element in FINAL_LIST if element not in another_list]
		"""
	
		vdistance = list()
		i = 0
		
		for element in self.whole_objects_list:
			print element.get("vertical_distance_with_object_above"), element.get("text")
			vdistance.append(element.get("vertical_distance_with_object_above"))
	
		average_vdist = sum([i for i in vdistance if i != 0])/len([i for i in vdistance if i != 0])
	
	
		print average_vdist
	
	
		final_list = [str()]
	
	
		SORTED_QUESTION_DISTANCE = self.rearrange_on_the_basis_of_y0()
	
		for element in SORTED_QUESTION_DISTANCE:
			
			if element.get("distance") <= average_vdist:
				final_list[-1] = "\t".join([final_list[-1], element.get("text")])
			else:
				final_list.append(element.get("text"))
			print element
	
	
	
		for nn in final_list:
			print nn
	
		print final_list
		print "average vertical distance %s"%(sum(vdistance)/int(len(self.whole_objects_list)))


	def rearrange_on_the_basis_of_y0(self):
		newlist = sorted(self.whole_objects_list, key=lambda k: k['y0'], reverse=True) 	
		return newlist

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







def remove_headings(lt_obj):
	"""
	This function removes the heading and topics or also if possible the footer from the pdf file
	Use pdf query to parse objects on the basis of regular expressions if required
	
	
	Use pypdf2 to add meta data to the questions
	"""

	pass









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
	filename = sys.argv[1]
	print filename
	ins = PDFConverter(filename, encoding=None, pages=1, images_folder=None)
	ins.parse_page()
