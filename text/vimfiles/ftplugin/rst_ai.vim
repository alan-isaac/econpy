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

set fileencoding=utf-8
colorscheme koehler

" add suffixes to gf searches
set suffixesadd=.rst 

