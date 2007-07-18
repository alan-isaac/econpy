" Vim syntax file
" Language:	GAUSS
" Maintainer:	Alan Isaac <aisaac@american.edu>
" URL:		http://www.american.edu/econ/notes/gauss.vim
" Last Change:	2002 March 30


" Remove any old syntax stuff hanging around
syn clear
syn case ignore

if !exists("main_syntax")
  let main_syntax = 'gauss'
endif





" StringEsc = \



sy region GAUrPar3 matchgroup=GAUrPar3 start=/(/ end=/)/ contains=ALLBUT,GAUmParenError contained
sy region GAUrPar2 matchgroup=GAUrPar2 start=/(/ end=/)/ contains=GAUrPar3,GAUmOperator,GAUmCtr,GAUmStringVar,GAUrBraces contained
sy region GAUrPar1 matchgroup=GAUrPar1 start=/(/  end=/)/ contains=GAUrPar2,GAUmOperator,GAUmCtr,GAUmStringVar,GAUrBraces
hi GAUrPar1 ctermfg=darkgreen guifg=darkgreen
hi GAUrPar2 ctermfg=blue guifg=blue
hi GAUrPar3 ctermfg=red guifg=red


" won't work because of operators; see c.vim
syntax region GAUmComment	matchgroup=CommentStart start="/\*" matchgroup=NONE end="\*/" 
syntax region GAUmComment2	matchgroup=CommentStart start="@" matchgroup=NONE end="@" 
syntax match GAUmPreProc	"#\S\+"
syn match   GAUmNumber           "=\=\s*-\=\d\+\.\=\d*"
syn match   GAUmOperator           "[*/+-><^!~%^&|=.:;,$?]"
syn region  GAURepeat           start="for\s*(" skip="'.*$" end="endfor" contains=ALL
syn region  GAUStringD          start=+"+  skip=+\\\\\|\\"+  end=+"+  
syn keyword GAUkConditional      if then else endif elseif 
syn keyword GAUkRepeat           while for do endo endfor
syn keyword GAUkOperator         and or .and .or

" catch errors caused by wrong parenthesis
syn region  GAUrParen       transparent start="(" end=")" contains=ALLBUT,GAUmParenError
syn match   GAUmParenError  ")"
syn region  GAUrBraces       transparent start="{" end="}" contains=ALLBUT,GAUmBracesError
syn match   GAUmBracesError  "}"
syn region  GAUrBracket      transparent start="[[]" end="]" contains=ALLBUT,GAUmBracketError
syn match   GAUmBracketError  "]"

syn keyword GAUkDeclare	call fn proc local 
syn keyword GAUkStatement	return stop

syn keyword GAUkStatement _daypryr _dstatd _dstatx _isleap 
syn keyword GAUkStatement abs arccos arcsin arctan arctan2 asclabel atan atan2 axmargin
syn keyword GAUkStatement balance band bandchol bandcholsol bandltsol bandrv bandsolpd bar base10 begwind besselj bessely box break
syn keyword GAUkStatement call cdfbeta cdfbvn cdfbvn2 cdfbvn2e cdfchic cdfchii cdfchinc cdffc cdffnc cdfgam cdfmvn cdfn cdfn2 cdfnc cdfni cdftc cdftci cdftnc cdftvn cdir ceil cfft cffti ChangeDir chdir chol choldn cholsol cholup chrs cint clear clearg close closeall cls cmadd cmcplx cmcplx2 cmdiv cmemult cmimag cminv cmmult cmreal cmsoln cmsub cmtrans code color cols colsf comlog compile complex con cond conj cons continue contour conv coreleft corrm corrvc corrx cos cosh counts countwts create crossprd crout croutp csrcol csrlin csrtype cumprodc cumsumc
syn keyword GAUkStatement datalist date datestr datestring datestrymd dayinyr debug declare delete delif denseSubmat design det detl dfft dffti dfree diag diagrv disable dlibrary dllcall dos doswin DOSWinCloseall DOSWinOpen draw dstat dummy dummybr dummydn
syn keyword GAUkStatement ed edit editm eig eigcg eigcg2 eigch eigch2 eigh eighv eigrg eigrg2 eigrs eigrs2 eigv enable end endp endwind envget eof eqSolve erf erfc error errorlog etdays ethsec etstr exctsmpl exec exp export exportf external eye
syn keyword GAUkStatement fcheckerr fclearerr feq fflush fft ffti fftm fftmi fftn fge fgets fgetsa fgetsat fgetst fgt fileinfo files filesa fix fle floor flt fmod fne fonts fopen for format formatcv formatnv fputs fputst fseek fstrerror ftell ftocv ftos
syn keyword GAUkStatement gamma gammaii gausset getf getname getnr getpath getwind gosub goto gradp graph graphprt graphset
syn keyword GAUkStatement hardcopy hasimag header hess hessp hist histf histp hsec
syn keyword GAUkStatement if imag import importf indcv indexcat indices indices2 indnv int intgrat2 intgrat3 intquad1 intquad2 intquad3 intrleav intrsect intsimp inv invpd invswp iscplx iscplxf ismiss isSparse
syn keyword GAUkStatement key keyw keyword
syn keyword GAUkStatement lag1 lagn let lib library line ln lncdfbvn lncdfbvn2 lncdfmvn lncdfn lncdfn2 lncdfnc lnfact lnpdfmvn lnpdfn load loadd loadf loadk loadm loadp loads loadwind local locate loess log loglog logx logy lower lowmat lowmat1 lpos lprint lpwidth lshow ltrisol lu lusol
syn keyword GAUkStatement makevars makewind margin maxc maxindc maxvec mbesselei mbesselei0 mbesselei1 mbesseli mbesseli0 mbesseli1 meanc median mergeby mergevar minc minindc miss missex missrv moment momentd msym
syn keyword GAUkStatement nametype ndpchk ndpclex ndpcntrl new nextn nextnevn nextwind null null1
syn keyword GAUkStatement ols olsqr olsqr2 ones open optn optnevn orth output outwidth
syn keyword GAUkStatement packr parse pause pdfn pi pinv plot plotsym polar polychar polyeval polyint polymake polymat polymult polyroot pop pqgwin prcsn print printdos printfm printfmt prodc putf
syn keyword GAUkStatement QProg qqr qqre qqrep qr qre qrep qrsol qrtsol qtyr qtyre qtyrep quantile quantiled qyr qyre qyrep
syn keyword GAUkStatement rank rankindx readr real recode recserar recsercp recserrc replay rerun reshape retp rev rfft rffti rfftip rfftn rfftnp rfftp rndbeta rndcon rndgam rndmod rndmult rndn rndnb rndns rndp rndseed rndu rndus rndvm rotater round rows rowsf rref run
syn keyword GAUkStatement save saveall saved savewind scale scale3d scalerr scalmiss schtoc schur screen scroll seekr selif seqa seqm setcnvrt setdif setvars setvmode setwind shell shiftr show sin sinh sleep solpd sortc sortcc sortd sorthc sorthcc sortind sortindc sortmc sparseCols sparseEye sparseFD sparseFP sparseHConcat sparseNZE sparseOnes sparseRows sparseSolve sparseSubmat sparseTD sparseTrTD sparseVConcat spline1D spline2D sqpSolve sqrt stdc stof strindx strlen strput strrindx strsect submat subscat substute sumc surface svd svd1 svd2 svdcusv svds svdusv sysstate system
syn keyword GAUkStatement tab tan tanh tempname time timestr title toeplitz token trace trap trapchk trim trimr trunc type typecv typef
syn keyword GAUkStatement union uniqindx unique until upmat upmat1 upper use utrisol
syn keyword GAUkStatement vals varget vargetl varput varputl vartype vcm vcx vec vech vecr vget view viewxyz vlist vnamecv volume vput vread vtypecv
syn keyword GAUkStatement wait waitc window writer
syn keyword GAUkStatement xlabel xpnd xtics xy xyz
syn keyword GAUkStatement ylabel ytics
syn keyword GAUkStatement zeros zlabel ztics 

syn keyword GAUkStatement co coset coprt gradre gradfd gradcd cml cmlset cmlprt cmlclprt cmltlimits cmlhist cmldensity cmlboot cmlblimits cmlclimits cmlprofile cmlbayes cmlpflclimits


" if !exists("did_gauss_syntax_inits")
  let did_gauss_syntax_inits = 1
  hi link GAUmComment       Comment
  hi link GAUmComment2       Comment
  hi link GAUStringD           String
  hi link GAUmNumber            Float
  hi link GAUkRepeat            Repeat
  hi link GAUkBranch            Conditional
  hi link GAUkConditional       Conditional
  hi link GAUkOperator          Operator
  hi link GAUmOperator          Operator
  hi link GAUmStringVar         Identifier 
  hi link GAUmCtr               Identifier
  hi link GAUkType              Type
  hi link GAUkStatement         Statement
  hi link GAUmPreProc         PreProc
  hi link GAUkDeclare	        Statement
  hi link GAUrBraces            Function
  hi link GAUrBracket            Function
  hi link GAUError             Error
  hi link GAUmParenError        GAUError
  hi link GAUmBracesError       GAUError
  hi link GAUmBracketError      GAUError
  hi link GAUInParen           GAUError
  hi link GAUBoolean           Boolean
  hi link CommentStart          Special
" endif


let b:current_syntax = "gauss"
if main_syntax == 'gauss'
  unlet main_syntax
endif

" vim: ts=8
