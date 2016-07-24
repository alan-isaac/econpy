setl encoding=utf-8
setl fileencoding=utf-8
setl fileformat=unix
setl filetype=mail
setl isk-=.
setl noexpandtab
setl nobackup
setl nocindent
setl spell

inoremap ;wq <esc>:up<bar>w! c:/temp/temp.mail<bar>q<cr>

"abbreviations
iab Acct Account
iab acct account
iab acctg accounting
iab Altho Although
iab altho although
iab amt amount
iab amts amounts
iab Appt Appointment
iab appt appointment
iab asap as soon as possible
iab B4 Before
iab b4 before
iab bday birthday
iab Bc Because
iab bc because
iab beh behavior
iab bhv behave
iab bhvr behavior
iab bldg building
iab bt between
iab Btw By the way
iab btw by the way
iab chk check
iab cd could
iab Cd Could
iab cdt could not
iab Cdt Could not
iab dept department
iab def definition
iab dfn definition
iab defintion definition
iab dpt department
iab Dpt Department
iab ec economic
iab ecs economics
iab endog endogenous
iab endogs endogenous variables
iab eqn equation
iab eqns equations
iab esp especially
iab exog exogenous
iab exogs exogenous variables
iab fn function
iab fns functions
iab fr from
iab fwd forward
iab fwdd forwarded
iab fwdg forwarding
iab grad graduate
iab gvt government
iab hw homework
iab hr hour
iab hrs hours
iab Id I would
iab impt important
iab imo in my opinion
iab Imo In my opinion
iab info information
iab intl international
iab iir if I recall correctly
iab IIR If I recall correctly
iab Iir If I recall correctly
iab iirc if I recall correctly
iab IIRC If I recall correctly
iab Iirc If I recall correctly
iab itrw in the real world
iab Mb Maybe
iab mb maybe
iab Mkt Market
iab mkt market
iab msg message
iab msgs messages
iab nec necessary
iab ntl nevertheless
iab Ntl Nevertheless
iab nvr never
iab Otoh On the other hand
iab otoh on the other hand
iab Ow Otherwise
iab ow otherwise
iab pd paid
iab Pls Please
iab pls please
iab pref preference
iab prefs preferences
iab prereq prerequisite
iab prodn production
iab Prof Professor
iab prof professor
iab pt point
iab rcd received
iab rcg receiving
iab rcv receive
iab rec receive
iab recd received
iab ru Are you
iab Shd Should
iab shd should
iab Shdt Should not
iab shdt should not
iab sig signature
iab soln solution
iab solns solutions
iab Sth Something
iab sth something
iab suff sufficient
iab Tf Therefore
iab tf therefore
iab Tho Although
iab tho although
iab thru through
iab Ur You are
iab ur you are
iab Ud You would
iab ud you would
iab Usl Usual
iab usl usual
iab Usu Usually
iab usu usually
iab Usy Usually
iab usy usually
iab W With
iab w with
iab Wi Within
iab wi within
iab Wo Without
iab wo without
iab Wd Would
iab wd would
iab wdt wouldn't
iab wdnt wouldn't
iab Wdt Wouldn't
iab Wdnt Wouldn't
iab wrt with respect to
iab yr your

"set colorscheme for email
"make more portable by defaulting to a Vim colorscheme
"(should be available on standard Vim installations)
"good: breeze, elflord, darkblue, navajo-night
let preferColorScheme='darkblue'
let buColorScheme='elflord'
execute 'silent! colorscheme ' . preferColorScheme
if g:colors_name != preferColorScheme
        execute 'silent! colorscheme ' . buColorScheme
endif

" mark long lines using syntax highlighting
highlight RightMargin term=reverse ctermbg=12 guifg=White guibg=Black
match RightMargin /\%>72v.\+/

" options: case matters??
" File: aimail.vim
"
" Purpose: facilitate editing mails and newgroup postings
"
" Author (sort of): Alan G. Isaac <aisaac AT american DOT edu>
"          most of what is interesting is stolen from
"          MailNews by Ralf Arens
"                     mailto:ralf.arens AT gmx DOT net
"                     mailto:ralf.arens AT tu-clausthal DOT de
"
" Last Modified: 2003-01-19
" this funtion parses and corrects mails and news
"	options:
"	:: delete " (was: ...)" in "Subject: ..."
"	a: append greetings and signature
"	b: at least one blank after `>' (`>text' to `> text')
"	d: delete quoted signature
"	g: delete greeting
"	h: short header
"	t: delete trailing empty lines
"	r: repair quotes (`> >' to `>>')
"	w: remove trailing whitespace
"	W: remove trailing whitespace only after `>\+'
"	q: delete quotes on empty lines
"	z: squeeze empty lines into one
"	Z: squeeze empty quoted line to one
" deletions are generally to black hole (:h quote_)
function! AImail(...)
        "set formatoptions, comments and textwidth
        set com=n:>,n:\|,fb:-,fb:·,fb:* et nomodeline sw=4 fo=awtcq1 tw=60
	if a:0 > 0
		let options = a:1
	else
		let options = ""
	endif
        " deal with new msgs
        if line("$")==1
          if options =~"a"
            let options="a"
          else
            let options=""
          endif
        endif
        " get rid of initials in quotes
        %s/^\(>[>[:blank:] ]*\)[A-Z]\{2,3}>/\1>/ge
	" shorten date, and first name first
        " (assumes header is in line 1)
	if options =~ "h"
           " alter date (no time)
           1s/\d\d:[-+:[:digit:] ]\+([^)]\+Time)//e
           1s/^\(On.* 20\d\d\) [^"<]\+\d /\1, /e
           1s/(\(PDT\|PST\|EDT\|EST\))//e
           1s/"\([^,"']\+\), \([^"]\+\)"/\2 \1 /e
           1s/<[^>]\+>//e
           1s/ \+/ /ge
        endif
	" DELETE GREETING (not yet very useful)
	if options =~ "g"
            0
            let greet=search('^\s*>\s*\(Hi\|Hello\|Dear\|Prof\)')
            " delete leading empty lines
            if greet>0 && getline(1) !~ '\S'
                     0;/\S/-d _
            endif
            " delete leading empty lines
            if greet>0 && getline(2) !~ '\S'
                     2;/\S/-d _
            endif
            if greet>0 && greet <=8
                0/^\s*>\s*\(Hi\|Hello\|Dear\|Prof\)
                s/^>\s*\(Hi\|Hello\|Dear\|Prof\)[^,.-:]\{-}\(Isaac\|Alan\|[,.-:]\+\)[,.-:]*/> /e
                if getline(".") =~ "^[>[:blank:] ]*$"
                  .;/[^>[:blank:]]/- d _
                endif
             endif
	endif
	" DELETE QUOTES on EMPTY LINES (:h :s_flags)
	if options =~ "q"
                %s/^>[>[:blank:] ]*$//e
	endif
	" add DUMMY LINE at eof in case file ``empty''
	$put='<eof>'
        " DELETE LEADING EMPTY LINES (into black hole register) 
	"  unnecessary if header is at start
        "  note use of \\
        if getline(1) !~ "\\S"
		0;/\S/-d _
	endif
	" deal with MSG FORWARDING (add leading blank line)
	  0/\S
	if getline(".") =~ "-- Forward"
	  if line(".") == 1
            1put!=''
          endif
	  0
	endif
	" squeeze "blank" (empty except white space) lines into one
	if options =~ "z"
          v/\S/,//-j
	endif
	" repair quotes (`> >' to `>>')
	" inequality assumes presence of dummy eof line
	if options =~ "r"
		"	position cursor at top
		0
		while line(".") < line("$")
			while getline(".") =~ '^>\+ >'
				s/^\(>\+\) >/\1>/e
			endwhile
			norm j
		endwhile
	endif
	" delete DUMMY LINE at eof
	$d _
	" remove " (was: ...)" in "Subject: ..."
	if options =~ ":"
		0/^Subject: /
		s/ (was: [^)]*)$//e
	endif
	" squeeze empty quoted lines into one
           "odd behavior of sub under 6.0ap (extra >)
	if options =~ "Z"
                %s/^>\([>[:blank:]]*\n\)\+/>\1/e
	endif
	" remove trailing whitespace after `^>\+'
	if options =~ "W"
		%s/\(^>\+\)\s\+$/\1/e
	endif
	" add one blank after `>' if there is none
	if options =~ "b"
		v/^>\+ /s/^>\+/& /e
	endif
	" delete paragraph after quoted signature ([MN]UA quote has to be `> ')
	if options =~ "d"
                if search('^>\s\?--\s*$') > 0
                        $put=''
                        g/^> --\s*$/,/^[>[:blank:]]*$/d _
                endif
	endif
	" delete trailing empty lines into black hole (:h quote_)
        "   adds and deletes dummy bof line
	if options =~ "t"
	        1put!='<bof>'
		while getline(line("$")) == ""
			$d _
		endwhile
	        1d _
	endif
	" remove trailing whitespace (*before* appending sig)
	if options =~ "w"
		%s/\s\+$//e
	endif
	" append greetings and signature
	if options =~ "a"
		call Sig()
	endif
	" position cursor on first line
	1
endf


" take care of signature
" be sure to set sig location below
fu! Sig()
        "set alt1exp and alt2exp for context dependents sigs
        "use expressions that pinpoint the context
	let alt1exp = "^Newsgroups: comp.text.tex"
	let alt2exp = "your_alt2exp"
	" assume not posting to alt1 -> alt1=0
	let alt1 = 0
	let alt2 = 0
	" if comp.text.tex -> alt1=1
	exe "%g/".alt1exp."/let alt1=1"
	exe "%g/".alt2exp."/let alt2=1"
	" assume sig exists not -> sig=0
	let sig = 0
	" if sig exists -> sig=1
        let sig = search('^--\s*$') > 0
	"	append greetings and possibly custom sig
	if sig == 0 && alt1 == 0 && alt2 == 0
		$put =''
		$put ='Cheers,'
		$put ='Alan'
		$put =''
		$put =''
		$put =''
		$put ='-- "
	        r L:\misc\sig
		let sig = 1
	endif
	if sig == 0 && alt1 == 1
		$put =\"\"
		$put =\"\"
		$put =\"Cheers,\"
		$put =\"Alan\"
		$put =\"\"
		$put =\"-- \"
	        r L:\misc\sig
		let sig = 1
	endif
	if sig == 0 && alt2 == 1
		$put =\"\"
		$put =\"\"
		$put =\"Cheers,\"
		$put =\"Alan\"
		$put =\"\"
		$put =\"-- \"
	        r L:\misc\sig
	endif
endf

call AImail("qtzwrbdgh")
" Add space at end of selected text lines
%s/^>\+ \S\+.*[^:)'"]$/& /e


imap ;mm <esc>:call AImail("qtzwrbdg")
" SOME MAPPINGS
imap ;sig <esc>:r c:\misc\sig<cr>{
imap ;bwi <cr><esc>0C<cr>Best Wishes,<cr>Alan Isaac<cr><cr>
imap ;bwa <cr><esc>0C<cr>Best Wishes,<cr>Alan<cr><cr>
imap ;cha <cr><esc>0C<cr>Cheers,<cr>Alan<cr>
imap ;chi <cr><esc>0C<cr>Cheers,<cr>Alan Isaac<cr>
imap ;chr <cr><esc>0C<cr>Cheers,<cr>Alan<cr>
imap ;hth <cr><esc>0C<cr>hth,<cr>Alan Isaac<cr>
imap ;chu <cr><esc>0C<cr>Cheers,<cr>Uncle Alan<cr>
imap ;tx <cr><esc>0C<cr>Thanks,<cr>Alan<cr>
imap !tx <cr><esc>0C<cr>Thanks!<cr>Alan<cr>
imap ;fwiw <cr><esc>0C<cr>fwiw,<cr>Alan<cr>
imap ;fyi <cr><esc>0C<cr>fyi,<cr>Alan<cr>
imap ;tui <cr><esc>0C<cr>Thank you,<cr>Alan Isaac<cr><cr>
imap ;tua <cr><esc>0C<cr>Thank you,<cr>Alan<cr><cr>
" change subject line
"map ;ns 1G/^Subject: /e<CR>a(was: <Esc>A)<Esc>%i
map ;ns 1G/^Subject: /<CR>:s,\(Subject: \)\(Re: \)*\(.*\)$,\1(was: \3),<CR>f(i
" put selected text in quotes 
vnoremap ;qt "xc<cr><tab>``<c-r>x''<cr>
" anonymous sender
imap ;sw <esc>:0/^On.\+wrote:\s*$/s/,[^,]\{-}wrote/, someone wrote<cr>
" rename sender with visually selected name
vnoremap ;sw "xy:1<cr>:s/,[^,]\{-}wrote/, wrote/<cr>/wrote<cr>i<c-r>x<space>

" Srinath Avadhanula
function! MailFormat() range
        exe a:lastline
        normal! mb
        put='a very improbable line isnt this--xx-xx-xx-xx-xx-'
        exe a:firstline
        normal! ma
        normal! 'aV'bgq
        let header = matchstr(getline('.'), '^\zs[^>]*\ze>')
        exe a:firstline.',/^a very improbable line isnt this--xx-xx-xx-xx-xx-$/-1 s/.'.header.'>//ge'
        /^a very improbable line isnt this--xx-xx-xx-xx-xx-$/-1
        normal! mb
        normal! 'aV'bgq
        /^a very improbable line isnt this--xx-xx-xx-xx-xx-$
        d
endfunction

" author: Benjamin Esham
function! UsenetSetup()
     setl textwidth=75                " wrap at 75 columns
     setl comments=n:>,n:\|,n:%       " recognize [>|%] as quote  indicators
     setl formatoptions=qn            " allow formatting with 'gq';  recognize lists (q.v.)
     " the unholy mess on the next line recognizes lists with "1.",  "-", and "*" as bullets,
     setl flp=^\\(\\d\\+[.\\t\ ]\\\|[-*â€¢]\ \\\|\ \ \\)\\s*    " and  also recognizes two-space blockquoting
     setl expandtab                   " use spaces instead of tabs  (eugh) 
     nmap <Leader>f :call FormatUsenetParagraph()<CR>
     " insert a randomly-chosen signature and turn on spell checking
     nmap <Leader>g :r !~/.vim/usenet/sig.pl ~/.vim/usenet/sigs<CR>:setl spell<CR> 
endfunction

" author: Peppe on comp.editors
" function: reflow paragraphs to textwidth
function! FormatUsenetParagraph()
     sil '{,'}s/\%(^[|>% \t]*\)\@<=\([|>%]\)\s*/\1 /ge
     normal gqip
endfunction


" vim: set noet ts=8 sw=8 sts=8
