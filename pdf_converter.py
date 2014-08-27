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

	def __init__(self, document, encoding=None, pages=None, images_folder=None, average_vdist=None):
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
		
	




		vdistance = list()
		i = 0
		
		for element in self.objects_respective_vertical_distance:
			print element.get("vertical_distance_with_object_above"), element.get("text")
			vdistance.append(element.get("vertical_distance_with_object_above"))
	
		self.average_vdist = sum([i for i in vdistance if i != 0])/len([i for i in vdistance if i != 0])
	
	
		print average_vdist
		#TODO : metadata of the pdf page
		
		
		
		Variables:
			self.objects_respective_vertical_distance
			list of the form with every element like this
					{"vertical_distance_with_object_above": layout_object.vdistance(self.whole_objects_list[-1]["object"]), 
							##Distance of this object fromt he object just present above it in the pdf
					"x0": 
						layout_object.x0, 
						##Objects starting x coordinate
					"x1": 	
						layout_object.x1, 
						##Objects ending x coordinate
					"y0": 
						layout_object.y0, 
						##Objects starting y coordinate
					"y1": 
						layout_object.y1,
						##Objects ending y  coordinate
					"text": 
						layout_object.get_text(), 
			self.formatted_output:
					a list which will have formatted output of questions	
				
		This list was created to calculate the self.average_vdist variable of this class, This average_vdist is the average distance 
		bewteen the lines in the pdf.
		If the distance is less than average_vdist, implies the text belongs to the same question
		"""
		self.average_vdist = average_vdist
		self.objects_heights = list()
		self.whole_objects_list = list()
		self.objects_respective_vertical_distance = list()

		self.formatted_output = [str()]

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
			self.objects_respective_vertical_distance.append({
				"vertical_distance_with_object_above": 
									child.vdistance(self.whole_objects_list[-1]["object"]), 
				"x0": 
					child.x0, 
				"x1": 	
					child.x1, 
				"y0": 
					child.y0, 
				"y1": 
					child.y1,
				"text": 
					child.get_text(), 
					})
		except IndexError:
			#As we seek -1 element of the self.objects_respective_vertical_distance, it might give indexerror for the 
			#first element
			pass
	
		self.whole_objects_list.append({
			"object": 
				child,
			"height":
				child.height,
			"text": 
				child.get_text(), 
			"is_child": 
				False,})
					
	
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
						self.objects_respective_vertical_distance.append({
							"vertical_distance_with_object_above": 
											layout_object.vdistance(self.whole_objects_list[-1]["object"]), 
							"x0": 
								layout_object.x0, 
							"x1": 	
								layout_object.x1, 
							"y0": 
								layout_object.y0, 
							"y1": 
								layout_object.y1,
							"text": 
								layout_object.get_text(), 
								})
					except IndexError:
						#As we seek -1 element of the self.objects_respective_vertical_distance, it might give indexerror for the 
						#first element
						pass
					self.whole_objects_list.append({
							"object": 
								layout_object,
							"height":
								layout_object.height,
							"text": 
								layout_object.get_text(), 
							"is_child": 
								False,})
					
			
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
	

		
		all_objects_heights = [element.get("height") for element in self.whole_objects_list]
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
	
		self.update_average_vdist() #calculates the average_vdist class variable
	
		self.joining_strings_for_same_question()	#joining string that belongs to the same question

	def joining_strings_for_same_question(self):
		"""
		This method joins the strings present in the self.objects_respective_vertical_distance after it has been sorted by 
		rearrange_on_the_basis_of_y0 on the basis of y0(strings starting y coordinates in the pdf

		Joining takes places by comparing their vertical_distance_with_object_above with the average_vdist class variable
		if objects vertical_distance_with_object_above is less than average_vdist class variable implies that 
		object belongs to the object present before in the self.objects_respective_vertical_distance list
		"""
		
		SORTED_QUESTION_DISTANCE = self.rearrange_on_the_basis_of_y0()
	
		for element in SORTED_QUESTION_DISTANCE:
			
			if element.get("vertical_distance_with_object_above") <= self.average_vdist:
				self.formatted_output[-1] = "\t".join([self.formatted_output[-1], element.get("text")])
			else:
				self.formatted_output.append(element.get("text"))
	

	def print_output(self):
		for sentence in self.formatted_output:
			print sentence


	def rearrange_on_the_basis_of_y0(self):
		newlist = sorted(self.objects_respective_vertical_distance, key=lambda k: k['y0'], reverse=True) 	
		return newlist


	def update_average_vdist(self):
		"""
		If average_vdist param is not provided to the class, This methos will calculate the average vdist
		
		Only the objects which are not children of other objects is considered while calculating the 
		average_vdist because if we do consider them, the average comes out to be to much for iut to be taken into account
		"""
		if not self.average_vdist:
			vdistance = list()
			vdistance = [element.get("vertical_distance_with_object_above") for element in self.objects_respective_vertical_distance
					if element.get("vertical_distance_with_object_above") != 0]
			self.average_vdist = sum(vdistance)/len(vdistance)
	



def remove_headings(lt_obj):
	"""
	This function removes the heading and topics or also if possible the footer from the pdf file
	Use pdf query to parse objects on the basis of regular expressions if required
	
	
	Use pypdf2 to add meta data to the questions
	"""

	pass


if __name__ == "__main__":
	filename = sys.argv[1]
	ins = PDFConverter(filename, encoding=None, pages=1, images_folder=None)
	ins.parse_page()
	ins.print_output()
