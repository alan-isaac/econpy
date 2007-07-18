" local syntax file - set colors on a per-machine basis:
" Vim color file
" Maintainer:	Tim Chase <timchase.vim@tim.thechases.com>
" Last Change:	2003 Jan 23

set background=dark
hi clear
if exists("syntax_on")
  syntax reset
endif
let g:colors_name = "timchase"
hi Cursor      guifg=Black guibg=White
hi Visual      guifg=gray guibg=Black
hi FoldColumn  guifg=#88ff88 guibg=#3c3c3c gui=bold
hi Folded      guifg=#88ff88 guibg=#3c3c3c gui=bold
hi Normal      guifg=gray      guibg=black
hi Comment     term=bold    ctermfg=DarkGray    gui=italic guifg=DarkGray
hi Constant    term=underline  ctermfg=white    guifg=white
hi Special     term=bold    ctermfg=DarkMagenta  guifg=Red
hi Identifier  term=underline  cterm=bold      ctermfg=gray guifg=gray
hi Statement   term=bold    ctermfg=Yellow gui=bold  guifg=Yellow
hi PreProc     term=underline  ctermfg=LightBlue  guifg=#8888ff gui=bold
hi Type        term=underline    ctermfg=Magenta  guifg=purple
hi Function    term=bold    ctermfg=White guifg=White
hi Operator    ctermfg=green      guifg=green
hi Ignore      ctermfg=black    guifg=bg
hi String      term=bold ctermfg=Cyan guifg=Cyan
hi Error       term=reverse ctermbg=Red ctermfg=White guibg=Red guifg=Yellow
hi Todo        ctermbg=Yellow ctermfg=Black guifg=Blue guibg=Yellow
hi Number      ctermfg=white guifg=white

" Common groups that link to default highlighting.
" You can specify other highlighting easily.
hi link Character	String
hi link Boolean	Constant
hi link Float	Number
hi link Conditional	Statement
hi link Label	Statement
hi link Keyword	Statement
hi link Repeat	Keyword
hi link Exception	Statement
hi link Include	PreProc
hi link Define	PreProc
hi link Macro	PreProc
hi link PreCondit	PreProc
hi link StorageClass	Type
hi link Structure	Type
hi link Typedef	Type
hi link Tag	Special
hi link SpecialChar	Operator
hi link Delimiter	Operator
hi link SpecialComment	Special
hi link Debug	Special
