" myfiletypefile
augroup filetype
  au! BufRead,BufNewFile *.prg	set filetype=eviews
  au! BufRead,BufNewFile *.gau	set filetype=gauss
augroup END

