" NOTE:
" You are probably looking for share_vimrc.vim in $VIMFILES
" The following are *personal* settings, inappropriate for others!

" *may* want to add the following
set iskeyword+=-
set printheader=
set printoptions=top:1in,right:0.75in,bottom:1in,left:1in,header:0,syntax:n,wrap:y,paper:letter
set sel=inclusive
" colorscheme murphy
colorscheme elflord
set nostartofline
set copyindent
"hack to limit undo to a line at a time
"inoremap <cr> <cr><up><down>


" CAUTION:
" ADDITIONAL STUFF LESS SUITABLE FOR OTHERS
"
" set grepprg=c:/programs/unxutils/grep
" Enable file type detection.
  " Use the default filetype settings, so that mail gets 'tw' set to 72,
  " 'cindent' is on in C files, etc.
  " Also load indent files, to automatically do language-dependent indenting.
filetype plugin on
"map <c-j> :let foo=&tw<cr>:se tw=72<cr>gqip:set tw=&foo<cr>
" set mouse behavior
set mouse=nv
set selectmode=mouse
"set breakat=" !@*-+_;:,./?"
"set no automatic formatting
set fo=""
:set viminfo='50,\"100,%,:0,nc:\\programs\\vim\\_viminfo
set lines=42
winpos 1 1
" create expected clipboard behavior
set clipboard=autoselect
inoremap <c-del> <c-o>cw
inoremap <c-bs> <c-w>
"set backup options
set bdir=F:\\bak,c:\\bak,.,c:\\temp
set backup
set writebackup
set backupskip=ae*.txt,*.tmp
"use spaces for tabs (turned off in python_ai.vim)
set expandtab



"set statusline (had trouble with this)
set statusline=%<%F\ [%1*%M%*%n%R%H]\ %L\ lines(%P)%=\ \ %-25(%3l,%c%03V\ \ %)'%03b'
"always display status line for last window
set laststatus=2

" abbreviations for spelling correction
iab Aaln Alan
iab captial capital
iab funciton function
iab preceed precede
iab preceeding preceding
iab preceeded preceded
iab teh the


" comments of style /* */
" inoremap  '* <esc>0i/*<space><esc>A<space>*/<esc>yyP0ll<c-q>$2hr*yyjp
" view file in browser
au Filetype html,xhtml inoremap <vb <esc>:up<cr>:!start c:\programs\firefox\firefox.exe file:///%:p:gs?\\?/?<cr>
" !start command for EViews
inoremap ;ev <esc>:up<cr>:!start c:\progra~1\EViews4\EViews4.exe %:p<cr>
" !start commands for LaTeX
au Filetype tex inoremap ;vpdf <esc>:!start "c:\programs\SumatraPDF\SumatraPDF.exe" %:p:r:gs?\\?/?.pdf<cr>
au Filetype tex inoremap ;vgsv <esc>:!start "C:\programs\Ghostgum\gsview\gsview32.exe" %:p:r:gs?\\?/?.pdf<cr>
au Filetype postscr inoremap ;vgsv <esc>:up<cr>:!start "C:\programs\Ghostgum\gsview\gsview32.exe" %:p:gs?\\?/?<cr>
au Filetype html inoremap ;gzip <esc>:!start "c:\programs\unxutils\gzip.exe" %:p:r:gs?\\?/?.htm<cr>
au Filetype tex inoremap ;vswp <esc>:up<cr>:!start C:\swp35\swp-pro.exe %:p:gs?\\?/?<cr>
au Filetype tex inoremap ;mt <esc>:up<cr>:!start C:\programs\MiKTeX2.6\miktex\bin\latex.exe &latex %:p:r:gs?\\?/?<cr>
au Filetype tex inoremap ;ps <esc>:!start C:\programs\MiKTeX2.6\miktex\bin\dvips.exe %:p:r:gs?\\?/?<cr>
au Filetype tex inoremap ;vyap <esc>:up<cr>:!start C:\programs\MiKTeX2.6\miktex\bin\yap.exe %:p:r:gs?\\?/?<cr>
au Filetype tex inoremap ;ymb <esc>:up<cr>:!start C:\programs\MiKTeX2.6\miktex\bin\yap.exe c:\mydocs\math\mathbook<cr>
au Filetype tex inoremap ;tx <esc>:up<cr>:!start c:\swp35\TCITex\TrueTeX\initex32 &latex %:p:r:gs?\\?/?<cr>
au Filetype tex inoremap ;dv <esc>:up<cr>:!start c:\swp35\TCITex\TrueTeX\dvigdi32 %:p:r:gs?\\?/?<cr>
au Filetype tex inoremap ;mb <esc>:up<cr>:!start C:\programs\MiKTeX2.6\miktex\bin\latex.exe &latex c:/mydocs/math/mathbook<cr>
"change highlighted text to mixed case:
vmap Uu "xc<c-r>=substitute(@x,'\(\<.\)\(\S\+\)','\u\1\L\2','g')<cr><esc>
" recall that Windows reserves <f1> and <f10>
inoremap <f9> <esc>:call H2T()<cr>
noremap <f9> :call H2T()<cr>
"vmap ;dc :!dc -e "5k<c-r>*"
vmap ;dc <esc>o<c-r>=system("dc -e \"5k<c-r>*\"")
"TextPad match-ups (more or less)
vmap <left> <esc>`<gV
vmap <right> <esc>`>gV
" <c-down> instead of <down> to column of original insertion point
inoremap <c-down> <esc>`[<down>i
" using f5 to search temporarily sets ignorecase
vmap <f5> y/\c<c-r>=escape(@",'\.[*')<cr>
inoremap <f5> <esc>/\c
nmap <f5> /\c
" using shift-f5 to search temporarily sets noignorecase
vmap <s-f5> y/\C<c-r>=escape(@",'\.[*')
inoremap <s-f5> <esc>/\C
nmap <s-f5> /\C
vmap <f8> y:%s@\c<c-r>=escape(@",'\.[*')<cr>@@g<left><left>
vmap <s-f8> y:%s@\C<c-r>=escape(@",'\.[*')<cr>@@g<left><left>
inoremap <c-cr> <esc>o<esc>i

" AUTOCOMMANDS
" my tex stuff
" see c:/programs/vim/vimfiles/ftplugin/tex_ai.vim
autocmd BufNewFile  *.tex        0r $VIMFILES/template/template.tex
autocmd BufNewFile  *.tex        set ft=tex
au Filetype tex inoremap ;df \begin{define}<cr>\end{define}<esc>O
" examples
au Filetype tex inoremap ;xm \begin{xmpl}<cr>\end{xmpl}<cr><esc>kO
" Computational exercises
au Filetype tex inoremap ;cx <esc>:r template_cx<cr>jf:a
" analytical exercises
au Filetype tex inoremap ;ax \begin{ex}<cr>\begin{ansex}<cr>\end{ansex}<cr>\end{ex}<cr><esc>kkkkO
"write file from insert mode
inoremap ;wq <esc>:up<bar>q<cr>
inoremap ;wd <esc>:w<bar>bd<cr>
inoremap ;wr <esc>:up<cr>
inoremap ;wa <esc>:wa<cr>
autocmd BufWritePre,FileWritePre *.tex   ks|call LastMod()|'s
autocmd BufWritePre,FileWritePre *.htm   ks|call LastMod()|'s
autocmd BufWritePre,FileWritePre *.xhtml   ks|call LastMod()|'s
autocmd BufWritePre,FileWritePre *.prg   ks|call LastMod()|'s
autocmd BufWritePre,FileWritePre *.inp   ks|call LastMod()|'s
" read :h template



function! LastMod()
  if line("$") > 40
    let l = 40
  else
    let l = line("$")
  endif
  exe "1," . l . "g/Last modified: /s/Last modified: [^<>]*/Last modified: " .
  \ strftime("%Y %b %d")
endfun

" create questions with enumerated choices
au Filetype tex inoremap ;ec <Esc>:call MCQ()<cr>
fu! MCQ()
    let question=input("Question? ")
    if question!=""
       put=\"\\item \" . question
       put=\"\\begin{enumerate}\"
       let answer=input("Answer? ")
       while answer !=""
         put=\"\\item \" . answer
         let answer=input("Answer? ")
       endwhile
       put=\"\\end{enumerate}\"
       put=\"\"
    endif
endf

function! BibH(...)
  if a:0 > 0
		let options = a:1
	else
		let options = ""
  endif
    let key=input("Key? ")
    let author=input("Author? ")
    let ad="<span class=\"author\">" . author . "</span>"
    let year=input("Year? ")
    let ad=ad . ", " . year . ", "
    let title=input("Title? ")
  " article
  if options =~ "a"
    let journal=input("Journal? ")
    let pubinfo="<span class=\"journal\">" . journal . "</span>"
    let volnum=input("Vol(Num)? ")
    if volnum != ""
      let pubinfo=pubinfo . " " . volnum
    endif
    let pages=input("pages? ")
    if pages != ""
      let pubinfo=pubinfo . ", p." . pages
    endif
    put!='<p id=\"' . key . '\">'
    put= ad
    put='&ldquo;<span class=\"title\">' .  title . '</span>,&rdquo;'
    put= pubinfo
    put='</p>'
  endif
  " book
  if options =~ "b"
    if author==""
      let author=input("Editor? ").' (ed)'
    endif
    let publisher=input("Publisher? ")
    let address=input("Address? ")
    let pubinfo="(" . address . ": " . publisher . ")"
    let isbn=input("ISBN? ")
    if isbn!=""
      let pubinfo=pubinfo .  " isbn: " . isbn
    endif
    put!='<p>'
    put=author . ', ' . date . ', '
    put='<em>' . title . '</em>'
    put=pubinfo
    put='</p>'
  endif
  " incollection
  if options =~ "i"
    let address=input("Address? ")
    let pubinfo="(" . address . ": " . publisher . ")"
    let isbn=input("ISBN? ")
    if isbn!=""
      let pubinfo=pubinfo .  " isbn: " . isbn
    endif
    execute "normal i\<li><cr>" . author . ", " . date . ",<cr>\<em>" . title . "\</em><cr>" . pubinfo. "<cr>\</li><cr><esc>"
  endif
    put=''
    put=''
endfunction

"address(w),author(a),booktitle(b),chapter(c),edition(d),editor(e),howpublished(h),institution(i),isbn(k),journal(j),month(m),note(z),number(n),organization(o),pages(p),publisher(q),school(r),series(s),title(t),type(u),volume(v),year(y),unused(fglx)
" Function: BibT
" Author: Alan G. Isaac
" Last Modified: 14 May 2002
" three sample usages:
":call BibT()                 will request type choice
":call BibT("article")        preferred, provides most common fields
":call BibT("article","ox")   adds optional fields (o) and any "extras"
fu! BibT(...)
  if a:0 > 0
      let choosetype = a:1
  else
    let choosetype=input("Choose type: (article,booklet,book,conference,inbook,incollection,inproceedings,manual,mastersthesis,misc,phdthesis,proceedings,techreport,unpublished)\n ")
  endif
  if a:0>1
    let options = a:2
  else
    let options = ""
  endif
  let extras=""
  let key=input("key? (e.g., jones02aer) ")

" characterize entry types
  let author=""
  let editor=""
  let isbn=""
  if choosetype ==? "article" 
    let required="atjy"
    let optional1="vnpm"
    let optional2="z"   "  z is note
    put!='@ARTICLE{' . key . ','
  endif
  if choosetype ==? "book"
    let required="ætqy"      " requires author *or* editor
    let optional1="wd"
    let optional2="vnsmz"   " w is address, d is edition
    let extras="k"           " isbn
    put!='@BOOK{' . key . ','
  endif
  if choosetype ==? "booklet"
    let required="t"  
    let optional1="ahy"
    let optional2="wmz"   " w is address
    put!='@BOOKLET{' . key . ','
  endif
  if choosetype ==? "inbook"  
    let required="ætcpqy"   
    let optional1="w"           " w is address
    let optional2="vnsudmz"     " d is edition
    let extras="k"              " isbn
    put!='@INBOOK{' . key . ','
  endif
  if choosetype ==? "incollection"  
    let required="atbqy"        " b is booktitle
    let optional1="ecpw"         " w is address, c is chapter
    let optional2="vnsudmz"    " d is edition
    let extras="k"              " isbn
    put!='@INCOLLECTION{' . key . ','
  endif
  if choosetype ==? "inproceedings"
    let required="atby"         " b is booktitle
    let optional1="epwoq"       " w is address, q is publisher
    let optional2="vnsmz"
    let extras="k"              " isbn
    put!='@INPROCEEDINGS{' . key . ','
  endif
  if choosetype ==? "manual"
    let required="t"
    let optional1="ow"
    let optional2="admyz"   " w is address
    put!='@MANUAL{' . key . ','
  endif
  if choosetype ==? "mastersthesis"
    let required="atry"      " r is school
    let optional1="w"         " w is address
    let optional2="umz"      " u is type, w is address
    put!='@MASTERSTHESIS{' . key . ','
  endif
  if choosetype ==? "misc"
    let required=""
    let optional1="athy"
    let optional2="mz"
    put!='@MISC{' . key . ','
  endif
  if choosetype ==? "phdthesis"
    let required="atry"      " r is school
    let optional1="w"         " w is address
    let optional2="umz"       " u is type
    put!='@PHDTHESIS{' . key . ','
  endif
  if choosetype ==? "proceedings"
    let required="ty"
    let optional1="ewo"            " w is address
    let optional2="vnsmqz"         " q is publisher
    put!='@PROCEEDINGS{' . key . ','
  endif
  if choosetype ==? "techreport"
    let required="atiy"
    let optional1="unw"           " u is type, w is address
    let optional2="mz" 
    put!='@TECHREPORT{' . key . ','
  endif
  if choosetype ==? "unpublished"
    let required="atz"
    let optional1="y"      
    let optional2="m"      
    put!='@UNPUBLISHED{' . key . ','
  endif

  " define fields
  let fields = required . optional1
  if options =~ "o"
    let fields = fields . optional2
  endif
  if options =~ "x"
    let fields = fields . extras
  endif

  " implement fields
  if fields =~ "[aæ]" 
    let author=input("Author(s)? ")
    if author!="" || required =~ "a"
      put='  author = {' . author . '},'
    endif
  endif
  if fields =~ "[eæ]" 
    let editor=input("Editor(s)? ")
    if editor!="" || required =~ "e"
      put='  editor = {' . editor . '},'
    endif
  endif
  if fields =~ "y" 
    let year=input("Year? ")
    put='  year = ' . year . ','
  endif
  if fields =~ "t" 
    let title=input("title? ")
    put='  title = {' . title . '},'
  endif
  if fields =~ "b"            " booktitle
    let booktitle=input("booktitle? ")
    put='  booktitle = {' .  booktitle . '},'
  endif
  if fields =~ "d"            " edition
    let edition=input("edition? (E.g., 2nd) ")
    put='  edition = {' .  edition . '},'
  endif
  if fields =~ "c"            " chapter
    let chapter=input("chapter? ")
    if chapter !=""
      put='  chapter = {' .  chapter . '},'
    endif
  endif
  if fields =~ "j"            " journal
    let jrnlkey=input("{Journal Name} (in braces) or journal key? ")
    if jrnlkey != ""
      put='  journal = ' . jrnlkey . ','
    else
      put='  journal = {},'
    endif
  endif
  if fields =~ "v" 
    let volume=input("volume? ")
    if volume !=""
      put='  volume = ' .  volume . ','
    endif
  endif
  if fields =~ "n" 
    let number=input("number? ")
    if number !=""
      put='  number = ' .  number . ','
    endif
  endif
  if fields =~ "m" 
    let month=input("month? ")
    if month !=""
      put='  month = ' .  month . ','
    endif
  endif
  if fields =~ "p" 
    let pages=input("pages? ")
    put='  pages = {' .  pages . '},'
  endif
  if fields =~ "q" 
    let publisher=input("publisher? ")
    put='  publisher = {' .  publisher . '},'
  endif
  if fields =~ "w" 
    let address=input("address? ")
    put='  address = {' .  address . '},'
  endif
  if fields =~ "h" 
    let howpublished=input("howpublished? ")
    put='  howpublished = {' .  howpublished . '},'
  endif
  if fields =~ "i" 
    let institution=input("institution? ")
    put='  institution = {' .  institution . '},'
  endif
  if fields =~ "o" 
    let organization=input("organization? ")
    put='  organization = {' .  organization . '},'
  endif
  if fields =~ "r" 
    let school=input("school? ")
    put='  school = {' .  school . '},'
  endif
  if fields =~ "s" 
    let series=input("series? ")
    put='  series = {' .  series . '},'
  endif
  if fields =~ "u" 
    let type=input("type? (E.g., Working Paper)")
    put='  type = {' .  type . '},'
  endif
  if fields =~ "k" 
    let isbn=input("isbn? ")
    if isbn !=""
      put='  isbn = {' .  isbn . '},'
    endif
  endif
  put='  otherinfo = {}'
  put='}'

  " for HTML cite info
if options =~ "h"
  if choosetype ==? "article"
    if jrnlkey =~ "{.\+}"
      let journal=substitute(jrnlkey,'[{}]','','g')
    else
      let journal=input("Journal? (no braces) (Press enter to use journal key) ")
      if journal==""
        let journal=substitute(jrnlkey,'.*','\U\0','')
      endif
    endif
    let pubinfo="<span class=\"journal\">" . journal . "</span>"
    let volnum=volume
    if number != ""
      let volnum = volnum . "(" . number . ")"
    endif
    if volnum != ""
      let pubinfo=pubinfo . " " . volnum
    endif
    if pages != ""
      let pubinfo=pubinfo . ", pp." . substitute(pages,'--','-','') . "."
    endif
    put='<p id=\"' . key . '\" class=\"ref\">'
    put='<span class="author">' . author . '</span>,'
    put='<span class="date">' . year . '</span>,'
    put='&ldquo;<span class="title">' .  title . '</span>,&rdquo;'
    put= pubinfo
    put='</p>'
    put= author . ' (' . year . substitute(jrnlkey,'.*',' \U\0','') . ')' 
    put = ''
  endif
  " incollection or book
  if (choosetype ==? "book")
    if (author=="") && editor!=""
      let author=editor . ' (ed)'
    endif
    let title='<span class="booktitle">' .  title . '</span>,'
  endif
  if (choosetype ==? "incollection")  && (author!="")
    if editor!=""
      let author=author . " in " . editor . ' (ed)'
      let title='<em>' . title . '</em>, in <span class="booktitle">' .  booktitle . '</span>,'
    endif
  endif
  if (choosetype ==? "book"  || choosetype ==? "incollection" )
    let pubinfo="(" . address . ": " . publisher . ")"
    if isbn!=""
      let pubinfo=pubinfo .  " isbn: " . isbn
    endif
    put='<p id="' . key . '" class="ref">'
    put='<span class="author">' . author . '</span>,'
    put='<span class="date">' . year . '</span>,'
    put=title
    put=pubinfo
    put='</p>'
    put= author . ' (' . year  . ')' 
  endif
endif
    +
endf

fu! BibBk()
    let key=input("key? ")
    put!=\"@BOOK{\" . key . \",\"
    let author=input("Author(s)? ")
    if author!=""
      put=\"  author = {\" . author . \"},\"
    else
      let editor=input("Editor(s)? ")
      put=\"  editor = {\" . editor . \"},\"
    endif
    let year=input("Year? ")
    put=\"  year = \" . year . \",\"
    let title=input("title? ")
    put=\"  title = {\" . title . \"},\"
    let publisher=input("publisher? ")
    put=\"  publisher = {\" .  publisher . \"},\"
    let address=input("address? ")
    put=\"  address = {\" .  address . \"},\"
    let isbn=input("isbn? ")
    if isbn !=""
      put=\"  isbn = {\" .  isbn . \"},\"
    endif
    put=\"  agi = {}\"
    put=\"}\"
    startinsert!
endf

function! Htable(cols)
  put=\"<table>\"
  let td="waiting"
  while td !=""
    put=\"<tr>\"
    let col=1
    while col<=a:cols
      let td=input("data? ")
      put=\"<td>\"
      put=td
      put=\"</td>\"
      let col=col+1
    endwhile
  put=\"</tr>\"
  endwhile
  put=\"</table>\"
endfunction

function! Hlet(...)
 0/<\/title
 put='<style><!--'
 append
  @page{margin: 1in 0}
  body{margin: 0;
       padding: 0 5em}
  p{text-indent:0em; margin-top: 1em;}
  h1.memo {
    text-align: left;
    color: black;
    background-color: white;
    border-top: solid blue 2px;
    border-bottom: solid blue 2px;
    letter-spacing: .5em;
    margin-top: 6em;
    text-align: left;
    font: bold small-caps 20pt Arial,sans-serif
    }
  td.memo {text-align: left;
    vertical-align: baseline;}
  th.memo {text-align: left;
    vertical-align: baseline;}
.
 put='--></style>'
 0/<body
 put='<h1 class=\"memo\">Memorandum</h1>'
 put='<table>'
 put='<tr>'
 let to=input("To: ")
 put='<th class=\"memo\"><b>To:</b></th><td class=\"memo\">' . to . '</td>'
 put='</tr>'
 put='<tr>'
 put='<th class=\"memo\"><b>From:</b></th> <td class=\"memo\">Alan G. Isaac<br />Department of Economics</td>'
 put='</tr>'
 put='<tr>'
 let date=input("Date (or enter):")
 if date==""
  let date=strftime("%d %b %Y")
 endif
 put='<th class=\"memo\"><b>Date:</b></th> <td class=\"memo\">' . date . '</td>'
 put='</tr>'
 put='<tr>'
 let re=input("anent: ")
 put='<th class=\"memo\"><b>Anent:</b></th> <td class=\"memo\">' . re . '</td>'
 put='</tr>'
 put='</table>'
 put='<pre>'
 put=''
 put=''
 put=''
 put='</pre>'
endfunction

function! Hmemo(...)
 0/<\/title
 put='<style><!--'
 append
  @page{margin: 1in 0}
  body{margin: 0;
       padding: 0 5em}
  p{text-indent:0em; margin-top: 1em;}
  h1.memo {
    text-align: left;
    color: black;
    background-color: white;
    border-top: solid blue 2px;
    border-bottom: solid blue 2px;
    letter-spacing: .5em;
    margin-top: 6em;
    text-align: left;
    font: bold small-caps 20pt Arial,sans-serif
    }
  td.memo {text-align: left;
    vertical-align: baseline;}
  th.memo {text-align: left;
    vertical-align: baseline;}
.
 put='--></style>'
 0/<body
 put='<h1 class=\"memo\">Memorandum</h1>'
 put='<table>'
 put='<tr>'
 let to=input("To: ")
 put='<th class=\"memo\"><b>To:</b></th><td class=\"memo\">' . to . '</td>'
 put='</tr>'
 put='<tr>'
 put='<th class=\"memo\"><b>From:</b></th> <td class=\"memo\">Alan G. Isaac<br />Department of Economics</td>'
 put='</tr>'
 put='<tr>'
 let date=input("Date (or enter):")
 if date==""
  let date=strftime("%d %b %Y")
 endif
 put='<th class=\"memo\"><b>Date:</b></th> <td class=\"memo\">' . date . '</td>'
 put='</tr>'
 put='<tr>'
 let re=input("anent: ")
 put='<th class=\"memo\"><b>Anent:</b></th> <td class=\"memo\">' . re . '</td>'
 put='</tr>'
 put='</table>'
 put='<pre>'
 put=''
 put=''
 put=''
 put='</pre>'
endfunction

function! Html(...)
 if a:0 > 0
   let options = a:1
  else
   let options = ""
 endif
   let today=strftime("%d %b %Y")
0
i
<html>
<head>
 <title>
 </title>
 <style type="text/css"><!--
   @page{margin: 1in 0}
   body{margin: 0 10%;}
   p{text-indent:0em; margin-top: 1em;}
   p.letterlead {text-indent:0em; margin-top: 1in;}
   p.sig {text-indent:0em; margin-top: 0.35in;}
 --></style>
</head>
<body>
.
 if options =~ "h"
   0/<body
   put =\"<p>\n6203 Maiden Lane\n<br>\nBethesda, MD 20817\n<br>\n\".today.\"</p>\"
   '] put=\"<address class='home'>\n</address>\"
   '] put='<p>Sincerely,</p>'
   put=\"<p class='sig'>Alan G. Isaac</p>\"
 endif
 if options =~ "w"
   0/<body
   put=''
   put=\"<p class='letterlead'>\" . today . '</p>'
   put=''
   put=\"<address>\n</address>\"
   '] put=''
   put='<p>Sincerely,</p>'
   put=\"<p class='sig'>\nAlan G. Isaac\n<br>\nAssociate Professor of Economics\n</p>\"
 endif
 if options =~ "m" || options=~ "r"
   0/<\/style
i
h1.memo {text-align: left; color: black;
         border-bottom-style: solid;
         border-top-style: solid;
         border-color: blue;
         border-bottom-width: 2px;
         border-top-width: 2px;
         letter-spacing: .5em;
         margin-top: 3em;
         text-align: left;
         color: black;
         font: bold small-caps 20pt Arial,sans-serif
        }
td.memo {text-align: left;
         vertical-align: baseline
        }
th.memo {text-align: left;
         vertical-align: baseline
        }
.
   0/<body
a
<table>
<tr>
<th class="memo">To:</th>
<td class="memo,to">
</td>
</tr>
<tr>
<th class="memo">From:</th>
<td class="memo">Alan G. Isaac<br />
Associate Professor<br />
Department of Economics<br />
American University
</td>
</tr>
<tr>
<th class="memo">Date:</th>
<td class="memo,date">
</td>
</tr>
<tr>
<th class="memo">Anent:</th>
<td class="memo,re">
</td>
</tr>
</table>
<pre>



</pre>
.
   let to=input("To: ")
   0/memo,to
   put=to
   let date=strftime("%d %b %Y")
   /memo,date
   put=date
   let re=input("Anent: ")
   /memo,re
   put=re
   0/<body
   put=''
   if options =~ "m"
   put='<h1 class=\"memo\">Memorandum</h1>'
   else
   put='<h1 class=\"memo\">Letter of<br />Recommendation</h1>'
   endif
 endif
 if options=~"2"
   0 put='<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'
 endif
 if options=~"x"
   0 put='<?xml version=\"1.0\" encoding=\"UTF-8\"?>'
   put='<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\"'
   put='            \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">'
 endif
 if options=~"4s"
   0 put='<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\"'
   put='            \"http://www.w3.org/TR/html4/strict.dtd\">'
 endif
 if options=~"4l"
   0 put='<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\"'
   put='        \"http://www.w3.org/TR/html4/loose.dtd\">'
 endif
$ 
a
</body>
</html>
.
0/<body
0/<address
endfunction

function! Htoc()
  put=\"<toc>\n</toc>\"
  g/<h\d/.,-/<\/h\d>/copy $
  0/\/body>/+2,$d a
  0/<toc>/put a
endfunction

function! Table2(title, ...)
  echohl Title
  echo a:title
  echohl None
  let idx = 1
  while idx <= a:0
    exe "echo a:" . idx
    let idx = idx + 1
  endwhile
  return idx
endfunction


function! M2Q()  "monthly to quarterly
  $put='<eof>'
  g/^\d\{4}\.0[369]\|^\d\{4}\.12/t $
  1,/<eof>/d
  %s@^\(\d\{4}\.\)03@\11@e
  %s@^\(\d\{4}\.\)06@\12@e
  %s@^\(\d\{4}\.\)09@\13@e
  %s@^\(\d\{4}\.\)12@\14@e
endfunction

function! H2T()
  %s/<\/title>/&\r/e
  0/<body/
  . put! =''
  .,-/>/j
  g/<title/.,-/<\/title>/m /<body/
  %s/<title>/Document TITLE: /e
  g/<[^>]\+$/.,/>/j
  %s/<img[^>]\+dropcap[^>]\+alt="\(\a\)">/\1/e
  0,/<body/-1 d
  0/<body
  s/<body\_[^>]*>//e
  %s/<h1>\s*\n*/TITLE: /e
  %s/<h2>\s*\n*/SECTION: /e
  %s/<h3>\s*\n*/Subection: /e
  %s/<\/h\d>/\r
  %s/<em>\|<\/em>\|<i>\|<\/i>\|<b>\|<\/b>\|<strong>\|<\/strong>/*/ge
  %s/<script\|<!\|<img/\r&/ge
  %s/<\/script>\|-->/\r&\r/ge
  g/^\s*<!/.,/-->/ d
  g/^\s*<script/.,/<\/script>/ d
  %s/&copy;/Copyright: /ge
  %s/&nbsp;/ /ge
  %s/&amp;/\&/ge
  %s/&quot;/"/ge
  %s/&#146;/'/ge
  %s/&#150;/--/ge
  %s/&#151;/---/ge
  %s/&#224;/à/ge
  %s/&#225;/á/ge
  %s/&#231;/ç/ge
  %s/&#232;/è/ge
  %s/&#233;/é/ge
  %s/&#234;/ê/ge
  %s/&#235;/ë/ge
  %s/&#239;/ï/ge
  %s/&#8212;/---/ge
  %s/&mdash;/---/ge
  %s/&ndash;/--/ge
  %s/&ldquo;/``/ge
  %s/&rdquo;/''/ge
  %s/&eacute;/é/ge
  %s/&gt;/>/ge
  %s/&lt;/</ge
  %s@\s*&#0151;\s*@---@ge
  %s/\s*—\s*/---/ge
  %s/<p/\r\r&/ge
  %s/<div/\r\r&/ge
  %s/<br[^>]*>/\r\r/ge
  %s/<\_.\{-}>//ge
  %s/^\s\+//e
%:s/x80/?/ge
%:s/x81/?/ge
%:s/x82/`/ge
%:s/x83/f/ge
%:s/x84/"/ge
%:s/x85/.../ge
%:s/x86/+/ge
%:s/x87/++/ge
%:s/x88/^/ge
%:s/x89/o\/oo/ge
%:s/x8a/S/ge
%:s/x8b/</ge
%:s/x8c/OE/ge
%:s/x8d/?/ge
%:s/x8e/?/ge
%:s/x8f/?/ge
%:s/x90/?/ge
%:s/x91/`/ge
%:s/x92) . "/'/ge"
%:s/x93/"/ge
%:s/x94/"/ge
%:s/x95/*/ge
%:s/x96/-/ge
%:s/x97/--/ge
%:s/x98/~/ge
%:s/x99/TM/ge
%:s/x9a/s/ge
%:s/x9b/>/ge
%:s/x9c/oe/ge
%:s/x9d/?/ge
%:s/x9e/?/ge
%:s/x9f/Y/ge
%s///ge
v/./,//-j
endfunction

function! Tth()
  %s/\\title{\(.\{-}\)}/<h1>\r\1\r<\/h1>/e
  %s/\\section{\(.\{-}\)}/<h2>\r\1\r<\/h2>/e
  %s/\\subsection{\(.\{-}\)}/<h3>\r\1\r<\/h3>/e
  %s/\\item\(.\{-}\)/<li>\1\r<\/li>/e
  g/^[^\]\+$/.,/\/\//- j
  %s@\\begin{enumerate}@<ol>@e
  %s@\\end{enumerate}@<\/ol>@e
  %s@\\begin{itemize}@<ul>@e
  %s@\\end{itemize}@<\/ol>@e
  %s@\\$@&usd;@e
  %s/^\s\+//e
  v/./,//-j
endfunction

function! HWprg()
  %s@^\s*save\s\+.\+@save\ c:\\temp.wf1@e
"  %s/\s\S\{-}\.dat/ c:\\data\\frankel79aer.dat
  %s@open \(.\{-}\)wf1@open\ c:\\progra\~1\\Eviews4\\macro1.wf1@e
  %s@^\s*print@'print@e
  1put!=\"'%%%%%%%%%%%%%%%%%%%%%%%\"
  1put!=\"'dangerous stuff above\"
  g/save/co 0
  0/^'dangerous
  0,.-s/^\s*\([^']\)/'\1
"  w
endfunction
au BufReadPost temp.prg call HWprg()


" ChiWriter to text
function! C2t()
  %s@\\[[:digit:]^,!]@@ge
  g/\\+/j
  %s@\\+ @@ge
  %s@\\ @ @ge
  %s@\\/@@ge
endfunction
function! Temp()
  let trythis=substitute("testing", ".*", "\\U\\0", "")
  put=trythis
  put=substitute("testing", ".*", "\\U\\0", "")
endfunction
" Print Latin-1 character repertoire plus illegal characters
function! PrintLatin1()
  let ct16=32
  while ct16<128
   let cs=""
   let ct1=ct16
   let ct16=ct16+16
   while ct1<ct16
    let cs=cs."   ".nr2char(ct1) 
    let ct1=ct1+1
   endwhile
   put=cs
  endwhile
  let ct16=160
  while ct16<256
   let cs=""
   let ct1=ct16
   let ct16=ct16+16
   while ct1<ct16
    let cs=cs."   ".nr2char(ct1) 
    let ct1=ct1+1
   endwhile
   put=cs
  endwhile
  let ct16=128
  while ct16<160
   let cs="<tr>"
   let ct1=ct16
   let ct16=ct16+16
   while ct1<ct16
    let cs=cs."<td>".nr2char(ct1)."</td>"
    let ct1=ct1+1
   endwhile
   put=cs
  endwhile
endfunction

" Mycolorscheme written by Dave Silvia
" I like breeze and the sienna dark scheme but am trying ps_color
au BufEnter *.tex call Mycolorscheme('ps_color')
function! Mycolorscheme(...)
        if !exists("g:colors_name")
                let defaultColorScheme='blue'
        else
                let defaultColorScheme=''
        endif
        let argIdx=1
        while argIdx <= a:0
                execute 'silent! colorscheme '.a:{argIdx}
                if exists("g:colors_name") && g:colors_name == a:{argIdx}
                        let defaultColorScheme=''
                        break
                endif
                let argIdx=argIdx+1
        endwhile
        if defaultColorScheme != ''
                execute 'colorscheme '.defaultColorScheme
        endif
endfunction

