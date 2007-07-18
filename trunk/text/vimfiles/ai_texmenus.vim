" MiKTeX MENUS:
" We first set working directory to current directory
" (needed to ensure .dvi and .aux files are in same director as .tex file)
au BufEnter *.tex  cd %:p:h
"==========================================================
" MiKTeX menus setup:
" 1. set MIKTEXBIN to location of binaries
let MIKTEXBIN='C:\programs\MiKTeX2.6\miktex\bin\'
" 2. set GSPATH to full path to ghostscript\lib
let GSPATH='C:\programs\gs\gs8.51\lib\'
" 3. set GSVPATH to full path to ghostview32.exe
let GSVPATH='C:\programs\Ghostgum\gsview\gsview32.exe'
silent amenu 90.10 &MiKTeX.&Texify :up<bar>:execute '!start '.MIKTEXBIN.'texify.exe "'.fnamemodify(@%,':p:r:gs?\\?/?').'.tex"'<cr>
silent amenu 90.20 &MiKTeX.View\ with\ (&yap) :execute '!start '.MIKTEXBIN.'yap.exe "'.fnamemodify(@%,':p:r:gs?\\?/?').'.dvi"'<cr>
silent amenu 90.30 &MiKTeX.View\ with\ (&gsview) :execute '!start '.GSVPATH.' "'.fnamemodify(@%,':p:r:gs?\\?/?').'.ps"'<cr>
amenu 90.100 &MiKTeX.-SEP1-			:
silent amenu 90.110 &MiKTeX.&LaTeX :up<bar>:silent execute '!start '.MIKTEXBIN.'latex.exe &latex "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
silent amenu 90.120 &MiKTeX.&BibTeX :execute '!start '.MIKTEXBIN.'bibtex.exe "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
silent amenu 90.130 &MiKTeX.Make&Index :execute '!start '.MIKTEXBIN.'makeindex.exe "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
amenu 90.200 &MiKTeX.-SEP2-			:
silent amenu 90.210 &MiKTeX.dvip&s :execute '!start '.MIKTEXBIN.'dvips.exe -Ppdf "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
silent amenu 90.220 &MiKTeX.dvipdf&m :execute '!start '.MIKTEXBIN.'dvipdfm.exe -vv "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
silent amenu 90.230 &MiKTeX.dvipdfm(landscape&) :execute '!start '.MIKTEXBIN.'dvipdfm.exe -l "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
silent amenu 90.240 &MiKTeX.dvipdfm&x :execute '!start '.MIKTEXBIN.'dvipdfmx.exe -vv "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
silent amenu 90.250 &MiKTeX.&pdflatex :up<bar>:execute '!start '.MIKTEXBIN.'pdflatex.exe "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr><cr>
silent amenu 90.260 &MiKTeX.ps&2pdf :execute '!start '.GSPATH.'ps2pdf.bat "'.fnamemodify(@%,':p:r:gs?\\?/?').'.ps"'<cr>
" If you want to use aspell, install it and set aspellbin to location of binary
let aspellbin='C:\programs\aspell\bin\'
" If you want to use a personal dictionary (recommended), set aspellpersonal
let aspellpersonal='--personal C:\mydocs\alan.pws'
amenu 90.270 &MiKTeX.&aspell :up<bar>:execute '!'.aspellbin.'aspell.exe '.aspellpersonal. ' check "'.fnamemodify(@%,':p:gs?\\?/?').'"'<cr>

