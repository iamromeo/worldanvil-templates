# global variables

tabsize=4
level = 0
clevel = 0
soutput = []
foutput = []
table = 0


# -------------------------------------------------------------------------
def doLayout(line):
    global soutput, foutput, level, clevel, tabsize, table
    line = line.replace("# ", "")
    cmd = line.split(':', 3)
    match cmd[0]:
        case 'card':
            soutput.append('<div class="card %s" id="card-%s">' % (cmd[1].strip(), cmd[1].strip()))
            if (len(cmd)==3):
                soutput.append("".ljust(tabsize)+('<div class="card-title %s">%s</div>' % (cmd[1].strip(), cmd[2].strip())))
            clevel = 1
        case '/card':
            soutput.append('</div>')
            level -= 1
        case 'col':
            soutput.append('<div class="%s">' % cmd[1].strip())
            clevel = 1
        case '/col':
            soutput.append('</div>')
            level -= 1
        case 'row':
            soutput.append('<div class="row">')
            clevel = 1
        case '/row':
            soutput.append('</div>')
            level -= 1
        case 'sheet':
            soutput.append('<div class="container-fluid sheet-%s">' % cmd[1].strip())
            clevel = 1
        case '/sheet':
            soutput.append('</div>')
            level -= 1
        case 'table':
            soutput.append('<table>')
            table = 1
            clevel = 1
        case '/table':
            soutput.append('</table>')
            table = 0
            level -= 1
        case _:
            # print("ERROR: unknown element %s" % cmd[0])
            a = 0


# -------------------------------------------------------------------------
def doField(field, params):
    global soutput, foutput, level, clevel, tabsize, table

    cf = field.replace(" ", "-")
    ff = field.replace(" ", "_")

    # parameters
    label = ""
    pholder = ""
    desc = ""
    min = ""
    max = ""
    type = ""
    required = ""
    rows = ""

    so = ""
    fo = ""

    # read all parameters
    x = len(params)
    i=0
    while (i<x):
        line = params[i]
        i += 1
        line = line.strip()
        s = line.split(":")
        k = s[0].strip()
        v = s[1].strip()
        if ("label" == k):
            label = v.replace('"', '').title()
        if ("placeholder" == k):
            pholder = v.replace('"', '')
        if ("description" == k):
            desc = v.replace('"', '').replace("'", "")
        if ("min" == k):
            min = v.replace('"', '')
        if ("max" == k):
            max = v.replace('"', '')
        if ("input" == k):
            type = v.replace('"', '')
        if ("required" == k):
            required = v.replace('"', '')
            if (required=="true"):
                required="required=required"
            else:
                required=''
        if ("rows" == k):
            rows = v.replace('"', '')

    # create output

    # --- basic sheet
    if  (table == 1):
        so = "<tr><td class='label label-%s'>" % cf
    else:
        so = "<div class='cContainer'><span class='label label-%s'> " % cf

    so += " "+label+" "

    if  (table == 1):
        so += "</td><td class='var var-%s'>" % cf
    else:
        so += "</span><span class='var var-%s'>" % cf

    if ("text" == type):
        so += " {{variables.%s|default|nl2br}} " % ff
    else:
        so += " {{variables.%s|default}} " % ff

    if  (table == 1):
        so += "</td></tr>"
    else:
        so += "</span></div>"

    # --- edit form
    if  (table == 1):
        fo = "<tr><td class='ilabel ilabel-%s' title='$DESC'>" % cf
    else:
        fo = "<div class='cContainer'><span class='ilabel ilabel-%s' title='$DESC'>" % cf

    fo += " "+label+" "

    if  (table == 1):
        fo += "</td><td class='ivar ivar-%s'>" % cf
    else:
        fo += "</span><span class='ivar ivar-%s'>" % cf

    if ("text" == type):
        fo += "<span class='iContent'><textarea class='form-control mention' id='%s' name='%s' placeholder='%s' $ROWS $REQUIRED >{{variables.%s|default}}</textarea></span>" % (ff, ff, pholder, ff)
        s = ""
        if (rows != ""):
            s = "rows='"+rows+"'"
        fo = fo.replace("$ROWS", s)
    elif ("string" == type):
        fo += "<input value='{{variables.%s|default}}' class='form-control %s' id='%s' name='%s' placeholder='%s' type='text' $REQUIRED />" % (ff, cf, ff, ff, pholder )

    elif ("integer" == type):
        fo += "<span class='iContent'>"
        fo += "<input value='{{variables.%s|default}}' class='form-control %s' id='%s' name='%s' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % (ff, cf, ff, ff, pholder )

        s = ""
        if (min != ""):
            s = "min='"+min+"'"
        fo = fo.replace("$MIN", s)
        s = ""
        if (max != ""):
            s = "max='"+max+"'"
        fo = fo.replace("$MAX", s)

    if  (table == 1):
        fo += "</td></tr>"
    else:
        fo += "</span></div>"

    if (so != ""):
        soutput.append(so)
    if (fo != ""):
        fo = fo.replace("$REQUIRED", required)
        fo = fo.replace("$DESC", desc)
        fo = fo.replace(" title=''", "")
        fo = fo.replace(" placeholder=''", "")
        foutput.append(fo)


# main() ------------------------------------------------------------------
file = open('schema.yml', mode = 'r', encoding = 'utf-8-sig')
lines = file.readlines()
file.close()

file_sheet = open('basic-sheet.html.twig', mode = 'w', encoding = 'utf-8-sig')
file_form = open('edit-form.html.twig', mode = 'w', encoding = 'utf-8-sig')

x = len(lines)
i=0
while (i<x):
    line = lines[i]
    soutput=[]
    foutput=[]
    clevel = 0
    indent = len(line) - len(line.lstrip())
    line = line.strip()
    if (line.startswith('# ')):
        doLayout(line)
        if (len(soutput)>0 and len(foutput)<1):
            foutput = soutput
    elif (line.startswith('fields')):
        print("Start")
    elif (line.startswith('###')):
        print(line)
    else:
        s = line.split(":")
        field = s[0]
        if (len(s)>1 and s[1]!=""):
            print("ERROR: field %s has parameters, it should not." % field)
        z = (indent-1)*2
        params = []
        tmp = lines[i+1]
        while (tmp[:z-2+tabsize].isspace() and not tmp.lstrip().startswith("#")):
            params.append(tmp)
            i += 1
            tmp = lines[i+1]
        doField(field, params)

    if (len(soutput)>0):
        for s in soutput:
            file_sheet.write("".ljust(level*tabsize)+s+"\n")
    if (len(foutput)>0):
        for s in foutput:
            file_form.write("".ljust(level*tabsize)+s+"\n")
    level += clevel
    i +=1

file_sheet.close()
file_form.close()
