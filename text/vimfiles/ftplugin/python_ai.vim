" Only do this when not done yet for this buffer
if exists("b:loaded_python_ai")
        finish
endif

setlocal formatoptions-=t formatoptions+=rol
setlocal tabstop=4 shiftwidth=4 smarttab expandtab autoindent backspace=indent,eol,start
setlocal iskeyword=a-z,A-Z,48-57,_
