" NOTE:
" If you like these settings, proceed as follows.
" i. copy this file into your vimfiles folder
" (which was created upon installation), and
" ii. source this file from your _vimrc file
" E.g., add the following line to your _vimrc file:
" source $VIM/vimfiles/ai_vimrc

"act like Vim not like vi
set nocompatible
" **If** you love Windows behavior
" uncomment the next line (*if* it's not already in your _vimrc)
"source $VIMRUNTIME/mswin.vim
"remap keys for MS mouse behavior
behave mswin
set keymodel=startsel
" Switch syntax highlighting on, when the terminal has colors
if &t_Co > 2 || has("gui_running")
  syntax on
endif

"set working directory to current directory
au BufNewFile,BufEnter *  cd %:p:h
" if you prefer to do this manually, here is a map to
" change to directory of current buffer (see :help filename-modifiers)
" map ,cd :cd %:p:h<CR>

" allow cursor wrapping except with h and l
set whichwrap=b,s<,>,[,]
" display last-line even if long (vs. @@)
set display=lastline
"set valid characters for filenames
set isf=@,48-57,/,\\,.,-,_,+,,,$,%,[,],:,@-@,!,~,=
"disable maximum linewidth
set textwidth=0
"set long lines to wrap, breaking at whitespace
set wrap linebreak
" turn off automatic highlighting during search
set nohls
" allow backspacing over everything in insert mode
set backspace=indent,eol,start
set history=50		" keep 50 lines of command line history
set ruler		" show the cursor position all the time
set cmdheight=2
" allow hidden windows
set hidden
" maintain indent on new lines
filetype indent off
set autoindent
" ignore case for searches *unless* type caps (smartcase)
set ignorecase
set smartcase
" set file browser directory
set browsedir=buffer
" Make p in Visual mode replace the selected text with the "" register.
vnoremap p <Esc>:let current_reg = @"<CR>gvs<C-R>=current_reg<CR><Esc>
" When editing a file, always jump to the last known cursor position.
"  Don't do it when the position is invalid or when inside an event handler
"  (happens when dropping a file on gvim).
autocmd BufReadPost *
    \ if line("'\"") > 0 && line("'\"") <= line("$") |
    \   exe "normal g`\"" |
    \ endif

