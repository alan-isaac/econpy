" Vim syntax file
" Language:	EViews
" Maintainer:	Alan Isaac <aisaac@american.edu>
" URL:		http://www.american.edu/econ/notes/eviews.vim
" Last Change:	2002 March 30


" Remove any old syntax stuff hanging around
syn clear
syn case ignore

if !exists("main_syntax")
  let main_syntax = 'eviews'
endif

let b:current_syntax = "eviews"

sy region eVrPar3 matchgroup=eVrPar3 start=/(/ end=/)/ contains=ALLBUT,eVmParenError contained
sy region eVrPar2 matchgroup=eVrPar2 start=/(/ end=/)/ contains=eVrPar3,eVmOperator,eVmCtr,eVmStringVar,eVrBraces contained
sy region eVrPar1 matchgroup=eVrPar1 start=/(/  end=/)/ contains=eVrPar2,eVmOperator,eVmCtr,eVmStringVar,eVrBraces
hi eVrPar1 ctermfg=darkgreen guifg=darkgreen
hi eVrPar2 ctermfg=blue guifg=blue
hi eVrPar3 ctermfg=red guifg=red

syn match   eVmLineComment      "'.*$"
syn match   eVmNumber           "=\=\s*-\=\d\+\.\=\d*"
syn match   eVmOperator           "[*/+-><^]"
syn match   eVmStringVar          "%[a-zA-Z0-9]\+"
syn match   eVmCtr                "{\=![a-zA-Z0-9]\+}\="
syn region  eVRepeat           start="for\s\+" skip="'.*$" end="next" contains=ALL
syn region  eVStringD          start=+"+  skip=+\\\\\|\\"+  end=+"+  
syn region  eVStringL          matchgroup=eVrPar1 start='[dt]([^-]*)'  end=+$+ contains=eVmLineComment,eVmOperator,eVkOperator keepend
syn keyword eVkConditional      if then else endif 
syn keyword eVkRepeat           while wend for to next exitloop
syn keyword eVkOperator         and or
syn keyword eVkFunction         subroutine
syn keyword eVkBoolean          true false

" catch errors caused by wrong parenthesis
syn region  eVrParen       transparent start="(" end=")" contains=ALLBUT,eVmParenError
syn match   eVmParenError  ")"
syn region  eVrBraces       transparent start="{" end="}" contains=ALLBUT,eVmBracesError
syn match   eVmBracesError  "}"
syn region  eVrBracket      transparent start="[[]" end="]" contains=ALLBUT,eVmBracketError
syn match   eVmBracketError  "]"

syn keyword eVkObject graph group matrix pool table series scalar var vector text equation workfile sym 
hi eVkObject ctermfg=blue guifg=red
syn keyword eVkUnitHeader	call function program local subroutine
syn keyword eVkStatement	return stop

syn keyword eVkStatement add align append ar arch archtest auto 
syn keyword eVkStatement bar 
syn keyword eVkStatement cause ccopy cd cdfplot ceiling censored cfetch chow clabel close coef coefcov coint copy cor correl correlsq count cov cross cusum 
syn keyword eVkStatement dbcopy dbcreate dbdelete dbopen dbpack dbrebuild dbrename dbrepair decomp define delete describe driconvert drop dtable 
syn keyword eVkStatement ec endog expand 
syn keyword eVkStatement fetch fill fiml fit freeze freq 
syn keyword eVkStatement garch genr gmm 
syn keyword eVkStatement hconvert hilo hist hpf 
syn keyword eVkStatement impulse include 
syn keyword eVkStatement kdensity kerfit 
syn keyword eVkStatement label line linefit ls lstyle 
syn keyword eVkStatement ma makeendog makegarch makegroup makelimit makemodel makeregs makeresid makestat makestate makesystem metafile ml model mtos 
syn keyword eVkStatement name nnfit nrnd 
syn keyword eVkStatement option ordered 
syn keyword eVkStatement param pdl pi pie poff pon predict print 
syn keyword eVkStatement qqplot 
syn keyword eVkStatement range rename reset residcor residcov resids results rls rnd rndint rndseed 
syn keyword eVkStatement sar scale scat scatmat seas set setcell setcolwidth setconvert setelem setline shade sheet show sma smooth smpl solve sort spec sspace statby state stats statusline stom stomna sur 
syn keyword eVkStatement testadd testbtw testby testdrop testfit teststat tsls 
syn keyword eVkStatement uroot 
syn keyword eVkStatement wald white wls write wtsls 
syn keyword eVkStatement x11 xy 
syn keyword eVkStatement @aic @all @cchisq @coefcov @coefs @count @dw @f @first @jstat @last @left @logl @meandep @ncoef @obs @qchisq @r2 @rbar2 @regobs @right @schwarz @sddep @se @seriesname @ssr @stderrs @str @strlen @sysncoef @trend @tstats 
syn keyword eVkStatement addtext call create displayname exit legend load merge new open read run sample save step stop store system 
syn keyword eVkOperator d log dlog
syn keyword eVkOption dat mult na skiprow rect t 

    syn match   eVkUnitHeader	"end\s*sub"

if !exists("did_eviews_syntax_inits")
  let did_eviews_syntax_inits = 1
  hi link eVmLineComment       Comment
  hi link eVStringD           String
  hi link eVStringL           String
  hi link eVStringA           String
  hi link eVmNumber            eVValue
  hi link eVkConditional       Conditional
  hi link eVkRepeat            Repeat
  hi link eVkBranch            Conditional
  hi link eVkOperator          Operator
  hi link eVmOperator          Operator
  hi link eVmStringVar         Identifier 
  hi link eVmCtr               Identifier
  hi link eVkType              Type
  hi link eVkStatement         Statement
  hi link eVkFunction          Function
  hi link eVrBraces            Function
  hi link eVrBracket            Function
  hi link eVError             Error
  hi link eVmParenError        eVError
  hi link eVmBracesError       eVError
  hi link eVmBracketError      eVError
  hi link eVInParen           eVError
  hi link eVBoolean           Boolean
endif

let b:current_syntax = "eviews"
if main_syntax == 'eviews'
  unlet main_syntax
endif

" vim: ts=8
