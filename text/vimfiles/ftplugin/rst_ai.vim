" reStructuredText filetype plugin file
" Language:	 reStructuredText
" Maintainer:	 Alan Isaac 
" Last Modified: 15th June 2009

" Only do this when not done yet for this buffer
if exists("b:loaded_rst_ai")
        finish
endif
" Don't reload plugin for this buffer
let b:loaded_rst_ai=1

setl fileencoding=utf-8
colorscheme koehler

" add suffixes to gf searches
set suffixesadd=.rst 

setl shiftwidth=3
setl tabstop=3

"section motion for .rst files (redefines section commands)
" (keeppattern prevent altering the search history)
nmap <buffer> [[ k$:keeppattern ?^=\+$<cr>k
nmap <buffer> ]] j$:keeppattern /^=\+$<cr>k
vmap <buffer> [[ k$?^=\+$<cr>k
vmap <buffer> ]] j$/^=\+$<cr>k

