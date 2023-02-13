#
# @name: yml to sheet
# @version: 1.0
# @author: Tillerz#3807
# @date: 2023-02-12 
#

# global variables

# used for output formatting
tabsize=4

# current indentation level of the yml
level = 0
# level change after a layout command, gets added to level
clevel = 0

# 1 if the current output shall get rendered as a table
table = 0
# 1 if the current table shall get rendered horizontally
horiz = 0
# >0 if we are in a loop
iter = 0

sheet_output = []
form_output = []


# -------------------------------------------------------------------------
def doLayout(line):
    global sheet_output, form_output, level, clevel, tabsize, table, horiz, iter
    line = line.replace("# ", "")
    cmd = line.split(':', 3)
    match cmd[0]:
        case 'card':
            sheet_output.append('<div class="card %s" id="card-%s">' % (cmd[1].strip(), cmd[1].strip()))
            if (len(cmd)==3):
                sheet_output.append("".ljust(tabsize)+('<div class="card-header %s">%s</div>' % (cmd[1].strip(), cmd[2].strip().title())))
            clevel = 1
        case '/card':
            sheet_output.append('</div>')
            level -= 1
        case 'card-body':
            sheet_output.append('<div class="card-body">')
            clevel = 1
        case '/card-body':
            sheet_output.append('</div>')
            level -= 1
        case 'col':
            # open a col, default width is col-12 except overwritten by optional parameter
            s = "col-12"
            if (len(cmd)>1):
                s = cmd[1].strip()
            sheet_output.append('<div class="%s">' % s)
            clevel = 1
        case '/col':
            # close an existing col
            sheet_output.append('</div>')
            level -= 1
        case 'iter':
            # start rendering the section between iter and /iter several times
            # default is 10 times, number overwritten by optional parameter
            iter = 10
            if (len(cmd)>1):
                iter = cmd[1].strip()
            sheet_output.append("{% for i in 1.."+iter+" %}")
            sheet_output.append("".ljust(tabsize)+"{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}")
            # if we are in a table, do additional things
            if (table==1):
                # for tables, we want alternating classes ev and od being added
                sheet_output.append("".ljust(tabsize)+"{% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}")
                # if the table is horizontal, we need to open the table column here
                if (horiz==1):
                    sheet_output.append("<tr>")
            clevel = 1
        case '/iter':
            # stop the iterated section
            # if we are in a table, do additional things
            if (table==1 and horiz==1):
                # if the table is horizontal, we need to close the table column here
                sheet_output.append("</tr>")
            iter = 0
            sheet_output.append("{% endfor %}")
            level -= 1
        case 'row':
            # open a row (can contain several cols)
            sheet_output.append('<div class="row">')
            clevel = 1
        case '/row':
            # close an existing row
            sheet_output.append('</div>')
            level -= 1
        case 'sheet':
            # top line of the rendered sheet/form output
            s = "sheetname"
            if (len(cmd)>1):
                s = cmd[1].strip()
            sheet_output.append('<div class="container-fluid sheet-%s">' % s)
            clevel = 1
        case '/sheet':
            # bottom line of the rendered sheet/form output
            sheet_output.append('</div>')
            level -= 1
        case 'table':
            # we are rendering data inside a table until we encounter /table
            s="<table class='table'>"
            horiz = 0
            if (len(cmd)>1):
                if (cmd[1].strip()=="horiz"):
                    horiz = 1
            sheet_output.append(s)
            table = 1
            clevel = 1
        case '/table':
            # stop rendering inside a table
            s='</table>'
            sheet_output.append(s)
            table = 0
            horiz = 0
            level -= 1
        case _:
            print("ERROR: unknown element %s" % cmd[0])
            a = 0


# -------------------------------------------------------------------------
def doField(field, params):
    global sheet_output, form_output, level, clevel, tabsize, table, horiz, iter

    fieldname_for_class = field.replace(" ", "-")
    fieldname_for_form = field.replace(" ", "_")

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
        so = "<th class='lbl {{eo}} lbl-%s'>" % fieldname_for_class
        if (horiz == 0):
            so = "<tr>"+so
    else:
        so = "<div class='cContainer'><div class='lbl lbl-%s'>" % fieldname_for_class

    so += " "+label+" "

    if  (table == 1):
        so += "</th><td class='var {{eo}} var-%s' title='$DESC'>" % fieldname_for_class
    else:
        so += "</div><div class='var var-%s' title='$DESC'>" % fieldname_for_class

    # --- value, different by input type:
    if ("text" == type):
        if (iter == 0):
            so += " {{variables.%s|default|nl2br}} " % fieldname_for_form
        else:
            so += " {{attribute(variables, '%s_' ~ id)|default|nl2br}} " % fieldname_for_form

    elif ("checkbox" == type):
        if (iter == 0):
            so += "{% if variables.$ID|default == 1 %}<i class='fa-regular fa-square-check'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}" 
        else:
            so += "{% if attribute(variables, '$ID_' ~ id)|default|default == 1 %}<i class='fa-regular fa-square-check'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}" 
        so = so.replace("$ID", fieldname_for_form)

    elif ("string" == type):
        if (iter == 0):
            so += " {{variables.%s|default}} " % fieldname_for_form
        else:
            so += " {{attribute(variables, '%s_' ~ id)|default}} " % fieldname_for_form

    elif ("integer" == type):
        prefix = ""
        postfix = ""
        if ("image" == render):
            prefix = "[img:"
            postfix = "]"

        if (iter == 0):
            so += prefix+("{{variables.%s|default}}" % fieldname_for_form)+postfix
        else:
            so += prefix+("{{attribute(variables, '%s_' ~ id)|default}}" % fieldname_for_form)+postfix

    if  (table == 1):
        so += "</td>"
        if (horiz == 0):
            so += "</tr>"

    else:
        so += "</div></div>"

    # --- edit form
    if  (table == 1):
        fo = "<tr><th class='ilbl {{eo}} ilbl-%s' title='$DESC'>" % fieldname_for_class
    else:
        fo = "<div class='cContainer'><div class='ilbl ilbl-%s' title='$DESC'>" % fieldname_for_class

    fo += " "+label+" "

    if  (table == 1):
        fo += "</th><td class='ivar {{eo}} ivar-%s'>" % fieldname_for_class
    else:
        fo += "</div><div class='ivar ivar-%s'>" % fieldname_for_class

    if ("text" == type):
        if (iter == 0):
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s mention' id='%s' name='%s' placeholder='%s' $ROWS $REQUIRED >{{variables.%s|default}}</textarea></div>" % ( fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder, fieldname_for_form)
        else:
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s mention' id='%s_{{id}}' name='%s_{{id}}' placeholder='%s' $ROWS $REQUIRED >{{attribute(variables, '%s_' ~ id)|default}}</textarea></div>" % ( fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder, fieldname_for_form)
        s = ""
        if (rows != ""):
            s = "rows='"+rows+"'"
        fo = fo.replace("$ROWS", s)
    elif ("string" == type):
        if (iter == 0):
            fo += "<input value='{{variables.%s|default}}' class='form-control ivar ivar-%s' id='%s' name='%s' placeholder='%s' type='text' $REQUIRED />" % ( fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder )
        else:
            fo += "<input value='{{attribute(variables, '%s_' ~ id)|default}}' class='form-control ivar ivar-%s' id='%s_{{id}}' name='%s_{{id}}' placeholder='%s' type='text' $REQUIRED />" % ( fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder )

    elif ("integer" == type):
        # fo += "<div class='iContent'>"
        if (iter == 0):
            fo += "<input value='{{variables.%s|default}}' class='form-control ivar ivar-%s' id='%s' name='%s' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % ( fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder )
        else:
            fo += "<input value='{{attribute(variables, '%s_' ~ id)|default}}' class='form-control ivar ivar-%s' id='%s_{{id}}' name='%s_{{id}}' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % ( fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder )

        # add the optional min and max values
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
            fo += "<input value='0' id='%s' name='%s' type='hidden' />" % ( fieldname_for_form, fieldname_for_form )
            fo += "<input value='1' {% if variables.$ID > 0 %} checked='checked'{% endif %} id='$ID' name='$ID' type='checkbox' />"
        else:
            fo += "<input value='0' id='%s_{{id}}' name='%s_{{id}}' type='hidden' />" % ( fieldname_for_form, fieldname_for_form )
            fo += "<input value='1' {% if attribute(variables, '$ID_' ~ id)|default > 0 %} checked='checked'{% endif %} id='$ID_{{id}}' name='$ID_{{id}}' type='checkbox' />"
        fo = fo.replace("$ID", fieldname_for_form)

    if  (table == 1):
        fo += "</td></tr>"
    else:
        fo += "</div></div>"

    # append output to sheet
    if (so != ""):
        # replace variables
        so = so.replace("$DESC", desc)
        # remove empty parameters
        so = so.replace(" title=''", "")
        sheet_output.append(so)
    # append output to form
    if (fo != ""):
        # replace variables
        fo = fo.replace("$REQUIRED", required)
        fo = fo.replace("$DESC", desc)
        # remove empty parameters
        fo = fo.replace(" title=''", "")
        fo = fo.replace(" placeholder=''", "")
        form_output.append(fo)


# main() ------------------------------------------------------------------
print("Reading schema.yml")
# read the whole schema file into a list
file = open('schema.yml', mode = 'r', encoding = 'utf-8-sig')
lines = file.readlines()
file.close()

# open sheet and form file for writing
file_sheet = open('basic-sheet.html.twig', mode = 'w', encoding = 'utf-8-sig')
file_form = open('edit-form.html.twig', mode = 'w', encoding = 'utf-8-sig')

# loop over all schema lines and parse them
x = len(lines)
i=0
while (i<x):
    line = lines[i]
    # remember the current indentation level
    indent = len(line) - len(line.lstrip())
    line = line.strip()
    sheet_output=[]
    form_output=[]
    clevel = 0
    # all lines starting with # are for layout
    if (line.startswith('# ')):
        doLayout(line)
        # we want to use the layout for the form too
        if (len(sheet_output)>0 and len(form_output)<1):
            form_output = sheet_output
    elif (line.startswith('fields')):
        # we found the start of the actual yaml data
        print("Parsing YAML data")
    elif (line.startswith('###!')):
        # special comment, this is being printed to stdout during the parsing process
        print(line)
    elif (not line.startswith('###')):
        # parse everything else
        s = line.split(":")
        field = s[0]
        # looking for a key: line
        if (len(s)>1 and s[1]!=""):
            print("ERROR: field '%s' has more than one parameter, it should not." % field)
        # looking for indented key:value parameter lines, reading them all into a list
        z = (indent-1)*2
        params = []
        tmp = lines[i+1]
        while (tmp[:z-2+tabsize].isspace() and not tmp.lstrip().startswith("#")):
            params.append(tmp)
            i += 1
            tmp = lines[i+1]
        # got field and parameters, expand them
        doField(field, params)

    # write the output to the sheet file
    if (len(sheet_output)>0):
        for s in sheet_output:
            file_sheet.write("".ljust(level*tabsize)+s+"\n")
    # write the output to the form file
    if (len(form_output)>0):
        for s in form_output:
            file_form.write("".ljust(level*tabsize)+s+"\n")
    level += clevel
    i +=1

# close files
file_sheet.close()
file_form.close()
print("Finished")
