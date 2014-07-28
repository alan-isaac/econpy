" my filetype file
if exists("did_load_filetypes")
  finish
endif
augroup filetype
  au! BufRead,BufNewFile *.prg setfiletype eviews
  au! BufRead,BufNewFile *.gau setfiletype gauss
  au! BufRead,BufNewFile *.mma setfiletype mma
  au! BufRead,BufNewFile *.nlogo setfiletype netlogo
  au! BufRead,BufNewFile *.nlogo3d setfiletype netlogo
augroup END

