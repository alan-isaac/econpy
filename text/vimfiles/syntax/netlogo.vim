" Vim syntax file
" Language:     NetLogo 5
" Maintainer:   Alan G. Isaac <aisaac@american.edu>
"   Tries to improve on the syntax file by Steven Stoddard
"   at http://voo-du.net/media/dump/nlogo.vim
" Copyright: 2014 Alan G. Isaac
" License: MIT http://opensource.org/licenses/MIT
" Last Change:  2014-07-29
" Filenames:    *.nlogo,*.nlogo~,*.nls

" TODO
" finish handling breeds (better approaches?)
" handle indenting
" make more NetLogo distinctions

if exists("b:current_syntax")
  finish
endif

syn case ignore

" Comment
syn keyword nlogoTodo contained TODO FIXME XXX
syn region nlComment start=";" end="$" keepend contains=nlogoTodo

" Constant
" a string is enclosed in double quotes
syn region nlogoString start=+"+ skip=+\\\\\|\\"+ end=+"+
" NetLogo "integer" (legal to start with 0!)

" all NetLogo numbers are floating point but have a variety of representations
" number: integer part, no fractional part, optional separator, optional exponent
syn match nlogoNumber /\<\d\+\.\=\([Ee][-+]\=\d\+\)\=/
" number: integer part, separator, fractional part, optional exponent
syn match nlogoNumber /\<\d\+\.\d\+\([Ee][-+]\=\d\+\)\=/
" number: no integer part, separator, fractional part, optional exponent
syn match nlogoNumber /\.\d\+\([Ee][-+]\=\d\+\)\=/

setlocal iskeyword+=-
setlocal iskeyword+=?

" Statement
syn keyword nlogoStatement carefully error-message report run runresult stop startup wait without-interruption error
syn keyword nlogoConditional if ifelse ifelse-value
syn keyword nlogoLogicalOperator and not or xor
syn keyword nlogoArithmeticOperator + - * /
syn keyword nlogoRepeat ask ask-concurrent repeat loop while foreach map
" Constant
syn keyword nlArithmeticConstant e pi
syn keyword nlColorConstant black gray white red orange brown yellow green lime
    \ turquoise cyan sky blue violet magenta pink
syn keyword nlogoBoolean false true

" Type
syn keyword nlogoDeclare __includes extensions globals patches-own turtles-own breed undirected-link-breed directed-link-breed
syn keyword nlogoType color heading hidden? label label-color pen-down? shape size who xcor ycor pcolor plabel plabel-color pxcor pycor patches turtles turtle patch BREED-at BREED-here BREED-on patch-ahead patch-at-heading-and-distance patch-here patch-left-and-ahead patch-right-and-ahead myself turtles-at turtles-from turtles-here turtles-on neighbors neighbors4 patch-left-and-ahead patch-right-and-ahead  other-turtles-here other-BREED-here

syn keyword nlogoTypeQuery is-agent? is-agentset? is-boolean? is-<breed>? is-command-task? is-directed-link? is-link? is-link-set? is-list? is-number? is-patch? is-patch-set? is-reporter-task? is-string? is-turtle? is-turtle-set? is-undirected-link? 

" Special
"syn match nlogoError      /[)\]}]/
"syn match nlogoCurlyError "]" 
"syn match nlogoCurlyError /[)\]]/ contained
"syn match nlogoParenError ")" 


" assignment
syn keyword nlogoDefine end let set to to-report task

syn keyword nlogoSpecial with of max-one-of min-one-of one-of random-n-of random-one-of with-max with-min bf butfirst but-first bl butlast but-last first last empty? any? all?

syn keyword nlogoKeyword back bk clear-ticks clear-turtles ct die distance distance-nowrap distancexy distancexy-nowrap downhill downhill4 dx dy forward fd hideturtle ht home inspect jump left lt no-label nobody pen-down pd pen-erase pe pen-up pu right rt self set-default-shape setxy shapes showturtle st stamp subtract-headings towards towards-nowrap towardsxy towardsxy-nowrap uphill clear-patches cp diffuse diffuse4 distance distance-nowrap distancexy distancexy-nowrap inspect no-label nobody nsum nsum4 self at-points count histogram-from in-radius in-radius-nowrap extract-hsb extract-rgb hsb rgb scale-color shade-of? wrap-color clear-all ca clear-drawing clear-patches cp  display follow home no-display no-label watch beep clear-output export-view export-interface export-output export-plot export-all-plots export-world get-date-and-time import-world mouse-down? mouse-xcor mouse-ycor output-print output-show output-type output-write print read-from-string reset-perspective rp reset-ticks reset-timer set-current-directory show show-turtle st timer type user-choice user-choose-directory user-choose-file user-choose-new-file user-input user-message user-one-of user-yes-or-no? write file-at-end? file-close file-close-all file-delete file-exists? file-open file-print file-read file-read-characters file-read-line file-show file-type file-write user-directory user-file user-new-file filter first fput item length list lput member? modes n-values position reduce remove remove-duplicates remove-item replace-item reverse sentence se shuffle sort sort-by sort-on sublist item length member? position remove remove-item read-from-string replace-item reverse substring word  abs acos asin atan ceiling cos exp floor int ln log max mean median min mod modes precision random random-exponential random-float random-gamma random-int-or-float random-normal random-poisson random-seed remainder round sin sqrt standard-deviation subtract-headings sum tan variance autoplot? auto-plot-off auto-plot-on clear-all-plots clear-plot export-plot export-all-plots histogram-from histogram-list plot plot-name plot-pen-down ppd plot-pen-reset plot-pen-up ppu plot-x-max plot-x-min plot-y-max plot-y-min plotxy ppd ppu resize-world set-current-plot set-current-plot-pen set-histogram-num-bars set-patch-size set-plot-pen-color set-plot-pen-interval set-plot-pen-mode set-plot-x-range set-plot-y-range setup-plots movie-cancel movie-close movie-grab-view movie-grab-interface movie-set-frame-rate movie-start movie-status follow home ride ride-me setxyz watch


syn keyword nlogoLinks
        \ links-own links link no-links both-ends other-end clear-links
        \ in-link-from
        \ layout-radial layout-spring layout-tutte link-heading link-length
        \ link-with my-in-links my-links my-out-links
        \ out-link-to hide-link show-link tie untie 


"TODO: in-BREED-from BREED-with <link-breeds>-own my-BREEDS my-in-BREEDS my-out-BREEDS out-BREED-to

"keywords get priority over matches, so we still list them
"(plus this allows easily turning off breed highlights)
syn keyword nlCreate
        \ create-turtles crt create-ordered-turtles cro create-temporary-plot-pen 
        \ create-link-from create-links-from create-link-to create-links-to create-link-with create-links-with
        \ hatch sprout

syn match nlCreate /\<create-\S\+/
syn match nlCreate /\<hatch-\S\+/
syn match nlCreate /\<sprout-\S\+/

" nlCreate handles these breed cases:
" hatch-BREED sprout-BREED 
" create-BREED-from create-BREEDS-from
" create-BREED-to create-BREEDS-to
" create-BREED-with create-BREEDS-with

syn keyword nlLinkNeighbor
        \ link-neighbor? link-neighbors
        \ in-link-neighbor? in-link-neighbors
        \ out-link-neighbor? out-link-neighbors

"handle breeds
syn match nlLinkNeighbor /\<\(in-\|out-\)\?\S\+-neighbor[?s]\>/

"       \ BREED-neighbor? BREED-neighbors
"       \ in-BREED-neighbor? in-BREED-neighbors
"       \ out-BREED-neighbor? out-BREED-neighbors

hi link nlComment               Comment
hi link nlArithmeticConstant    Constant
hi link nlColorConstant         Constant
hi link nlogoString            String
hi link nlogoNumber      Number
hi link nlogoBoolean     Boolean
hi link nlogoStatement   Statement
hi link nlogoConditional         Conditional
hi link nlogoLogicalOperator     Operator
hi link nlogoArithmeticOperator  Operator
hi link nlogoRepeat              Repeat
hi link nlogoKeyword             Keyword
hi link nlogoLinks               Keyword
hi link nlCreate                 Keyword
hi link nlLinkNeighbor           Keyword
hi link nlogoType                Type
hi link nlogoTypeQuery           Keyword
hi link nlogoDefine              Define
hi link nlogoDeclare             Define
hi link nlogoSpecial             Special
hi link nlogoError               Error
hi link nlogoBraceError          Error
hi link nlogoCurlyError          Error
hi link nlogoParenError          Error
hi link nlogoTodo                Todo

let b:current_syntax="nlogo"
