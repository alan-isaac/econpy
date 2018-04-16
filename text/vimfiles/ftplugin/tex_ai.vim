" Vim filetype plugin file
" Language:	 LaTeX
" Maintainer:	 Alan Isaac 
" Last Modified: 15th October 2002

" Only do this when not done yet for this buffer
if exists("b:loaded_tex_ai")
        finish
endif
" Don't reload plugin for this buffer
let b:loaded_tex_ai=1

let s:cpo_save=&cpo
set cpo&vim
colorscheme koehler

" add suffixes to gf searches
set suffixesadd=.tex

" LaTeX comment formatting
setlocal comments=b:%
"setlocal formatoptions-=t formatoptions+=rol
setlocal formatoptions=q

" Define patterns for the matchit macro
if !exists("b:match_words")
  let b:match_ignorecase = 0
  let b:match_words = '\begin:\end'
endif

set cpo-=C
set cpo+=B

" Define patterns for the browse file filter
if has("gui_win32") && !exists("b:browsefilter")
  let b:browsefilter = "LaTeX Files (*.tex)\t*.tex\n" .
    \ "Aux Files (*.aux)\t*.aux\n" .
    \ "Log Files (*.log)\t*.log\n" .
    \ "BibTeX Files (*.bib)\t*.bib\n" .
    \ "BibTeX Log Files (*.blg)\t*.blg\n" .
    \ "All Files (*.*)\t*.*\n"
endif


" ************* LaTeX environments ******************
imap <buffer> <unique> ;be <esc>ciw\begin{}<cr>\end{}<esc>"-Pk$"-Po
imap <buffer> <unique> *be <esc>ciw\begin{}<cr>\end{}<esc>"-Pi*<esc>k$"-Pi*<esc>o
imap <buffer> <unique> ;bm \begin{bmatrix}<cr>\end{bmatrix}<esc>O\\<esc>I
imap <buffer> <unique> ;en \begin{enumerate}<cr>\end{enumerate}<cr><esc>kO\item<space>
imap <buffer> <unique> ;al \begin{align}<cr>\\<cr>\end{align}<esc>kO&=<home>
imap <buffer> <unique> *al \begin{align*}<cr>\\<cr>\end{align*}<esc>kO&=<home>
imap <buffer> <unique> ;eq \begin{equation}<cr>\end{equation}<esc>O
imap <buffer> <unique> *eq \begin{equation*}<cr>\end{equation*}<esc>O
imap <buffer> <unique> ;sp \begin{split}<cr>\end{split}<esc>O&=<left><left>
imap <buffer> <unique> ;ml \begin{multline}<cr>\end{multline}<esc>O
imap <buffer> <unique> *ml \begin{multline*}<cr>\end{multline*}<esc>O
imap <buffer> <unique> ;ga \begin{gather}<cr>\end{gather}<esc>O
imap <buffer> <unique> *ga \begin{gather*}<cr>\end{gather*}<esc>O
imap <buffer> <unique> ;fn %<cr>\footnote{%<cr>}<cr>%<esc>-i
vmap <buffer> <unique> ;fn "xc%<cr>\footnote{%<cr>}<cr>%<esc>-"xP
imap <buffer> <unique> ;it \begin{itemize}<cr>\end{itemize}<cr><esc>kO\item<space>
imap <buffer> <unique> ;tr \begin{tabular}{cc}\hline\hline<cr>\hline<cr>\end{tabular}<cr><esc>kkkO
imap <buffer> <unique> ;th \begin{theorem}<cr>\end{theorem}<cr>\begin{mbProof}<cr>\end{mbProof}<cr><esc>3kO

"Greek letters
map! <buffer> <unique> 'ga \alpha
map! <buffer> <unique> 'gb \beta
map! <buffer> <unique> 'gc \chi
map! <buffer> <unique> 'gC \Chi
map! <buffer> <unique> 'gd \delta
map! <buffer> <unique> 'gD \Delta
map! <buffer> <unique> 'ge \varepsilon
map! <buffer> <unique> 'gf \phi
map! <buffer> <unique> 'gF \Phi
map! <buffer> <unique> 'gg \gamma
map! <buffer> <unique> 'gG \Gamma
map! <buffer> <unique> 'gh \eta
map! <buffer> <unique> 'gi \iota
map! <buffer> <unique> 'gj \varphi
map! <buffer> <unique> 'gk \kappa
map! <buffer> <unique> 'gl \lambda
map! <buffer> <unique> 'gL \Lambda
map! <buffer> <unique> 'gm \mu
map! <buffer> <unique> 'gn \nu
" map! <buffer> <unique> 'go \omicron
map! <buffer> <unique> 'gp \pi
map! <buffer> <unique> 'gP \Pi
map! <buffer> <unique> 'gq \theta
map! <buffer> <unique> 'gr \rho
map! <buffer> <unique> 'gR \Rho
map! <buffer> <unique> 'gs \sigma
map! <buffer> <unique> 'gS \Sigma
map! <buffer> <unique> 'gt \tau
map! <buffer> <unique> 'gu \upsilon
map! <buffer> <unique> 'gw \omega
map! <buffer> <unique> 'gW \Omega
map! <buffer> <unique> 'gx \xi
map! <buffer> <unique> 'gX \Xi
map! <buffer> <unique> 'gy \psi
map! <buffer> <unique> 'gY \Psi
map! <buffer> <unique> 'gz \zeta
map! <buffer> <unique> 'gZ \Zeta

" LaTeX math
imap <buffer> <unique> ;ht <c-r>="\\hat{".input("hat:")."}"<cr>
vmap <buffer> <unique> ;ht "xc\hat{}<esc>"xP
imap <buffer> <unique> ;br <c-r>="\\bar{".input("bar:")."}"<cr>
imap <buffer> <unique> ;dt <c-r>="\\dot{".input("dot:")."}"<cr>
imap <buffer> <unique> ;bf <c-r>="\\mathbf{".input("bold:")."}"<cr>
vmap <buffer> <unique> ;bf "xc\mathbf{}<esc>"xP
map! <buffer> <unique> ;fa \forall
map! <buffer> <unique> ;sm \setminus
map! <buffer> <unique> ;ex \exists
map! <buffer> <unique> ;cd \centerdot
map! <buffer> <unique> ;im \implies
map! <buffer> <unique> ;pa \partial
" sum with limits
imap <buffer> <unique> ;sl <c-r>="\\sum_{".input("from:")."}^{".input("to:")."}"<cr>
" sum with lower limit
imap <buffer> <unique> ;s_ <c-r>="\\sum_{".input("from:")."}"<cr>
imap <buffer> <unique> ;_ <c-r>="_{".input("sub:")."}"<cr>
imap <buffer> <unique> ;^ <c-r>="^{".input("sup:")."}"<cr>
imap <buffer> <unique> ;fr <c-r>="\\frac{".input("top:")."}{".input("bot:")."}"<cr>
vmap <buffer> <unique> ;fr "xc\frac{}<esc>"xPla{}<esc>i
imap <buffer> <unique> ;em <c-r>="\\emph{".input("emphasized text: ")."}"<cr>
nmap <buffer> <unique> ;em "xciw\emph{}<esc>"xP
vmap <buffer> <unique> ;em "xc\emph{}<esc>"xP
imap <buffer> <unique> ;mc <c-r>="\\mathcal{".input("caligraphic text: ")."}"<cr>
vmap <buffer> <unique> ;rm "xc\mathrm{}<esc>"xP
imap <buffer> <unique> ;tt <c-r>="\\texttt{".input("text: ")."}"<cr>
nmap <buffer> <unique> ;tt "xciw\texttt{}<esc>"xP
vmap <buffer> <unique> ;tt "xc\texttt{}<esc>"xP
cmap <buffer> <unique> ;tt \texttt{
imap <buffer> <unique> ;qq \qquad<space>
imap <buffer> <unique> ;a} <esc>/}<cr>a
imap <buffer> <unique> ;ch <c-r>="\\chapter{".input("chapter title: ")."}"<cr>
imap <buffer> <unique> ;sec <c-r>="\\section{".input("section title: ")."}"<cr>
imap <buffer> <unique> ;ssec <c-r>="\\subsection{".input("subsection title: ")."}"<cr>
imap <buffer> <unique> ;sssec <c-r>="\\subsubsection{".input("subsubsection title: ")."}"<cr>
imap <buffer> <unique> ;la <c-r>="\\label{".input("label name: ")."}"<cr>

" centering better than center env., which adds vertical space
imap <buffer> <unique> ;fgr \begin{figure}[tbp]<cr>\centering<cr>\includegraphics[width=\textwidth]{}<cr>\caption{}<cr>\label{f:}<cr>\end{figure}
imap <buffer> <unique> ;tbl \begin{table}[btp]<cr>\caption{}<cr>\label{t:}<cr>\centering<cr>\begin{tabular}{cc}\toprule<cr>\bottomrule<cr>\end{tabular}<cr>\end{table}<esc>?:<cr>a

"section motion for .tex files (redefines the usual section commands)
map <buffer> [[ k$?\\\(sub\)\{0,1}section[[{]<cr>
map <buffer> ]] /\\\(sub\)\{0,1}section[[{]<cr>

if exists("g:loaded_global_tex_ai")
        let &cpo = s:cpo_save
        finish
endif
let g:loaded_global_tex_ai = 1


let &cpo = s:cpo_save
sy region aitexComment matchgroup=aitexComment start=/\\begin{comment}/ end=/\\end{comment})/ contained
hi aitexComment ctermfg=gray guifg=gray
"EOF

