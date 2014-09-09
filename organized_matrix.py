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
from pdfminer.converter import TextConverter
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
		self.whole_objects_list = list()

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
			self.page_height = layout.height
			self.page_width = layout.width
			
			if self.pages:
				if page_count == self.pages:
					break
			page_count += 1
			self.parse_layout_objects(layout, layout._objs, (i+1))


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
		print child
		if isinstance( child, pdfminer.layout.LTTextBox) or isinstance(child, pdfminer.layout.LTTextLine):
			print "child is the proper isinstance"
		try:
			self.whole_objects_list.append({
				"object": 
									child,
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
			self.whole_objects_list.append({
				"object": 
									child,
				"vertical_distance_with_object_above": 
									0, 
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
			pass
	
	
	def parse_layout_objects(self, __layout, layout_objects, page_number):
		"""
		This method iterates over the layout object present in the page
		"""
	
		print __layout.x0, __layout.x1, __layout.y0, __layout.y1

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
						#first element
						self.whole_objects_list.append({
							"object": 
									layout_object,

							"vertical_distance_with_object_above": 
												0, 
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
	

		
		self.update_average_vdist() #calculates the average_vdist class variable

		self.two_dimensional_matrix()


		#self.joining_strings_for_same_question()	#joining string that belongs to the same question


	def two_dimensional_matrix(self):
		"""
		This method now only works according to the one page because it now cannot distinguish whether the question in the last page 
		is still continuing on the next page.

		The whole matrix was made according to the length and beardth of the page, which has already been calculated by
		parse_page mthod of this class and has been stored in self.parse_page

		This method creates a two dimensional matrix of the pdf objects according to their coordinates.
		x0 is the starting x coordinate and x1 is the ending x coordinate, similarly
		y0 is the starting y coorodinbate and the y1 is the ending y coordinate.
		
		
		"""
		for item in self.whole_objects_list:
			print item, "\n\n"

		two_dimensional_matrix = [[(element, s) for s in range(0, 649)] for element in range(0, 829)]
		
		
		"""
		ii = [(int(i["x0"]), int(i["y0"])) for i in self.whole_objects_list]	
		print sorted([int(i["x0"]) for i in self.whole_objects_list])	
		print [int(i["y0"]) for i in self.whole_objects_list]
		
		print "length of the list %s"%len(ii)
		print "length of the set %s"%len(list(set(ii)))
		"""
		
		for _object in self.whole_objects_list:
			check_list = list()
			"""
			two_dimensional_matrix[y0][x0] because the number of elements in this two dimensional matrix represents
			the height of the matrix or height of the page

			"""
			x0, y0, x1, y1 = int(_object["x0"]), int(_object["y0"]), int(_object["x1"]), int(_object["y1"])

			counter = 0
			two_dimensional_matrix[y0][x0] = _object
			
			"""
			for element in range(x0+1, x1+1):
				two_dimensional_matrix[y0][element] = None
				print "matrix updated with new cooridinates"

			two_dimensional_matrix[y0] = [element for element in two_dimensional_matrix[y0] if element]	
			"""
		
		check_list = list()
		for element in two_dimensional_matrix[::-1]:
			for member in element:
				try:
					if isinstance( member["object"], pdfminer.layout.LTTextBox) or isinstance(member["object"], pdfminer.layout.LTTextLine):
						check_list.append("True")
						print member["object"]
				except:
					pass
		
		print "THe length of the check list is %s"%len(check_list)
		return

	def joining_strings_for_same_question(self):
		"""
		This method joins the strings present in the self.objects_respective_vertical_distance after it has been sorted by 
		rearrange_on_the_basis_of_y0 on the basis of y0(strings starting y coordinates in the pdf

		Joining takes places by comparing their vertical_distance_with_object_above with the average_vdist class variable
		if objects vertical_distance_with_object_above is less than average_vdist class variable implies that 
		object belongs to the object present before in the self.objects_respective_vertical_distance list
		"""
		
		#SORTED_QUESTION_DISTANCE = self.rearrange_on_the_basis_of_y0()
		SORTED_QUESTION_DISTANCE = self.whole_objects_list
	
		for element in SORTED_QUESTION_DISTANCE:
			
			if element.get("vertical_distance_with_object_above") <= self.average_vdist:
				self.formatted_output[-1] = "\t".join([self.formatted_output[-1], element.get("text")])
			else:
				self.formatted_output.append(element.get("text"))
	

	def print_output(self):
		print self.formatted_output
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
			vdistance = [element.get("vertical_distance_with_object_above") for element in self.whole_objects_list
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
	filename, pages = sys.argv[1], sys.argv[2]
	print pages
	ins = PDFConverter(filename, encoding=None, pages=int(pages), images_folder=None)
	ins.parse_page()
	ins.print_output()



"""
#########################################################
############ First column starts #######################
#########################################################
{'vertical_distance_with_object_above': 14.025703762000035, 'x1': 315.0156999999999, 'y0': 575.4193, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 592.2093, 'hoverlap': 62.77159999999992, 'x0': 72.3966, 'object': <LTTextLineHorizontal 72.397,575.419,315.016,592.209 u'1. The  sun  remains  visible  for  some  time  after  it\n'>, 'text': u'1. The  sun  remains  visible  for  some  time  after  it\n'} 


{'vertical_distance_with_object_above': 0, 'x1': 314.20019999999994, 'y0': 568.7194, 'horizontal_distance_with_object_above': 0, 'voverlap': 5.2900999999999385, 'y1': 580.7094, 'hoverlap': 227.17569999999992, 'x0': 87.84, 'object': <LTTextLineHorizontal 87.840,568.719,314.200,580.709 u'actually sets below the horizon. This happens due to\n'>, 'text': u'actually sets below the horizon. This happens due to\n'} 


{'vertical_distance_with_object_above': 0.009900000000016007, 'x1': 205.2596, 'y0': 556.7194999999999, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 568.7094999999999, 'hoverlap': 117.4196, 'x0': 87.84, 'object': <LTTextLineHorizontal 87.840,556.719,205.260,568.709 u'1. Atmospheric refraction\n'>, 'text': u'1. Atmospheric refraction\n'} 


{'vertical_distance_with_object_above': 0.00989999999990232, 'x1': 183.3271, 'y0': 544.7196, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 556.7096, 'hoverlap': 95.4871, 'x0': 87.84, 'object': <LTTextLineHorizontal 87.840,544.720,183.327,556.710 u'2. Scattering of light\n'>, 'text': u'2. Scattering of light\n'} 


{'vertical_distance_with_object_above': 0.009900000000016007, 'x1': 150.5717, 'y0': 532.7197, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 544.7097, 'hoverlap': 62.73169999999999, 'x0': 87.84, 'object': <LTTextLineHorizontal 87.840,532.720,150.572,544.710 u'3. Dispersion\n'>, 'text': u'3. Dispersion\n'}



		if next.x0 => previous.x0 and next.y0 <= previous.yo:
			beolongs to this column, whatever it is

		if next.y0 => previous.y0:
				if next.x0 >= previous.x0:
		
		if next.x0 => previous.x0 and next.y0 => previous.yo:
			anamoly for whatever column




#########################################################
############ Anamoly of first column #######################
#########################################################


{'vertical_distance_with_object_above': 0.009899999999959164, 'x1': 302.6319, 'y0': 457.72029999999995, 'horizontal_distance_with_object_above': 60.96879999999999, 'voverlap': 0, 'y1': 469.71029999999996, 'hoverlap': 0, 'x0': 201.6417, 'object': <LTTextLineHorizontal 201.642,457.720,302.632,469.710 u'(b) Remain unaffected\n'>, 'text': u'(b) Remain unaffected\n'} 


{'vertical_distance_with_object_above': 0.009899999999959164, 'x1': 282.5311, 'y0': 445.7204, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 457.7104, 'hoverlap': 80.8894, 'x0': 201.6417, 'object': <LTTextLineHorizontal 201.642,445.720,282.531,457.710 u'(d) Be almost half\n'>, 'text': u'(d) Be almost half\n'} 


{'vertical_distance_with_object_above': 51.0095, 'x1': 274.7266, 'y0': 508.7199, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 520.7099000000001, 'hoverlap': 73.08490000000003, 'x0': 201.6417, 'object': <LTTextLineHorizontal 201.642,508.720,274.727,520.710 u'(b) 1 and 2 only\n'>, 'text': u'(b) 1 and 2 only\n'} 


{'vertical_distance_with_object_above': 0.009900000000016007, 'x1': 285.9884, 'y0': 496.71999999999997, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 508.71, 'hoverlap': 73.08490000000003, 'x0': 201.6417, 'object': <LTTextLineHorizontal 201.642,496.720,285.988,508.710 u'(d) 1, 2 and 3 only\n'>, 'text': u'(d) 1, 2 and 3 only\n'} 


{'vertical_distance_with_object_above': 8.30989999999997, 'x1': 80.6156, 'y0': 476.42010000000005, 'horizontal_distance_with_object_above': 121.02609999999999, 'voverlap': 0, 'y1': 488.4101, 'hoverlap': 0, 'x0': 72.3966, 'object': <LTTextBoxHorizontal(5) 72.397,476.420,80.616,488.410 u'2.\n'>, 'text': u'2.\n'} 

########################################################t
############ second columns proceeds after first column #######################
#########################################################

{'vertical_distance_with_object_above': 0.009900000000016007, 'x1': 314.642, 'y0': 93.2235, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 105.2135, 'hoverlap': 90.66720000000001, 'x0': 87.7524, 'object': <LTTextLineHorizontal 87.752,93.224,314.642,105.213 u'(c) Anywhere, irrespective of the position of the sun\n'>, 'text': u'(c) Anywhere, irrespective of the position of the sun\n'} 


{'vertical_distance_with_object_above': 0.009900000000001796, 'x1': 238.1337, 'y0': 81.2236, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 93.2136, 'hoverlap': 150.3813, 'x0': 87.84, 'object': <LTTextLineHorizontal 87.840,81.224,238.134,93.214 u'(d) Even in the absence of the sun\n'>, 'text': u'(d) Even in the absence of the sun\n'} 


{'vertical_distance_with_object_above': 482.20570000000004, 'x1': 585.2944, 'y0': 575.4193, 'horizontal_distance_with_object_above': 104.62289999999999, 'voverlap': 0, 'y1': 592.2093, 'hoverlap': 0, 'x0': 342.7566, 'object': <LTTextBoxHorizontal(18) 342.757,575.419,585.294,592.209 u'8. When  white  light  passes  through  a  glass  prism,  it\n'>, 'text': u'8. When  white  light  passes  through  a  glass  prism,  it\n'} 


{'vertical_distance_with_object_above': 0, 'x1': 512.6815, 'y0': 568.7194, 'horizontal_distance_with_object_above': 0, 'voverlap': 5.2900999999999385, 'y1': 580.7094, 'hoverlap': 169.92490000000004, 'x0': 358.2, 'object': <LTTextLineHorizontal 358.200,568.719,512.682,580.709 u'gets dispersed into colours because\n'>, 'text': u'gets dispersed into colours because\n'} 


{'vertical_distance_with_object_above': 0.009900000000016007, 'x1': 519.8824000000001, 'y0': 556.7194999999999, 'horizontal_distance_with_object_above': 0, 'voverlap': 0, 'y1': 568.7094999999999, 'hoverlap': 154.48150000000004, 'x0': 358.2, 'object': <LTTextLineHorizontal 358.200,556.719,519.882,568.709 u'(a) Glass imparts colours to the light\n'>, 'text': u'(a) Glass imparts colours to the light\n'} 



################################################################
############ Anamoly of the second column ######################
################################################################

{'text': u'(b) 1 and 2\n', 'object': <LTTextLineHorizontal 472.002,445.720,523.207,457.710 u'(b) 1 and 2\n'>, 'vertical_distance_with_object_above': 0.009900000000016007, 'y1': 457.7104, 'y0': 445.7204, 'x0': 472.0017, 'x1': 523.2073999999999} 


{'text': u'(d) 1 and 4\n', 'object': <LTTextLineHorizontal 472.002,433.720,523.207,445.710 u'(d) 1 and 4\n'>, 'vertical_distance_with_object_above': 0.009900000000016007, 'y1': 445.71049999999997, 'y0': 433.72049999999996, 'x0': 472.0017, 'x1': 523.2073999999999} 


{'text': u'2. Green, orange, red\n', 'object': <LTTextLineHorizontal 472.002,481.720,572.506,493.710 u'2. Green, orange, red\n'>, 'vertical_distance_with_object_above': 36.00970000000001, 'y1': 493.7102, 'y0': 481.7202, 'x0': 472.0017, 'x1': 572.5056} 


{'text': u'4. Blue, green, yellow\n', 'object': <LTTextLineHorizontal 472.002,469.720,574.411,481.710 u'4. Blue, green, yellow\n'>, 'vertical_distance_with_object_above': 0.009900000000016007, 'y1': 481.71029999999996, 'y0': 469.72029999999995, 'x0': 472.0017, 'x1': 574.4114000000001} 


{'text': u'10. The  gap  between  the  irrigation  potential  and  its\n', 'object': <LTTextBoxHorizontal(24) 337.258,413.421,585.297,430.211 u'10. The  gap  between  the  irrigation  potential  and  its\n'>, 'vertical_distance_with_object_above': 39.50959999999998, 'y1': 430.2107, 'y0': 413.4207, 'x0': 337.2576, 'x1': 585.2969999999999} 


#######################################################################################
############ Continuation to the secaond page the same question #######################
#######################################################################################





"""

