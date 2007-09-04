'''
Utility classes for interacting with Microsoft Office applications.
(Sorry: platform specific...)

:requires: win32com <http://sourceforge.net/projects/pywin32/>
:license: MIT
:author: Alan G. Isaac
'''
import win32com.client as win32
from time import sleep
#DEFINE PowerPoint constants (Many available in win32com.client.constants!)
ppWindowNormal = 1
ppWindowMinimized = 2
ppWindowMaximized = 3
ppArrangeTiled = 1
ppArrangeCascade = 2
ppViewSlide = 1
ppViewSlideMaster = 2
ppViewNotesPage = 3
ppViewHandoutMaster = 4
ppViewNotesMaster = 5
ppViewOutline = 6
ppViewSlideSorter = 7
ppViewTitleMaster = 8
ppViewNormal = 9
ppViewPrintPreview = 10
ppViewThumbnails = 11
ppViewMasterThumbnails = 12
ppSchemeColorMixed = -2
ppNotSchemeColor = 0
ppBackground = 1
ppForeground = 2
ppShadow = 3
ppTitle = 4
ppFill = 5
ppAccent1 = 6
ppAccent2 = 7
ppAccent3 = 8
ppSlideSizeOnScreen = 1
ppSlideSizeLetterPaper = 2
ppSlideSizeA4Paper = 3
ppSlideSize35MM = 4
ppSlideSizeOverhead = 5
ppSlideSizeBanner = 6
ppSlideSizeCustom = 7
ppSlideSizeLedgerPaper = 8
ppSlideSizeA3Paper = 9
ppSlideSizeB4ISOPaper = 10
ppSlideSizeB5ISOPaper = 11
ppSlideSizeB4JISPaper = 12
ppSlideSizeB5JISPaper = 13
ppSlideSizeHagakiCard = 14
ppSaveAsPresentation = 1
ppSaveAsPowerPoint7 = 2
ppSaveAsPowerPoint4 = 3
ppSaveAsPowerPoint3 = 4
ppSaveAsTemplate = 5
ppSaveAsRTF = 6
ppSaveAsShow = 7
ppSaveAsAddIn = 8
ppSaveAsPowerPoint4FarEast = 10
ppSaveAsDefault = 11
ppSaveAsHTML = 12
ppSaveAsHTMLv3 = 13
ppSaveAsHTMLDual = 14
ppSaveAsMetaFile = 15
ppSaveAsGIF = 16
ppSaveAsJPG = 17
ppSaveAsPNG = 18
ppSaveAsBMP = 19
ppSaveAsWebArchive = 20
ppSaveAsTIF = 21
ppSaveAsPresForReview = 22
ppSaveAsEMF = 23
ppDefaultStyle = 1
ppTitleStyle = 2
ppBodyStyle = 3
ppLayoutMixed = -2
ppLayoutTitle = 1
ppLayoutText = 2
ppLayoutTwoColumnText = 3
ppLayoutTable = 4
ppLayoutTextAndChart = 5
ppLayoutChartAndText = 6
ppLayoutOrgchart = 7
ppLayoutChart = 8
ppLayoutTextAndClipart = 9
ppLayoutClipartAndText = 10
ppLayoutTitleOnly = 11
ppLayoutBlank = 12
ppLayoutTextAndObject = 13
ppLayoutObjectAndText = 14
ppLayoutLargeObject = 15
ppLayoutObject = 16
ppLayoutTextAndMediaClip = 17
ppLayoutMediaClipAndText = 18
ppLayoutObjectOverText = 19
ppLayoutTextOverObject = 20
ppLayoutTextAndTwoObjects = 21
ppLayoutTwoObjectsAndText = 22
ppLayoutTwoObjectsOverText = 23
ppLayoutFourObjects = 24
ppLayoutVerticalText = 25
ppLayoutClipArtAndVerticalText = 26
ppLayoutVerticalTitleAndText = 27
ppLayoutVerticalTitleAndTextOverChart = 28
ppLayoutTwoObjects = 29
ppLayoutObjectAndTwoObjects = 30
ppLayoutTwoObjectsAndObject = 31
ppEffectMixed = -2
ppEffectNone = 0
ppEffectCut = 257
ppEffectCutThroughBlack = 258
ppEffectRandom = 513
ppEffectBlindsHorizontal = 769
ppEffectBlindsVertical = 770
ppEffectCheckerboardAcross = 1025
ppEffectCheckerboardDown = 1026
ppEffectCoverLeft = 1281
ppEffectCoverUp = 1282
ppEffectCoverRight = 1283
ppEffectCoverDown = 1284
ppEffectCoverLeftUp = 1285
ppEffectCoverRightUp = 1286
ppEffectCoverLeftDown = 1287
ppEffectCoverRightDown = 1288
ppEffectDissolve = 1537
ppEffectFade = 1793
ppEffectUncoverLeft = 2049
ppEffectUncoverUp = 2050
ppEffectUncoverRight = 2051
ppEffectUncoverDown = 2052
ppEffectUncoverLeftUp = 2053
ppEffectUncoverRightUp = 2054
ppEffectUncoverLeftDown = 2055
ppEffectUncoverRightDown = 2056
ppEffectRandomBarsHorizontal = 2305
ppEffectRandomBarsVertical = 2306
ppEffectStripsUpLeft = 2561
ppEffectStripsUpRight = 2562
ppEffectStripsDownLeft = 2563
ppEffectStripsDownRight = 2564
ppEffectStripsLeftUp = 2565
ppEffectStripsRightUp = 2566
ppEffectStripsLeftDown = 2567
ppEffectStripsRightDown = 2568
ppEffectWipeLeft = 2817
ppEffectWipeUp = 2818
ppEffectWipeRight = 2819
ppEffectWipeDown = 2820
ppEffectBoxOut = 3073
ppEffectBoxIn = 3074
ppEffectFlyFromLeft = 3329
ppEffectFlyFromTop = 3330
ppEffectFlyFromRight = 3331
ppEffectFlyFromBottom = 3332
ppEffectFlyFromTopLeft = 3333
ppEffectFlyFromTopRight = 3334
ppEffectFlyFromBottomLeft = 3335
ppEffectFlyFromBottomRight = 3336
ppEffectPeekFromLeft = 3337
ppEffectPeekFromDown = 3338
ppEffectPeekFromRight = 3339
ppEffectPeekFromUp = 3340
ppEffectCrawlFromLeft = 3341
ppEffectCrawlFromUp = 3342
ppEffectCrawlFromRight = 3343
ppEffectCrawlFromDown = 3344
ppEffectZoomIn = 3345
ppEffectZoomInSlightly = 3346
ppEffectZoomOut = 3347
ppEffectZoomOutSlightly = 3348
ppEffectZoomCenter = 3349
ppEffectZoomBottom = 3350
ppEffectStretchAcross = 3351
ppEffectStretchLeft = 3352
ppEffectStretchUp = 3353
ppEffectStretchRight = 3354
ppEffectStretchDown = 3355
ppEffectSwivel = 3356
ppEffectSpiral = 3357
ppEffectSplitHorizontalOut = 3585
ppEffectSplitHorizontalIn = 3586
ppEffectSplitVerticalOut = 3587
ppEffectSplitVerticalIn = 3588
ppEffectFlashOnceFast = 3841
ppEffectFlashOnceMedium = 3842
ppEffectFlashOnceSlow = 3843
ppEffectAppear = 3844
ppEffectCircleOut = 3845
ppEffectDiamondOut = 3846
ppEffectCombHorizontal = 3847
ppEffectCombVertical = 3848
ppEffectFadeSmoothly = 3849
ppEffectNewsflash = 3850
ppEffectPlusOut = 3851
ppEffectPushDown = 3852
ppEffectPushLeft = 3853
ppEffectPushRight = 3854
ppEffectPushUp = 3855
ppEffectWedge = 3856
ppEffectWheel1Spoke = 3857
ppEffectWheel2Spokes = 3858
ppEffectWheel3Spokes = 3859
ppEffectWheel4Spokes = 3860
ppEffectWheel8Spokes = 3861
ppAnimateLevelMixed = -2
ppAnimateLevelNone = 0
ppAnimateByFirstLevel = 1
ppAnimateBySecondLevel = 2
ppAnimateByThirdLevel = 3
ppAnimateByFourthLevel = 4
ppAnimateByFifthLevel = 5
ppAnimateByAllLevels = 16
ppAnimateUnitMixed = -2
ppAnimateByParagraph = 0
ppAnimateByWord = 1
ppAnimateByCharacter = 2
ppAnimateChartMixed = -2
ppAnimateBySeries = 1
ppAnimateByCategory = 2
ppAnimateBySeriesElements = 3
ppAnimateByCategoryElements = 4
ppAnimateChartAllAtOnce = 5
ppAfterEffectMixed = -2
ppAfterEffectNothing = 0
ppAfterEffectHide = 1
ppAfterEffectDim = 2
ppAfterEffectHideOnClick = 3
ppAdvanceModeMixed = -2
ppAdvanceOnClick = 1
ppAdvanceOnTime = 2
ppSoundEffectsMixed = -2
ppSoundNone = 0
ppSoundStopPrevious = 1
ppSoundFile = 2
ppFollowColorsMixed = -2
ppFollowColorsNone = 0
ppFollowColorsScheme = 1
ppFollowColorsTextAndBackground = 2
ppUpdateOptionMixed = -2
ppUpdateOptionManual = 1
ppUpdateOptionAutomatic = 2
ppAlignmentMixed = -2
ppAlignLeft = 1
ppAlignCenter = 2
ppAlignRight = 3
ppAlignJustify = 4
ppAlignDistribute = 5
ppAlignThaiDistribute = 6
ppAlignJustifyLow = 7
ppBaselineAlignMixed = -2
ppBaselineAlignBaseline = 1
ppBaselineAlignTop = 2
ppBaselineAlignCenter = 3
ppBaselineAlignFarEast50 = 4
ppTabStopMixed = -2
ppTabStopLeft = 1
ppTabStopCenter = 2
ppTabStopRight = 3
ppTabStopDecimal = 4
ppIndentControlMixed = -2
ppIndentReplaceAttr = 1
ppIndentKeepAttr = 2
ppCaseSentence = 1
ppCaseLower = 2
ppCaseUpper = 3
ppCaseTitle = 4
ppCaseToggle = 5
ppSlideShowPointerNone = 0
ppSlideShowPointerArrow = 1
ppSlideShowPointerPen = 2
ppSlideShowPointerAlwaysHidden = 3
ppSlideShowPointerAutoArrow = 4
ppSlideShowRunning = 1
ppSlideShowPaused = 2
ppSlideShowBlackScreen = 3
ppSlideShowWhiteScreen = 4
ppSlideShowDone = 5
ppSlideShowManualAdvance = 1
ppSlideShowUseSlideTimings = 2
ppSlideShowRehearseNewTimings = 3
ppFileDialogOpen = 1
ppFileDialogSave = 2
ppPrintOutputSlides = 1
ppPrintOutputTwoSlideHandouts = 2
ppPrintOutputThreeSlideHandouts = 3
ppPrintOutputSixSlideHandouts = 4
ppPrintOutputNotesPages = 5
ppPrintOutputOutline = 6
ppPrintOutputBuildSlides = 7
ppPrintOutputFourSlideHandouts = 8
ppPrintOutputNineSlideHandouts = 9
ppPrintOutputOneSlideHandouts = 10
ppPrintHandoutVerticalFirst = 1
ppPrintHandoutHorizontalFirst = 2
ppPrintColor = 1
ppPrintBlackAndWhite = 2
ppPrintPureBlackAndWhite = 3
ppSelectionNone = 0
ppSelectionSlides = 1
ppSelectionShapes = 2
ppSelectionText = 3
ppDirectionMixed = -2
ppDirectionLeftToRight = 1
ppDirectionRightToLeft = 2
ppDateTimeFormatMixed = -2
ppDateTimeMdyy = 1
ppDateTimeddddMMMMddyyyy = 2
ppDateTimedMMMMyyyy = 3
ppDateTimeMMMMdyyyy = 4
ppDateTimedMMMyy = 5
ppDateTimeMMMMyy = 6
ppDateTimeMMyy = 7
ppDateTimeMMddyyHmm = 8
ppDateTimeMMddyyhmmAMPM = 9
ppDateTimeHmm = 10
ppDateTimeHmmss = 11
ppDateTimehmmAMPM = 12
ppDateTimehmmssAMPM = 13
ppDateTimeFigureOut = 14
ppTransitionSpeedMixed = -2
ppTransitionSpeedSlow = 1
ppTransitionSpeedMedium = 2
ppTransitionSpeedFast = 3
ppMouseClick = 1
ppMouseOver = 2
ppActionMixed = -2
ppActionNone = 0
ppActionNextSlide = 1
ppActionPreviousSlide = 2
ppActionFirstSlide = 3
ppActionLastSlide = 4
ppActionLastSlideViewed = 5
ppActionEndShow = 6
ppActionHyperlink = 7
ppActionRunMacro = 8
ppActionRunProgram = 9
ppActionNamedSlideShow = 10
ppActionOLEVerb = 11
ppActionPlay = 12
ppPlaceholderMixed = -2
ppPlaceholderTitle = 1
ppPlaceholderBody = 2
ppPlaceholderCenterTitle = 3
ppPlaceholderSubtitle = 4
ppPlaceholderVerticalTitle = 5
ppPlaceholderVerticalBody = 6
ppPlaceholderObject = 7
ppPlaceholderChart = 8
ppPlaceholderBitmap = 9
ppPlaceholderMediaClip = 10
ppPlaceholderOrgChart = 11
ppPlaceholderTable = 12
ppPlaceholderSlideNumber = 13
ppPlaceholderHeader = 14
ppPlaceholderFooter = 15
ppPlaceholderDate = 16
ppShowTypeSpeaker = 1
ppShowTypeWindow = 2
ppShowTypeKiosk = 3
ppPrintAll = 1
ppPrintSelection = 2
ppPrintCurrent = 3
ppPrintSlideRange = 4
ppPrintNamedSlideShow = 5
ppAutoSizeMixed = -2
ppAutoSizeNone = 0
ppAutoSizeShapeToFitText = 1
ppMediaTypeMixed = -2
ppMediaTypeOther = 1
ppMediaTypeSound = 2
ppMediaTypeMovie = 3
ppSoundFormatMixed = -2
ppSoundFormatNone = 0
ppSoundFormatWAV = 1
ppSoundFormatMIDI = 2
ppSoundFormatCDAudio = 3
ppFarEastLineBreakLevelNormal = 1
ppFarEastLineBreakLevelStrict = 2
ppFarEastLineBreakLevelCustom = 3
ppShowAll = 1
ppShowSlideRange = 2
ppShowNamedSlideShow = 3
ppFrameColorsBrowserColors = 1
ppFrameColorsPresentationSchemeTextColor = 2
ppFrameColorsPresentationSchemeAccentColor = 3
ppFrameColorsWhiteTextOnBlack = 4
ppFrameColorsBlackTextOnWhite = 5
ppBorderTop = 1
ppBorderLeft = 2
ppBorderBottom = 3
ppBorderRight = 4
ppBorderDiagonalDown = 5
ppBorderDiagonalUp = 6
ppHTMLv3 = 1
ppHTMLv4 = 2
ppHTMLDual = 3
ppHTMLAutodetect = 4
ppPublishAll = 1
ppPublishSlideRange = 2
ppPublishNamedSlideShow = 3
ppBulletMixed = -2
ppBulletNone = 0
ppBulletUnnumbered = 1
ppBulletNumbered = 2
ppBulletPicture = 3
ppBulletStyleMixed = -2
ppBulletAlphaLCPeriod = 0
ppBulletAlphaUCPeriod = 1
ppBulletArabicParenRight = 2
ppBulletArabicPeriod = 3
ppBulletRomanLCParenBoth = 4
ppBulletRomanLCParenRight = 5
ppBulletRomanLCPeriod = 6
ppBulletRomanUCPeriod = 7
ppBulletAlphaLCParenBoth = 8
ppBulletAlphaLCParenRight = 9
ppBulletAlphaUCParenBoth = 10
ppBulletAlphaUCParenRight = 11
ppBulletArabicParenBoth = 12
ppBulletArabicPlain = 13
ppBulletRomanUCParenBoth = 14
ppBulletRomanUCParenRight = 15
ppBulletSimpChinPlain = 16
ppBulletSimpChinPeriod = 17
ppBulletCircleNumDBPlain = 18
ppBulletCircleNumWDWhitePlain = 19
ppBulletCircleNumWDBlackPlain = 20
ppBulletTradChinPlain = 21
ppBulletTradChinPeriod = 22
ppBulletArabicAlphaDash = 23
ppBulletArabicAbjadDash = 24
ppBulletHebrewAlphaDash = 25
ppBulletKanjiKoreanPlain = 26
ppBulletKanjiKoreanPeriod = 27
ppBulletArabicDBPlain = 28
ppBulletArabicDBPeriod = 29
ppBulletThaiAlphaPeriod = 30
ppBulletThaiAlphaParenRight = 31
ppBulletThaiAlphaParenBoth = 32
ppBulletThaiNumPeriod = 33
ppBulletThaiNumParenRight = 34
ppBulletThaiNumParenBoth = 35
ppBulletHindiAlphaPeriod = 36
ppBulletHindiNumPeriod = 37
ppBulletKanjiSimpChinDBPeriod = 38
ppBulletHindiNumParenRight = 39
ppBulletHindiAlpha1Period = 40
ppShapeFormatGIF = 0
ppShapeFormatJPG = 1
ppShapeFormatPNG = 2
ppShapeFormatBMP = 3
ppShapeFormatWMF = 4
ppShapeFormatEMF = 5
ppRelativeToSlide = 1
ppClipRelativeToSlide = 2
ppScaleToFit = 3
ppScaleXY = 4
ppPasteDefault = 0
ppPasteBitmap = 1
ppPasteEnhancedMetafile = 2
ppPasteMetafilePicture = 3
ppPasteGIF = 4
ppPasteJPG = 5
ppPastePNG = 6
ppPasteText = 7
ppPasteHTML = 8
ppPasteRTF = 9
ppPasteOLEObject = 10
ppPasteShape = 11


class PptPresentation(object):
	'''Simple Python class for creating PowerPoint presentations.
	'''
	def __init__(self, slide_list, **kwargs):
		self.slide_list = slide_list
		self.kwargs = kwargs
		self.ppt = None
		self.ppt_presentation = None
	def create_show(self, visible = True):
		import win32com.client as win32
		ppt = win32.gencache.EnsureDispatch('Powerpoint.Application')
		self.ppt = ppt
		ppt.Visible = visible  #bool
		presentation = ppt.Presentations.Add()
		self.presentation = presentation
		#set a few options
		kwargs = self.kwargs
		slide_master = presentation.SlideMaster
		if 'footer' in kwargs: #string
			slide_master.HeadersFooters.Footer.Text = kwargs['footer']
		if 'date_time' in kwargs: #bool
			#turn on or off the DateAndTime field
			slide_master.HeadersFooters.DateAndTime.UseFormat = kwargs['date_time']
		if 'preset_gradient' in kwargs: #3-tuple, e.g. (6, 1, 10)
			slide_master.Background.Fill.PresetGradient(*kwargs['preset_gradient'])
		#insert last slide first
		for slide in reversed(self.slide_list):
			slide.add_slide(presentation)
			if visible:
				slide.select() #bring slide to front
			slide.format_slide()
	def save_as(self, file_name):
		self.presentation.SaveAs(file_name)
	def close(self):
		self.presentation.Close()
	def ppt_quit(self):
		self.ppt.Quit()
		


class PptTitleSlide(object):
	def add_slide(self, presentation, slide_num=1):
		#create slide
		slide = presentation.Slides.Add(slide_num, self.layout)
		self.slide = slide
		sleep(0.1)
	def select(self):
		self.slide.Select()
	def format_slide(self):
		self.format_content()
		self.format_title()
	def format_title(self):
		slide = self.slide
		if self.title:
			#add title
			#title_range = slide.Shapes[0].TextFrame.TextRange
			title_range = slide.Shapes.Title.TextFrame.TextRange
			title_range.Text = self.title
			title_range.Font.Bold = True
			sleep(0.10)
		else:
			#slide.Shapes[0].Delete()
			slide.Shapes.Title.Delete()
			slide.Shapes[0].Top = 20
			slide.Shapes[0].Height = 13*36
		

class PptOutline(PptTitleSlide):
	'''Bulleted outline with optional title (above).
	Each line of text is bulleted.
	Level of indentation (real tabs) determines outline level.
	'''
	def __init__(self, text, title=''):
		self.text = text
		self.title = title
		self.slide = None
		self.layout = ppLayoutText
	def format_content(self):
		slide = self.slide
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
				sleep(0.10)
			

class PptPicture(PptTitleSlide):
	'''Slide with picture inserted from file and title.

	:see: http://msdn2.microsoft.com/en-us/library/aa211638(office.11).aspx
	'''
	def __init__(self, file_path, title):
		self.file_path = file_path
		self.title = title
		self.slide = None
		self.layout = ppLayoutTitleOnly
	def format_content(self):
		slide = self.slide
		#title_range = slide.Shapes[0].TextFrame.TextRange
		title_range = slide.Shapes.Title.TextFrame.TextRange
		title_range.Text = self.title
		title_range.Font.Bold = True
		#position picture 5/8" from left, 1.5" from top
		from_left, from_top = 45, 108  #in points
		shape4picture = slide.Shapes.AddPicture(self.file_path, False, True, from_left, from_top)
		#scale to fit 9" x 5"
		w,h = shape4picture.Width, shape4picture.Height
		scalar = min((9*72)/w,(5*72)/h)
		shape4picture.ScaleHeight(scalar,True)
		sleep(0.10)
		shape4picture.ScaleWidth(scalar,True)
		#center the picture (assumes standard 10" wide slide)
		shape4picture.Left = (720 - shape4picture.Width)/2
		sleep(0.10)
		

class PptBasicTable(PptTitleSlide):
	'''Basic PowerPoint table, with optional title.
	If data is R by K, there can be K headers (optional) and R stubs (optional).
	'''
	def __init__(self, data2d, headers=None, stubs=None, title=''):
		self.data = data2d
		self.headers = headers
		self.stubs = stubs
		self.title = title
		self.slide = None
		self.layout = ppLayoutTitleOnly
	def format_content(self):
		slide = self.slide
		#preliminary computations
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
		#add shape to hold table
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
				sleep(0.10)
		#format title
		if self.title:
			#add title
			title_range = slide.Shapes[0].TextFrame.TextRange
			title_range.Text = self.title
			title_range.Font.Bold = True
			sleep(0.10)
		else: #no title
			slide.Shapes[0].Delete()
			slide.Shapes[0].Top = 20
			slide.Shapes[0].Height = 13*36


