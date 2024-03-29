" MiKTeX MENUS for GVim:
" In your _gvimrc file, source this file or copy its contents.

" First set working directory to current directory
" (needed to ensure .dvi and .aux files are in same director as .tex file):
au BufEnter *.tex  cd %:p:h
"==========================================================
" MiKTeX menus setup:
" 1. set MIKTEXBIN to location of binaries
let MIKTEXBIN='C:\Program Files\MiKTeX 2.9\miktex\bin\x64\'
" 2. set GSPATH to full path to ghostscript\lib
let GSPATH='C:\programs\gs\gs8.64\lib\'
" 3. set GSVPATH to full path to ghostview32.exe
let GSVPATH='C:\programs\Ghostgum\gsview\gsview64.exe'
let PDFVIEWERPATH='D:\programs\SumatraPDF\SumatraPDF.exe'
let ACROPATH='C:\Program Files (x86)\Adobe\Acrobat 11.0\Acrobat\Acrobat.exe'
let NOTESPATH='C:\Users\aisaac\dpt\www\notes'
"==========================================================
silent amenu 90.10 &MiKTeX.Te&Xify :up<bar>:execute '!start "'.MIKTEXBIN.'texify.exe" "'.fnamemodify(@%,':p:r:gs?\\?/?').'.tex"'<cr>
silent amenu 90.20 &MiKTeX.View\ with\ PDF\ &Viewer :execute '!start "'.PDFVIEWERPATH.'" "'.fnamemodify(@%,':p:r').'.pdf"'<cr>
silent amenu 90.30 &MiKTeX.View\ with\ &Acrobat :execute '!start "'.ACROPATH.'" "'.fnamemodify(@%,':p:r:gs?\\?/?').'.pdf"'<cr>
silent amenu 90.35 &MiKTeX.View\ with\ &Yap :execute '!start "'.MIKTEXBIN.'yap.exe" "'.fnamemodify(@%,':p:r:gs?\\?/?').'.dvi"'<cr>
silent amenu 90.40 &MiKTeX.View\ with\ &GSview :execute '!start "'.GSVPATH.'" "'.fnamemodify(@%,':p:r:gs?\\?/?').'.ps"'<cr>
silent amenu 90.50 &MiKTeX.View\ Web\ &Notes :execute '!start cmd /c "'.NOTESPATH.'\'.fnamemodify(@%,':r').'.html"'<cr>
" silent amenu 90.50 &MiKTeX.&Run\ local\ batch :execute '!start "'.fnamemodify(@%,':p:r:gs?\\?/?').'.bat"'<cr>
amenu 90.100 &MiKTeX.-SEP1-			:
silent amenu 90.110 &MiKTeX.&luatex :up<bar>:execute '!start "'.MIKTEXBIN.'lualatex.exe" "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr><cr>
silent amenu 90.120 &MiKTeX.&pdflatex :up<bar>:execute '!start "'.MIKTEXBIN.'pdflatex.exe" --shell-escape "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr><cr>
silent amenu 90.130 &MiKTeX.La&TeX :up<bar>:silent execute '!start "'.MIKTEXBIN.'latex.exe" "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
silent amenu 90.140 &MiKTeX.&Biber :execute '!start "'.MIKTEXBIN.'biber.exe" "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
silent amenu 90.145 &MiKTeX.&BibTeX :execute '!start "'.MIKTEXBIN.'bibtex.exe" "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
" silent amenu 90.150 &MiKTeX.Make&Index :execute '!start "'.MIKTEXBIN.'makeindex.exe" "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
silent amenu 90.150 &MiKTeX.Make&Index :execute '!start "'.MIKTEXBIN.'makeindex.exe" "'.fnamemodify(@%,':r:gs?\\?/?').'"'<cr>
" amenu 90.200 &MiKTeX.-SEP2-			:
" silent amenu 90.210 &MiKTeX.dvip&s :execute '!start "'.MIKTEXBIN.'dvips.exe" -Ppdf "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
" silent amenu 90.220 &MiKTeX.dvipdf&m :execute '!start "'.MIKTEXBIN.'dvipdfm.exe" -vv "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
" silent amenu 90.230 &MiKTeX.dvipdfm(landscape) :execute '!start "'.MIKTEXBIN.'dvipdfm.exe" -l "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
" silent amenu 90.240 &MiKTeX.dvipdfmx :execute '!start "'.MIKTEXBIN.'dvipdfmx.exe" -vv "'.fnamemodify(@%,':p:r:gs?\\?/?').'"'<cr>
" silent amenu 90.260 &MiKTeX.ps&2pdf :execute '!start "'.GSPATH.'ps2pdf.bat" "'.fnamemodify(@%,':p:r:gs?\\?/?').'.ps"'<cr>
