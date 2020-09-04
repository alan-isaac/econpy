"""Provides function `netlogo4to6` to convert NetLogo version 4 files
to NetLogo files that can be loaded by version 6.
(NOTE: NetLogo 6 will convert version 5 files itself.)
Please send comments to alan DOT isaac AT gmail DOT com.
"""
charsetProblem = """
Unhandled problematic characters:
NetLogo 4 files with characters outside of UTF-8
(e.g., from the old Windows character set)
will baffle this script. You will have to
remove these by hand, usually from the Info tab.
"""

import os, re, sys, textwrap, warnings

sectionsep = "@#$#@#$#@"
header = """Converted from NetLogo version 4 by netlogo4to6.py.
Known limitations:
1. Conversion does not handle lambdas.  (Therefore instances
   of `foreach` and `map` must be edited by hand.)
2. You may need to add by hand a `reset-ticks`
   command to the setup procedure.
"""
commentHeader = textwrap.indent(header, "; ")

def netlogo4to6(fpath): 
    """
    Version 4 sections are separated by sectionsep:
      0 : code
      1 : interface widgets
      2 : Info tab
      3 : shapes
      4 : version info
      5 : commands?
      6 : empty?
      7 : experiments
      8 : empty?
      9 : commands
      10 : empty (just end of file?)
    Version 6 adds a section:
      11 : 0
    Version 6 does not allow a CC-WINDOW widget.
    Version 6 buttons append a disable-until-ticks parameter (0 or 1).
    """
    global commentHeader
    if not fpath.endswith(".nlogo"):
        raise ValueError("not a .nlogo file")
    with open(fpath, "r", encoding="utf-8") as fin:
        try:
            data = fin.read()
        except UnicodeDecodeError:
            warnings.warn(charsetProblem)
            commentHeader += textwrap.indent(charsetProblem, "; ")
            data = open(fpath, "r").read()
    sections = list(map(lambda x:x.strip(), data.split(sectionsep)))
    #print(sections[0])
    if not (11 == len(sections)):
        _msg = "{} sections instead of the 11 expected from a version 4 file."
        assert (12 == len(sections) and sections[-1]==""), _msg.format(len(sections))
    if not sections[4].startswith("NetLogo 4"):
        raise ValueError("not a version 4 file")
    #fix the sections:
    sections[0] = commentHeader + fixCode( sections[0] )
    sections[1] = fixWidgets4to6(sections[1])
    sections[4] = "NetLogo 6.0.0"
    sections[7] = fixPrimitives4to6( sections[7] )
    sections.insert(-1, "0")
    #prepare output
    _sectionsep = "\n" + sectionsep + "\n"
    return _sectionsep.join(sections)

def fixWidgets4to6(widgetsAsString):
    oldWidgets = widgetsAsString.split("\n\n")
    if not oldWidgets[0].startswith("GRAPHICS-WINDOW"):
        raise ValueError("not a .nlogo file")
    newWidgets = list()
    for w in oldWidgets:
        if w.startswith("CC-WINDOW"):
            continue
        elif w.startswith("BUTTON"):
            w = w + "\n1"
        newWidgets.append( fixCode(w) )
    return "\n\n".join(newWidgets)

def fixCode(codeSection):
    lines = list()
    for line in codeSection.split("\n"):
        lines.append( fixPrimitives4to6(line) )
    return "\n".join(lines)

def fixPrimitives4to6(mystr):
    for cmd in ("update-plots", "clear-globals", "clear-ticks",
        "hubnet-clients-list", "hubnet-kick-client", "hubnet-kick-all-clients",
        "range", "sort-on", "stop-inspecting", "stop-inspecting-dead-agents"):
        mystr = re.sub("\\b" + cmd + "\\b", cmd + "-4to6", mystr)
    return mystr

if __name__=="__main__":
    for pth in sys.argv[1:]:
        fname, fext = os.path.splitext(pth) 
        outname = fname + "_v6" + fext
        with open(outname,"w") as fout:
            fout.write(netlogo4to6(pth))

