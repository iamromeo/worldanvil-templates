#
# @name: yml to sheet
# @version: 1.0
# @author: Tillerz#3807
# @date: 2023-02-25
#

# global variables

# used for output formatting
tabsize = 4

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

lc = 0

counters = {
    'col': 0,
    'row': 0,
    'card': 0,
    'card-body': 0,
    'iter': 0,
    'sheet': 0,
    'table': 0
}


# -------------------------------------------------------------------------
def doError(field):
    global counters
    value = counters[field]
    if (value > 0):
        print("ERROR: # /"+field+" elements missing: %d" % value)
    if (value < 0):
        print("ERROR: superfluous # /"+field+" elements: %d" % abs(value))


# -------------------------------------------------------------------------
def doLayout(line):
    global sheet_output, form_output, level, clevel, tabsize, table, horiz, iter, lc
    line = line.replace("# ", "")
    cmd = line.split(':', 3)
    if cmd[0] == 'card':
        counters["card"] += 1
        s = ""
        if (len(cmd) > 1):
            s = cmd[1].strip()
        else:
            print("ERROR (line %s): %s needs a class name as parameter" %
                    (lc+1, cmd[0]))
        sheet_output.append('<div class="card %s" id="card-%s">' % (s, s))
        if (len(cmd) == 3):
            sheet_output.append("".ljust(
                tabsize)+('<div class="card-header %s">%s</div>' % (cmd[1].strip(), cmd[2].strip().title())))
        clevel = 1
    elif cmd[0] == '/card':
        counters["card"] -= 1
        sheet_output.append('</div>')
        level -= 1
    elif cmd[0] == 'card-body':
        counters["card-body"] += 1
        sheet_output.append('<div class="card-body">')
        clevel = 1
    elif cmd[0] == '/card-body':
        counters["card-body"] -= 1
        sheet_output.append('</div>')
        level -= 1
    elif cmd[0] == 'col':
        counters["col"] += 1
        # open a col, default width is col-12 except overwritten by optional parameter
        s = "col-12"
        if (len(cmd) > 1):
            s = cmd[1].strip()
        else:
            print("WARN (line %s): %s has no parameter, using %s as default" % (
                lc+1, cmd[0], s))
        sheet_output.append('<div class="%s">' % s)
        clevel = 1
    elif cmd[0] == '/col':
        counters["col"] -= 1
        # close an existing col
        sheet_output.append('</div>')
        level -= 1
    elif cmd[0] == 'iter':
        counters["iter"] += 1
        # start rendering the section between iter and /iter several times
        # default is 10 times, number overwritten by optional parameter
        iter = 10
        if (len(cmd) > 1):
            iter = cmd[1].strip()
        else:
            print("WARN (line %s): %s has no parameter, using %s as default" % (
                lc+1, cmd[0], iter))
        sheet_output.append("{% " + "for i in 1..%s" % iter + " %}")
        sheet_output.append("".ljust(
            tabsize)+"{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}")
        # if we are in a table, do additional things
        if (table == 1):
            # for tables, we want alternating classes ev and od being added
            sheet_output.append("".ljust(
                tabsize)+"{% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}")
            # if the table is horizontal, we need to open the table column here
            if (horiz == 1):
                sheet_output.append("<tr22222>")
        clevel = 1
    elif cmd[0] == '/iter':
        counters["iter"] -= 1
        # stop the iterated section
        # if we are in a table, do additional things
        if (table == 1 and horiz == 1):
            # if the table is horizontal, we need to close the table column here
            sheet_output.append("</tr22222>")
        iter = 0
        sheet_output.append("{% endfor %}")
        level -= 1
    elif cmd[0] == 'row':
        counters["row"] += 1
        # open a row (can contain several cols)
        sheet_output.append('<div class="row">')
        clevel = 1
    elif cmd[0] == '/row':
        counters["row"] -= 1
        # close an existing row
        sheet_output.append('</div>')
        level -= 1
    elif cmd[0] == 'sheet':
        counters["sheet"] += 1
        # top line of the rendered sheet/form output
        s = "sheetname"
        if (len(cmd) > 1):
            s = cmd[1].strip().replace(" ", "-")
        else:
            print("WARN (line %s): %s has no parameter, using %s as default" % (
                lc+1, cmd[0], s))
        sheet_output.append('<div class="container-fluid sheet-%s">' % s)
        clevel = 1
    elif cmd[0] == '/sheet':
        counters["sheet"] -= 1
        # bottom line of the rendered sheet/form output
        sheet_output.append('</div>')
        level -= 1
    elif cmd[0] == 'table':
        counters["table"] += 1
        # we are rendering data inside a table until we encounter /table
        s = "<table class='table'>"
        horiz = 0
        sheet_output.append(s)
        if (len(cmd) > 1):
            if (cmd[1].strip() == "horiz"):
                horiz = 1
        table = 1
        clevel = 1
    elif cmd[0] == '/table':
        counters["table"] -= 1
        if (horiz == 1):
            horiz = 0
        # stop rendering inside a table
        s = '</table>'
        sheet_output.append(s)
        table = 0
        level -= 1
    else:
        print("ERROR (line %s): unknown element %s" % (lc+1, cmd[0]))
        a = 0


# -------------------------------------------------------------------------
def doField(field, params):
    global sheet_output, form_output, level, clevel, tabsize, table, horiz, iter, lc

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

    options = []

    # read all parameters
    x = len(params)
    i = 0
    while (i < x):
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
            if (required == "true"):
                required = "required=required"
            else:
                required = ''
        if ("rows" == k):
            rows = v.replace('"', '')
        if ("options" == k):
            # loop over all options and save them to array for later
            while (i < x):
                options.append(params[i])
                i += 1

    # create output

    # --- basic sheet --------------------------------------------------------
    # --- print the label
    if (table == 1):
        so = "<th class='lbl {{eo}} lbl-%s'>" % fieldname_for_class
        if (horiz == 0):
            so = "<tr>"+so
    else:
        so = "<div class='cContainer'><div class='lbl lbl-%s'>" % fieldname_for_class

    so += " "+label+" "

    if (table == 1):
        so += "</th><td class='var {{eo}} var-%s' title='$DESC'>" % fieldname_for_class
    else:
        so += "</div><div class='var var-%s' title='$DESC'>" % fieldname_for_class

    # --- print the saved data, different per input type:
    if ("text" == type):
        if (iter == 0):
            so += " {{variables.%s|default|nl2br}} " % fieldname_for_form
        else:
            so += " {{attribute(variables, '%s_' ~ id)|default|nl2br}} " % fieldname_for_form

    if ("select" == type):
        if (iter == 0):
            so += " {{variables.%s|default}} " % fieldname_for_form
        else:
            so += " {{attribute(variables, '%s_' ~ id)|default}} " % fieldname_for_form

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
            so += prefix+("{{variables.%s|default}}" %
                          fieldname_for_form)+postfix
        else:
            so += prefix+("{{attribute(variables, '%s_' ~ id)|default}}" %
                          fieldname_for_form)+postfix

    if (table == 1):
        so += "</td>"
        if (horiz == 0):
            so += "</tr>"

    else:
        so += "</div></div>"

    # --- edit form ----------------------------------------------------------
    # --- print the label

    if (table == 1):
        fo = "<th class='ilbl {{eo}} ilbl-%s' title='$DESC'>" % fieldname_for_class
        if (horiz == 0):
            fo = "<tr>" + fo
    else:
        fo = "<div class='cContainer'><div class='ilbl ilbl-%s' title='$DESC'>" % fieldname_for_class

    fo += "<label for='%s'>%s</label>" % (fieldname_for_class, label)

    if (table == 1):
        fo += "</th><td class='ivar {{eo}} ivar-%s'>" % fieldname_for_class
    else:
        fo += "</div><div class='ivar ivar-%s'>" % fieldname_for_class

    # --- print the saved data, different per input type:
    if ("text" == type):
        if (iter == 0):
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s mention' id='%s' name='%s' placeholder='%s' $ROWS $REQUIRED >{{variables.%s|default}}</textarea></div>" % (
                fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder, fieldname_for_form)
        else:
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s mention' id='%s' name='%s_{{id}}' placeholder='%s' $ROWS $REQUIRED >{{attribute(variables, '%s_' ~ id)|default}}</textarea></div>" % (
                fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder, fieldname_for_form)
        s = ""
        if (rows != ""):
            s = "rows='"+rows+"'"
        fo = fo.replace("$ROWS", s)

    if ("select" == type):
        level += 1
        if (iter == 0):
            fo += "\n"+"".ljust(level*tabsize)+"<select $REQUIRED class='form-control ivar ivar-%s' id='%s' name='%s'>\n" % (
                fieldname_for_class, fieldname_for_form, fieldname_for_form)
        else:
            fo += "\n"+"".ljust(+level*tabsize)+"<select $REQUIRED class='form-control ivar ivar-%s' id='%s' name='%s_{{id}}'>\n" % (
                fieldname_for_class, fieldname_for_form, fieldname_for_form)

        x1 = len(options)
        i1 = 0
        while (i1 < x1):
            s1 = options[i1].strip().split(":")
            k1 = s1[0].strip()
            v1 = s1[1].strip()
            if (iter == 0):
                fo += "".ljust((level+1)*tabsize)+"<option value='" + k1 + \
                    "' {% if variables."+fieldname_for_form+"|default == '" + k1 + \
                    "' %}selected='selected' {% endif %} > " + \
                    v1 + " </option>\n"
            else:
                fo += "".ljust((level+1)*tabsize)+"<option value='" + k1 + \
                    "' {% if attribute(variables, '"+fieldname_for_form+"_' ~ id)|default == '" + \
                    k1 + \
                    "' %}selected='selected' {% endif %} > " + \
                    v1 + " </option>\n"
            i1 += 1
        fo += "".ljust(level*tabsize)+"</select>"
        level -= 1

    elif ("string" == type):
        if (iter == 0):
            fo += "<input value='{{variables.%s|default}}' class='form-control ivar ivar-%s' id='%s' name='%s' placeholder='%s' type='text' $REQUIRED />" % (
                fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder)
        else:
            fo += "<input value='{{attribute(variables, '%s_' ~ id)|default}}' class='form-control ivar ivar-%s' id='%s' name='%s_{{id}}' placeholder='%s' type='text' $REQUIRED />" % (
                fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder)

    elif ("integer" == type):
        # fo += "<div class='iContent'>"
        if (iter == 0):
            fo += "<input value='{{variables.%s|default}}' class='form-control ivar ivar-%s' id='%s' name='%s' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % (
                fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder)
        else:
            fo += "<input value='{{attribute(variables, '%s_' ~ id)|default}}' class='form-control ivar ivar-%s' id='%s' name='%s_{{id}}' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % (
                fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder)

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
            fo += "<input value='0' id='%s' name='%s' type='hidden' />" % (
                fieldname_for_form, fieldname_for_form)
            fo += "<input value='1' {% if variables.$ID|default > 0 %} checked='checked'{% endif %} id='$ID' name='$ID' type='checkbox' />"
        else:
            fo += "<input value='0' id='%s' name='%s_{{id}}' type='hidden' />" % (
                fieldname_for_form, fieldname_for_form)
            fo += "<input value='1' {% if attribute(variables, '$ID_' ~ id)|default > 0 %} checked='checked'{% endif %} id='$ID' name='$ID_{{id}}' type='checkbox' />"
        fo = fo.replace("$ID", fieldname_for_form)

    if (table == 1):
        fo += "</td>"
        if (horiz == 0):
            fo += "</tr>"
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
file = open('schema.yml', mode='r', encoding='utf-8-sig')
lines = file.readlines()
file.close()

# open sheet and form file for writing
file_sheet = open('basic-sheet.html.twig', mode='w', encoding='utf-8-sig')
file_form = open('edit-form.html.twig', mode='w', encoding='utf-8-sig')

# loop over all schema lines and parse them
x = len(lines)
lc = 0
while (lc < x):
    line = lines[lc]
    # remember the current indentation level
    indent = len(line) - len(line.lstrip())
    line = line.strip()
    sheet_output = []
    form_output = []
    clevel = 0
    # all lines starting with # are for layout
    if (line.startswith('# ')):
        doLayout(line)
        # we want to use the layout for the form too
        if (len(sheet_output) > 0 and len(form_output) < 1):
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
        if (len(s) > 1 and s[1] != ""):
            print("ERROR (line %s): field '%s' has more than one parameter, it should not." % (
                lc+1, field))
        # looking for indented key:value parameter lines, reading them all into a list
        z = (indent-1)*2
        params = []
        tmp = lines[lc+1]
        while (tmp[:z-2+tabsize].isspace() and not tmp.lstrip().startswith("#")):
            params.append(tmp)
            lc += 1
            tmp = lines[lc+1]
        # got field and parameters, expand them
        doField(field, params)

    # write the output to the sheet file
    if (len(sheet_output) > 0):
        for s in sheet_output:
            file_sheet.write("".ljust(level*tabsize)+s+"\n")
    # write the output to the form file
    if (len(form_output) > 0):
        for s in form_output:
            file_form.write("".ljust(level*tabsize)+s+"\n")
    level += clevel
    lc += 1

# close files
file_sheet.close()
file_form.close()

doError("col")
doError("row")
doError("card")
doError("card-body")
doError("iter")
doError("sheet")
doError("table")

print("Finished")
