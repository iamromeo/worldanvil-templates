#
# @name: yml to sheet
# @version: 1.2
# @author: @Tillerz (Discord)
# @date: 2023-07-08
#

import re

# VS Code does not switch to the folder the scipt is in, so we need to do it ourselves
import os
os.chdir(os.path.dirname(__file__))

# global variables

# used for output formatting
tabsize = 2

# current indentation level of the yml
level = 0
# level change after a layout command, gets added to level
clevel = 0

# 1 if the current output shall get rendered as a table
table = 0
# 1 if the current table shall get rendered horizontally
horiz = 0
# >0 if we are in a loop
iterf = 1
iter = 0
iter_in_table = 0
# even/odd alternating css class
eo = ""
# mention off by default, needs a trigger to enable it
mention = 0
# make it a bar with filled dots
dots = 0
# split header away from horiz table (default, use nosplit to include head in each table row)
split = 1
s_tableheader = ""
f_tableheader = ""
s_table = ""
f_table = ""
width = ""
tr_open = 0
sheet_output = []
form_output = []
yaml_output = []

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
    global yaml_output, sheet_output, form_output, level, clevel, tabsize, table, horiz, iterf, iter, iter_in_table, lc, eo, mention, dots, split, s_tableheader, f_tableheader, s_table, f_table, width, tr_open
    line = line.replace("# ", "")
    cmd = line.split(':', 3)
    if cmd[0] == 'card':
        counters["card"] += 1
        s = ""
        if (len(cmd) > 1):
            s = cmd[1].strip().lower()
        else:
            print("ERROR (line %s): %s needs a class name as parameter" % (lc+1, cmd[0]))
        sheet_output.append('<div class="card %s" id="card-%s">' % (s, s))
        if (len(cmd) == 3):
            sheet_output.append("".ljust(tabsize)+('<div class="card-header %s">%s</div>' % (cmd[1].strip().lower(), cmd[2].strip().title())))
        clevel = 1
    elif cmd[0] == '/card':
        counters["card"] -= 1
        sheet_output.append('</div>')
        level -= 1
        eo = ""
    elif cmd[0] == 'card-body':
        if (len(cmd) > 1):
            s = cmd[1].strip()
            if s == "mention":
                mention = 1
        counters["card-body"] += 1
        sheet_output.append('<div class="card-body of">')
        clevel = 1
    elif cmd[0] == '/card-body':
        mention = 0
        counters["card-body"] -= 1
        sheet_output.append('</div>')
        level -= 1
        eo = ""
    elif cmd[0] == 'col':
        counters["col"] += 1
        # open a col, default width is col-12 except overwritten by optional parameter
        s = "col-12"
        if (len(cmd) > 1):
            s = cmd[1].strip()
        else:
            print("WARN (line %s): %s has no parameter, using %s as default" % (lc+1, cmd[0], s))
        sheet_output.append('<div class="%s">' % s)
        clevel = 1
    elif cmd[0] == '/col':
        counters["col"] -= 1
        # close an existing col
        sheet_output.append('</div>')
        level -= 1
        eo = ""
    elif cmd[0] == 'dots':
        if (len(cmd) > 1):
            dots = cmd[1].strip()
    elif cmd[0] == 'include':
        ifile = open(cmd[1].strip(), mode='r', encoding='utf-8-sig')
        lines = ifile.readlines()
        ifile.close()
        if (len(lines) > 0):
            for s in lines:
                if (s.strip()!=""):
                    file_sheet.write(s)
                    file_form.write(s)
    elif cmd[0] == 'iter':
        counters["iter"] += 1
        # start rendering the section between iter and /iter several times
        # default is 10 times, number overwritten by optional parameter
        iterf = 1
        iter = 10
        if (len(cmd) > 1):
            iter = int(cmd[1].strip())
            if (len(cmd) > 2):
                iterf = int(cmd[1].strip())
                iter = int(cmd[2].strip())
        else:
            print("WARN (line %s): %s has no parameter, using 1 .. %s as default" % (lc+1, cmd[0], iter))
        if (table == 1 and horiz == 1):
            s_table += "{% " + "for i in %s..%s" % (iterf, iter) + " %}###"
            s_table += "".ljust(tabsize)+"{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}{% if id < 100 %}{% set id = '0' ~ id %}{% endif %}###"
            f_table += "{% " + "for i in %s..%s" % (iterf, iter) + " %}###"
            f_table += "".ljust(tabsize)+"{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}{% if id < 100 %}{% set id = '0' ~ id %}{% endif %}###"
        else:
            sheet_output.append("{% " + "for i in %s..%s" % (iterf, iter) + " %}")
            sheet_output.append("".ljust(tabsize)+"{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}{% if id < 100 %}{% set id = '0' ~ id %}{% endif %}")
        # if we are in a table, do additional things
        if (table == 1 and horiz == 1):
            s_table += "".ljust(tabsize)+"{% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}###<tr>###"
            f_table += "".ljust(tabsize)+"{% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}###<tr>###"
        else:
            sheet_output.append("".ljust(tabsize)+"{% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}")
        clevel = 1
    elif cmd[0] == '/iter':
        counters["iter"] -= 1
        # stop the iterated section
        # if we are in a table, do additional things
        if (table == 1):
            iter_in_table = 1
            if (horiz == 1):
                # if the table is horizontal, we need to close the table column here
                s_table += "###</tr>###{% endfor %}###"
                f_table += "###</tr>###{% endfor %}###"
        else:
            sheet_output.append("{% endfor %}")
        iter = 0
        level -= 1
        eo = ""
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
        eo = ""
    elif cmd[0] == 'sheet':
        counters["sheet"] += 1
        # top line of the rendered sheet/form output
        s = "sheetname"
        if (len(cmd) > 1):
            s = cmd[1].strip().lower().replace(" ", "-")
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
        sheet_output.append("<table class='table'>")
        form_output.append("<table class='table'>")
        counters["table"] += 1
        # we are rendering data inside a table until we encounter /table
        eo = "ev"
        horiz = 0
        split = 1
        tr_open = 0
        s_tableheader = ""
        f_tableheader = ""
        s_table = "$TABLEHEADER"
        f_table = "$TABLEHEADER"
        if (len(cmd) > 1):
            if (cmd[1].strip() == "horiz"):
                horiz = 1
                if (len(cmd) > 2):
                    if (cmd[2].strip() == "nosplit"):
                        split = 0
        table = 1
        clevel = 1
    elif cmd[0] == '/table':
        counters["table"] -= 1

        # start/end of row inside a horizontal table
        tro_h = ""
        trc_h = ""
        if (s_tableheader != "" and horiz == 1 and (iter_in_table == 1 or split == 1)):
            tro_h = "<tr>"
            trc_h = "</tr>"

        # insert tableheader + table into sheet
        if (s_table != ""):
            s_table = s_table.replace("$TABLEHEADER", tro_h+"###"+s_tableheader+"###"+trc_h+"###")
            tmp = re.split('###', s_table)
            for s in tmp:
                sheet_output.append(s)

        # insert tableheader + table into form
        if (f_table != ""):
            f_table = f_table.replace("$TABLEHEADER", tro_h+"###"+f_tableheader+"###"+trc_h+"###")
            tmp = re.split('###', f_table)
            for s in tmp:
                form_output.append(s)
        # close table

        if (tr_open == 1):
            sheet_output.append('</tr>')
            form_output.append('</tr>')

        sheet_output.append('</table>')
        form_output.append('</table>')

        iter_in_table = 0
        horiz = 0
        split = 1
        tr_open = 0
        table = 0
        level -= 1
        eo = "ev"
    elif cmd[0] == 'width':
        if (len(cmd) > 1):
            width = cmd[1].strip().lower().replace(" ", "")
    else:
        print("ERROR (line %s): unknown element %s" % (lc+1, cmd[0]))
        a = 0


# -------------------------------------------------------------------------
def doField(field, params):
    global yaml_output, sheet_output, form_output, level, clevel, tabsize, table, horiz, iterf, iter, iter_in_table, lc, eo, mention, dots, split, s_tableheader, f_tableheader, s_table, f_table, width, tr_open

    fieldname_for_yaml = re.sub('[^a-zA-Z0-9\-\_ ]', '', field).replace("_", " ").replace("-", " ").lower()
    fieldname_for_class = fieldname_for_yaml.replace(" ", "-")
    fieldname_for_form = fieldname_for_yaml.replace(" ", "_")

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
    mt = ""

    so = ""
    fo = ""

    options = []

    if mention == 1:
        mt = "mention"

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
            label = v.replace('"', '').replace("'", '')
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

    # ### create output ############################################################

    # === import yaml for WA =======================================================

    postfix = ""
    x = int(iterf)
    y = int(iter)
    if (y < 1):
        y = 1

    i = x
    while (i <= y):
        if (x != y):
            postfix = " %03d" % i

        yaml_output.append("  "+fieldname_for_yaml+postfix+":")
        yaml_output.append('    label: "'+fieldname_for_yaml+postfix+'"')
        if (desc != ""):
            yaml_output.append('    description: "'+desc+'"')
        else:
            yaml_output.append('    description: "'+label+'"')
        if (pholder != ""):
            yaml_output.append('    placeholder: "'+pholder+'"')
        if (required == "required=required"):
            yaml_output.append('    required: true')
        yaml_output.append('    input: '+type)
        if (rows != ""):
            yaml_output.append('    rows: '+rows)
        if (render != ""):
            yaml_output.append('    render: '+render)
        if (min != ""):
            yaml_output.append('    min: '+min)
        if (max != ""):
            yaml_output.append('    max: '+max)
        if (options != []):
            yaml_output.append('    options:')
            for s in options:
                yaml_output.append('      '+s.strip().replace("\n", ""))
        i += 1

    # --- basic for all ------------------------------------------------------------

    align = ""
    if ("checkbox" == type or "integer" == type):
        align = "c"

    tdwidth = ""
    if (width != ""):
        tdwidth = "width='%s'" % (width)

    # table <tr>s
    if (table == 1):
        if (iter == 0):
            if (horiz == 0):
                so += "<tr>"
                fo += "<tr>"
            else:
                if (split == 1):
                    so += "<tr>"
                    fo += "<tr>"
                else:
                    if (tr_open == 0):
                        s_tableheader += "<tr>"
                        f_tableheader += "<tr>"
                        tr_open = 1
        else:
            if (horiz == 0):
                so += "<tr>"
                fo += "<tr>"

    if (iter > 0 or (table == 1 and horiz == 1)):
        eo = "{{eo}}"
    else:
        if eo == "od":
            eo = "ev"
        else:
            eo = "od"
    eo2 = eo

    # === basic sheet ==============================================================

    # --- print the label
    if (label != ""):
        lalign = align
        if (iter == 0):
            lalign = ""
        if (table == 1):
            if (horiz == 1):
                if (split == 1):
                    eo2 = "od"
                    s_tableheader += "<th class='lbl %s lbl-%s %s' %s> %s </th>###" % (eo2, fieldname_for_class, lalign, tdwidth, label)
                else:
                    so += "<th class='lbl %s lbl-%s %s' %s title='$DESC'> %s </th>" % (eo, fieldname_for_class, lalign, tdwidth, label)
            else:
                so += "<th class='lbl %s lbl-%s %s' %s title='$DESC'> %s </th>" % (eo, fieldname_for_class, lalign, tdwidth, label)
        else:
            so += "<div class='lbl %s lbl-%s %s' %s title='$DESC'> %s </div>" % (eo, fieldname_for_class, lalign, tdwidth, label)
        # if we have a label/th, do not use the width for the field value also
        tdwidth = ""

    # --- print the saved data, different per input type:
    if (table == 1):
        so += "<td "
    else:
        so += "<div "
    so += "class='var %s var-%s %s' %s title='$DESC'>" % (eo, fieldname_for_class, align, tdwidth)

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
        if (dots == 0):
            if (iter == 0):
                so += " {{variables.%s|default}} " % fieldname_for_form
            else:
                so += " {{attribute(variables, '%s_' ~ id)|default}} " % fieldname_for_form
        else:
            # make a line of boxes:
            if (iter == 0):
                so += "{% set curr = variables."+fieldname_for_form+"|default %}"
            else:
                so += "{% set curr = attribute(variables, '"+fieldname_for_form+"_' ~ id)|default %}"
            so += "{% for i in 1.."+dots+" %}{% if i <= curr %}<i class='fa-solid fa-square'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}{% endfor %}"
            dots = 0
    elif ("integer" == type):
        if (dots == 0):
            prefix = ""
            postfix = ""
            # if it is an image, render it as such:
            if ("image" == render):
                prefix = "[img:"
                postfix = "]"
            if (iter == 0):
                so += prefix+("{{variables.%s|default}}" % fieldname_for_form)+postfix
            else:
                so += prefix+("{{attribute(variables, '%s_' ~ id)|default}}" % fieldname_for_form)+postfix
        else:
            # make a line of boxes:
            if (iter == 0):
                so += "{% set curr = variables."+fieldname_for_form+"|default %}"
            else:
                so += "{% set curr = attribute(variables, '"+fieldname_for_form+"_' ~ id)|default %}"
            so += "{% for i in 1.."+dots+" %}{% if i <= curr %}<i class='fa-solid fa-square'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}{% endfor %}"
            dots = 0

    if (table == 1):
        so += "</td>"
        if (iter == 0):
            if (horiz == 0):
                so += "</tr>"
            else:
                if (split == 1):
                    so += "</tr>"
        else:
            if (horiz == 0):
                so += "</tr>"
    else:
        so += "</div>"

    # === edit form =============================================================

    # --- print the label
    if (label != ""):
        lalign = align
        if (iter == 0):
            lalign = ""
        if (table == 1):
            if (horiz == 1):
                if (split == 1):
                    eo2 = "od"
                    f_tableheader += "<th class='ilbl %s ilbl-%s %s' %s><label for='%s'>%s</label></th>###" % (eo2, fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
                else:
                    fo += "<th class='ilbl %s ilbl-%s %s %s' title='$DESC'><label for='%s'>%s</label></th>" % (eo, fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
            else:
                fo += "<th class='ilbl %s ilbl-%s %s' %s title='$DESC'><label for='%s'>%s</label></th>" % (eo, fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
        else:
            fo = "<div class='ilbl %s ilbl-%s %s' %s title='$DESC'><label for='%s'>%s</label></div>" % (eo, fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
        # if we have a label/th, do not use the width for the field value also
        tdwidth = ""

    # --- print the saved data, different per input type:
    if (table == 1):
        fo += "<td "
    else:
        fo += "<div "
    fo += "class='ivar %s ivar-%s %s' %s title='$DESC'>" % (eo, fieldname_for_class, align, tdwidth)

    if ("text" == type):
        if (iter == 0):
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s %s' id='%s' name='%s' placeholder='%s' $ROWS $REQUIRED >{{variables.%s|default}}</textarea></div>" % (
                fieldname_for_class, mt, fieldname_for_form, fieldname_for_form, pholder, fieldname_for_form)
        else:
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s %s' id='%s' name='%s_{{id}}' placeholder='%s' $ROWS $REQUIRED >{{attribute(variables, '%s_' ~ id)|default}}</textarea></div>" % (
                fieldname_for_class, mt, fieldname_for_form, fieldname_for_form, pholder, fieldname_for_form)
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
                    "' %}selected='selected' {% endif %} > " + v1 + " </option>\n"
            else:
                fo += "".ljust((level+1)*tabsize)+"<option value='" + k1 + \
                    "' {% if attribute(variables, '"+fieldname_for_form+"_' ~ id)|default == '" + k1 + \
                    "' %}selected='selected' {% endif %} > " + v1 + " </option>\n"
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
            fo += "<input value='{{variables.%s|default}}' class='form-control ivar ivar-%s c' id='%s' name='%s' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % (
                fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder)
        else:
            fo += "<input value='{{attribute(variables, '%s_' ~ id)|default}}' class='form-control ivar ivar-%s c' id='%s' name='%s_{{id}}' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % (
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
            fo += "<input value='0' id='%s' name='%s' type='hidden' />" % (fieldname_for_form, fieldname_for_form)
            fo += "<input value='1' class='c' {% if variables.$ID|default > 0 %} checked='checked'{% endif %} id='$ID' name='$ID' type='checkbox' />"
        else:
            fo += "<input value='0' id='%s' name='%s_{{id}}' type='hidden' />" % (fieldname_for_form, fieldname_for_form)
            fo += "<input value='1' class='c' {% if attribute(variables, '$ID_' ~ id)|default > 0 %} checked='checked'{% endif %} id='$ID' name='$ID_{{id}}' type='checkbox' />"
        fo = fo.replace("$ID", fieldname_for_form)

    if (table == 1):
        fo += "</td>"
        if (iter == 0):
            if (horiz == 0):
                fo += "</tr>"
            else:
                if (split == 1):
                    fo += "</tr>"
        else:
            if (horiz == 0):
                fo += "</tr>"
    else:
        fo += "</div>"

    # --- end form -----------------------------------------------------------------

    width=""
  
    # append output to sheet
    if (so != ""):
        # replace variables
        so = so.replace("$DESC", desc)
        # remove empty parameters
        so = so.replace(" title=''", "")
        if (table == 1 and horiz == 1):
            s_table += so
        else:
            sheet_output.append(so)
    # append output to form
    if (fo != ""):
        # replace variables
        fo = fo.replace("$REQUIRED", required)
        fo = fo.replace("$DESC", desc)
        # remove empty parameters
        fo = fo.replace(" title=''", "")
        fo = fo.replace(" placeholder=''", "")
        if (table == 1 and horiz == 1):
            f_table += fo
        else:
            form_output.append(fo)


# main() ------------------------------------------------------------------


print("Reading schema.yml")
# read the whole schema file into a list
file = open('schema.yml', mode='r', encoding='utf-8-sig')
lines = file.readlines()
file.close()

# open files for writing
file_yaml = open('import-to-wa.yml', mode='w', encoding='utf-8-sig')
file_sheet = open('basic-sheet.html.twig', mode='w', encoding='utf-8-sig')
file_form = open('edit-form.html.twig', mode='w', encoding='utf-8-sig')

# get the indent size inside the yaml file
itabsize=2
x = len(lines)
lc = 0
while (lc < x):
    line = lines[lc]
    if (line.strip() !="" and not line.lower().startswith("fields:") and not line.lstrip().startswith("#") ):
        itabsize = len(line) - len(line.lstrip())
        lc = x
    lc += 1
print("YAML indent length: %s" % itabsize)

# loop over all schema lines and parse them
x = len(lines)
lc = 0
while (lc < x):
    line = lines[lc]
    if (lc == 0):
        if (line.startswith('fields')):
            # we found the start of the actual yaml data
            print("Parsing YAML data")
        else:
            print("ERROR (line %s): file must start with fields: in the first line." % (lc+1))
            exit(0)
    elif line.strip() != "":
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
        elif (line.startswith('###!')):
            # special comment, this is being printed to stdout during the parsing process
            print(line)
        elif (not line.startswith('###')):
            # parse everything else
            s = line.split(":")
            field = s[0]
            # looking for a key: line
            if (len(s) > 1 and s[1] != ""):
                print("ERROR (line %s): field '%s' has more than one parameter, it should not." % (lc+1, field))
            # looking for indented key:value parameter lines, reading them all into a list
            z = (indent-1)*2
            params = []
            tmp = lines[lc+1]
            while (tmp[:z+itabsize].isspace() and not tmp.lstrip().startswith("#")):
                params.append(tmp)
                lc += 1
                tmp = lines[lc+1]
            # got field and parameters, expand them
            doField(field, params)

        # write the output to the sheet file
        if (len(sheet_output) > 0):
            for s in sheet_output:
                s = "".ljust(level*tabsize)+s+"\n"
                if (s.lstrip()!=""):
                    file_sheet.write(s)
        # write the output to the form file
        if (len(form_output) > 0):
            for s in form_output:
                s = "".ljust(level*tabsize)+s+"\n"
                if (s.lstrip()!=""):
                    file_form.write(s)
        level += clevel
    lc += 1

file_yaml.write("fields:\n")
for s in yaml_output:
    if (s.lstrip()!=""):
        file_yaml.write(s+"\n")

# close files
file_sheet.close()
file_form.close()
file_yaml.close()
doError("col")
doError("row")
doError("card")
doError("card-body")
doError("iter")
doError("sheet")
doError("table")
print("Finished")
# eof