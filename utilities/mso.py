'''
Utility classes for interacting with Microsoft Office applications.
(Sorry: platform specific...)

:requires: win32com <http://sourceforge.net/projects/pywin32/>
:license: MIT
:author: Alan G. Isaac
'''
import win32com.client as win32
from time import sleep

class PptPresentation(object):
	'''Simple Python class for creating PowerPoint presentations.
	'''
	def __init__(self, slide_list, **kwargs):
		self.slide_list = slide_list
		self.kwargs = kwargs
	def create_show(self, visible = True):
		import win32com.client as win32
		ppoint = win32.gencache.EnsureDispatch('Powerpoint.Application')
		ppoint.Visible = visible  #bool
		pres = ppoint.Presentations.Add()
		#set a few options
		kwargs = self.kwargs
		slide_master = pres.SlideMaster
		if 'footer' in kwargs: #string
			slide_master.HeadersFooters.Footer.Text = kwargs['footer']
		if 'date_time' in kwargs: #bool
			#turn on or off the DateAndTime field
			slide_master.HeadersFooters.DateAndTime.UseFormat = kwargs['date_time']
		if 'preset_gradient' in kwargs: #3-tuple, e.g. (6, 1, 10)
			slide_master.Background.Fill.PresetGradient(*kwargs['preset_gradient'])
		#insert last slide first
		for slide in reversed(self.slide_list):
			slide.add_slide(pres)


class PptOutline(object):
	'''Bulleted outline with optional title (above).
	Each line of text is bulleted.
	Level of indentation (real tabs) determines outline level.
	'''
	def __init__(self, text, title=''):
		self.text = text
		self.title = title
		self.slide = None
	def add_slide(self, presentation, slide_num=1):
		#create slide
		#  safer to use win32.constants.ppLayoutText as 2nd argument?
		slide = presentation.Slides.Add(slide_num, 2)
		self.slide = slide #currently unused
		sleep(0.25)
		#add text
		text = self.text
		text_range = slide.Shapes[1].TextFrame.TextRange
		#text_range.InsertAfter(self.text)
		for line in text.split("\n"):
			line = line.rstrip()
			indent = 1 + line.count("\t")
			line = line.lstrip()
			if line:
				line = text_range.InsertAfter(line+"\r\n")
				line.IndentLevel = indent
				sleep(0.25)
		#format title
		if self.title:
			#add title
			title_range = slide.Shapes[0].TextFrame.TextRange
			title_range.Text = self.title
			title_range.Font.Bold = True
			sleep(0.25)
		else:
			slide.Shapes[0].Delete()
			slide.Shapes[0].Top = 20
			slide.Shapes[0].Height = 13*36
			

class PptPicture(object):
	'''Slide with picture inserted from file and title.

	:see: http://msdn2.microsoft.com/en-us/library/aa211638(office.11).aspx
	'''
	def __init__(self, file_path, title):
		self.file_path = file_path
		self.title = title
		self.slide = None
	def add_slide(self, presentation, slide_num=1):
		#create slide
		# safer to use win32.constants.ppLayoutTitleOnly for 2nd argument?
		slide = presentation.Slides.Add(slide_num, 11)
		self.slide = slide #currently unused
		sleep(0.2)
		title_range = slide.Shapes[0].TextFrame.TextRange
		title_range.Text = self.title
		title_range.Font.Bold = True
		#position picture 5/8" from left, 1.5" from top
		from_left, from_top = 45, 108  #in points
		shape4picture = slide.Shapes.AddPicture(self.file_path, False, True, from_left, from_top)
		#scale to fit 9" x 5"
		w,h = shape4picture.Width, shape4picture.Height
		print w,h
		scalar = min((9*72)/w,(5*72)/h)
		shape4picture.ScaleHeight(scalar,True)
		sleep(0.25)
		shape4picture.ScaleWidth(scalar,True)
		#center the picture (assumes standard 10" wide slide)
		shape4picture.Left = (720 - shape4picture.Width)/2
		sleep(0.25)
		

class PptBasicTable(object):
	'''Basic PowerPoint table, with optional title.
	If data is R by K, there can be K headers (optional) and R stubs (optional).
	'''
	def __init__(self, data2d, headers=None, stubs=None, title=''):
		self.data = data2d
		self.headers = headers
		self.stubs = stubs
		self.title = title
		self.slide = None
	def add_slide(self, presentation, slide_num=1):
		data, headers, stubs, title = self.data, self.headers, self.stubs, self.title
		data_nrows, data_ncols = len(data), len(data[0])
		row_offset, col_offset = 1, 1
		table_nrows, table_ncols = data_nrows, data_ncols
		if headers:
			row_offset += 1
			table_nrows +=1
		if stubs:
			col_offset += 1
			table_ncols +=1
		#create slide
		#  safer to use win32.constants.ppLayoutTitleOnly as 2nd argument?
		slide = presentation.Slides.Add(slide_num, 11)
		self.slide = slide #currently unused
		sleep(0.1)
		shape4table = slide.Shapes.AddTable(table_nrows, table_ncols)
		sleep(0.1)
		table = shape4table.Table
		#add headers, if any
		if headers:
			for col in range(data_ncols):
				cell = table.Cell(1,col+col_offset)
				cell.Shape.TextFrame.TextRange.Text = str(headers[col])
				sleep(0.1)
		#add stubs, if any
		if stubs:
			for row in range(data_nrows):
				cell = table.Cell(row+row_offset,1)
				cell.Shape.TextFrame.TextRange.Text = str(stubs[row])
				sleep(0.1)
		#fill in table
		for row in range(data_nrows):
			for col in range(data_ncols):
				cell = table.Cell(row+row_offset,col+col_offset)
				cell.Shape.TextFrame.TextRange.Text = str(data[row][col])
				sleep(0.25)
		#format title
		if self.title:
			#add title
			title_range = slide.Shapes[0].TextFrame.TextRange
			title_range.Text = self.title
			title_range.Font.Bold = True
			sleep(0.25)
		else: #no title
			slide.Shapes[0].Delete()
			slide.Shapes[0].Top = 20
			slide.Shapes[0].Height = 13*36


