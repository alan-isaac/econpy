" myfiletypefile
augroup filetype
  au! BufRead,BufNewFile *.prg	set filetype=eviews
  au! BufRead,BufNewFile *.gau	set filetype=gauss
  au! BufRead,BufNewFile *.mma	set filetype=mma sw=2
augroup END

