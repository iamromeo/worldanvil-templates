# global variables

tabsize=4
level = 0
clevel = 0
soutput = []
foutput = []
table = 0
horiz = 0
iter = 0


# -------------------------------------------------------------------------
def doLayout(line):
    global soutput, foutput, level, clevel, tabsize, table, horiz, iter
    line = line.replace("# ", "")
    cmd = line.split(':', 3)
    match cmd[0]:
        case 'card':
            soutput.append('<div class="card %s" id="card-%s">' % (cmd[1].strip(), cmd[1].strip()))
            if (len(cmd)==3):
                soutput.append("".ljust(tabsize)+('<div class="card-header %s">%s</div>' % (cmd[1].strip(), cmd[2].strip().title())))
            clevel = 1
        case '/card':
            soutput.append('</div>')
            level -= 1
        case 'card-body':
            soutput.append('<div class="card-body">')
            clevel = 1
        case '/card-body':
            soutput.append('</div>')
            level -= 1
        case 'col':
            soutput.append('<div class="%s">' % cmd[1].strip())
            clevel = 1
        case '/col':
            soutput.append('</div>')
            level -= 1
        case 'iter':
            iter = cmd[1].strip()
            soutput.append("{% for i in 1.."+iter+" %}")
            soutput.append("".ljust(tabsize)+"{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}")
            if (table==1):
                soutput.append("".ljust(tabsize)+"{% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}")
                if (horiz==1):
                    soutput.append("<tr>")
            clevel = 1
        case '/iter':
            if (table==1 and horiz==1):
                soutput.append("</tr>")
            iter = 0
            soutput.append("{% endfor %}")
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
            s="<table class='table'>"
            horiz = 0
            if (len(cmd)>1):
                if (cmd[1].strip()=="horiz"):
                    horiz = 1
            #        s += '<tr>'
            soutput.append(s)
            table = 1
            clevel = 1
        case '/table':
            s='</table>'
            #if (horiz==1):
            #    s += '</tr>'+s
            soutput.append(s)
            table = 0
            horiz = 0
            level -= 1
        case _:
            # print("ERROR: unknown element %s" % cmd[0])
            a = 0


# -------------------------------------------------------------------------
def doField(field, params):
    global soutput, foutput, level, clevel, tabsize, table, horiz, iter

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
    render = ""

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
        if ("render" == k):
            render = v.replace('"', '')
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
    # --- key:
    if  (table == 1):
        so = "<td class='lbl {{eo}} lbl-%s'>" % cf
        if (horiz == 0):
            so = "<tr>"+so
    else:
        so = "<div class='cContainer'><div class='lbl lbl-%s'> " % cf

    so += " "+label+" "

    if  (table == 1):
        so += "</td><td class='var {{eo}} var-%s'>" % cf
    else:
        so += "</div><div class='var var-%s'>" % cf

    # --- value, different by input type:
    if ("text" == type):
        if (iter == 0):
            so += " {{variables.%s|default|nl2br}} " % ff
        else:
            so += " {{attribute(variables, '%s_' ~ id)|default|nl2br}} " % ff

    elif ("checkbox" == type):
        if (iter == 0):
            so += "{% if variables.$ID|default == 1 %}<i class='fa-regular fa-square-check'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}" 
        else:
            so += "{% if attribute(variables, '$ID_' ~ id)|default|default == 1 %}<i class='fa-regular fa-square-check'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}" 
        so = so.replace("$ID", ff)

    elif ("string" == type):
        if (iter == 0):
            so += " {{variables.%s|default}} " % ff
        else:
            so += " {{attribute(variables, '%s_' ~ id)|default}} " % ff

    elif ("integer" == type):
        pre = ""
        post = ""
        if ("image" == render):
            pre = "[img:"
            post = "]"

        if (iter == 0):
            so += pre+("{{variables.%s|default}}" % ff)+post
        else:
            so += pre+("{{attribute(variables, '%s_' ~ id)|default}}" % ff)+post

    if  (table == 1):
        so += "</td>"
        if (horiz == 0):
            so += "</tr>"

    else:
        so += "</div></div>"

    # --- edit form
    if  (table == 1):
        fo = "<tr><td class='ilbl {{eo}} ilbl-%s' title='$DESC'>" % cf
    else:
        fo = "<div class='cContainer'><div class='ilbl ilbl-%s' title='$DESC'>" % cf

    fo += " "+label+" "

    if  (table == 1):
        fo += "</td><td class='ivar {{eo}} ivar-%s'>" % cf
    else:
        fo += "</div><div class='ivar ivar-%s'>" % cf

    if ("text" == type):
        if (iter == 0):
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s mention' id='%s' name='%s' placeholder='%s' $ROWS $REQUIRED >{{variables.%s|default}}</textarea></div>" % ( cf, ff, ff, pholder, ff)
        else:
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s mention' id='%s_{{id}}' name='%s{{id}}' placeholder='%s' $ROWS $REQUIRED >{{attribute(variables, '%s_' ~ id)|default}}</textarea></div>" % ( cf, ff, ff, pholder, ff)
        s = ""
        if (rows != ""):
            s = "rows='"+rows+"'"
        fo = fo.replace("$ROWS", s)
    elif ("string" == type):
        if (iter == 0):
            fo += "<input value='{{variables.%s|default}}' class='form-control ivar ivar-%s' id='%s' name='%s' placeholder='%s' type='text' $REQUIRED />" % ( ff, cf, ff, ff, pholder )
        else:
            fo += "<input value='{{attribute(variables, '%s_' ~ id)|default}}' class='form-control ivar ivar-%s' id='%s_{{id}}' name='%s_{{id}}' placeholder='%s' type='text' $REQUIRED />" % ( ff, cf, ff, ff, pholder )

    elif ("integer" == type):
        # fo += "<div class='iContent'>"
        if (iter == 0):
            fo += "<input value='{{variables.%s|default}}' class='form-control ivar ivar-%s' id='%s' name='%s' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % ( ff, cf, ff, ff, pholder )
        else:
            fo += "<input value='{{attribute(variables, '%s_' ~ id)|default}}' class='form-control ivar ivar-%s' id='_{{id}}' name='_{{id}}' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % ( ff, cf, ff, ff, pholder )

        s = ""
        if (min != ""):
            s = "min='"+min+"'"
        fo = fo.replace("$MIN", s)
        s = ""
        if (max != ""):
            s = "max='"+max+"'"
        fo = fo.replace("$MAX", s)
    elif ("checkbox" == type):
        if (iter == 0):
            fo += "<input value='0' id='%s' name='%s' type='hidden' />" % ( ff, ff )
            fo += "<input value='1' {% if variables.$ID > 0 %} checked='checked'{% endif %} id='$ID' name='$ID' type='checkbox' />"
        else:
            fo += "<input value='0' id='%s_{{id}}' name='%s_{{id}}' type='hidden' />" % ( ff, ff )
            fo += "<input value='1' {% if attribute(variables, '$ID_' ~ id)|default > 0 %} checked='checked'{% endif %} id='$ID_{{id}}' name='$ID_{{id}}' type='checkbox' />"
        fo = fo.replace("$ID", ff)

    if  (table == 1):
        fo += "</td></tr>"
    else:
        fo += "</div></div>"

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
