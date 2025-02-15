#
# @name: yaml to sheet
# @version: 1.4
# @author: @Tillerz (Discord & World Anvil)
# @date: 2024-02-03
#

import re
from datetime import date
today = date.today().strftime("%Y-%m-%d")

# VS Code (Windows) does not switch to the folder the scipt is in, so we need to do it ourselves
from sys import platform
if (platform == 'win32' or platform == 'cygwin'):
    import os
    os.chdir(os.path.dirname(__file__))

# global variables

# used for twig file output formatting
tabsize = 2

# current indentation level of the input yml
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
# storage for the output data
sheet_output = []
form_output = []
yaml_output = []
# set to 1 if the script has a reason to quit (eg if # /sheet is found)
quit = 0
# line counter
lc = 0
# field counter
fc = 0
# formatting tag counter
tc = 0

# open + close counters, throws error if number is not 0 after parsing
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
def clean(s, level):
    global tabsize, today

    s = "".ljust(level*tabsize)+s.replace("TIMESTAMP", today)+"\n"

    # remove superfluous spaces
    s = s.replace("' >", "'>")
    s = s.replace(" '>", "'>")
    s = s.replace(" ' >", "'>")
    s = s.replace("  />", " />")
    s = s.replace("  />", " />")
    s = s.replace("  />", " />")
    return s


# -------------------------------------------------------------------------
def doLayout(line):
    global yaml_output, sheet_output, form_output, level, clevel, tabsize, table, horiz, iterf, iter, iter_in_table, lc, eo, mention, dots, split, s_tableheader, f_tableheader, s_table, f_table, width, tr_open, quit, tc
    # "    # CoMManD ..." ->  "command ..."
    line = line.strip().replace("# ", "", 1).strip()
    cmd = line.split(':', 3)
    cmd[0] = cmd[0].lower()
    tc += 1

    # parse the "# <keyword> : <param> : ..." commands
    if cmd[0] == 'br':
        sheet_output.append("<br class='linebreak'>")
    elif cmd[0] == 'card':
        counters["card"] += 1
        s = ""
        if (len(cmd) > 1):
            s = cmd[1].strip().lower()
        else:
            print("ERROR (line %s): %s needs a class name as parameter" % (lc+1, cmd[0]))
        sheet_output.append("<div class='card %s' id='card-%s'>" % (s, s))
        if (len(cmd) == 3):
            sheet_output.append("".ljust(tabsize)+("<div class='card-header %s'>%s</div>" % (cmd[1].strip().lower(), cmd[2].strip().title())))
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
        sheet_output.append("<div class='card-body of'>")
        clevel = 1
    elif cmd[0] == '/card-body':
        mention = 0
        counters["card-body"] -= 1
        sheet_output.append('</div>')
        level -= 1
        eo = ""
    elif cmd[0] == 'col':
        counters["col"] += 1
        # open a col, default width is col-12 except overwritten by optional parameter, can be anything like "col-12 col-sm-6 ..."
        s = "col-12"
        if (len(cmd) > 1):
            s = cmd[1].strip()
        else:
            print("WARN (line %s): %s has no parameter, using %s as default" % (lc+1, cmd[0], s))
        sheet_output.append("<div class='%s'>" % s)
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
    elif cmd[0] == 'hr':
        sheet_output.append("<hr class='separator'>")
    elif cmd[0] == 'include':
        ifile = open(cmd[1].strip(), mode='r', encoding='utf-8-sig')
        lines = ifile.readlines()
        ifile.close()
        if (len(lines) > 0):
            for s in lines:
                if (s.strip()!=""):
                    sheet_output.append(s.rstrip())
                    form_output.append(s.rstrip())
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
            s1 = "{% " + "for i in %s..%s" % (iterf, iter) + " %}###"
            s2 = "".ljust(tabsize)+"{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}{% if id < 100 %}{% set id = '0' ~ id %}{% endif %}###"
            s_table += s1
            s_table += s2
            f_table += s1
            f_table += s2
        else:
            sheet_output.append("{% " + "for i in %s..%s" % (iterf, iter) + " %}")
            sheet_output.append("".ljust(tabsize)+"{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}{% if id < 100 %}{% set id = '0' ~ id %}{% endif %}")
        # if we are in a table, do additional things
        if (table == 1 and horiz == 1):
            s1 = "".ljust(tabsize)+"{% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}###<tr>###"
            s_table += s1
            f_table += s1
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
        else:
            sheet_output.append("{% endfor %}")
        iter = 0
        level -= 1
        eo = ""
    elif cmd[0] == 'row':
        counters["row"] += 1
        # open a row (can contain several cols)
        sheet_output.append("<div class='row'>")
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
        sheet_output.append("<div class='container-fluid sheet-%s'>" % s)
        clevel = 1
    elif cmd[0] == '/sheet':
        counters["sheet"] -= 1
        # bottom line of the rendered sheet/form output
        sheet_output.append('</div>')
        level -= 1
        quit = 1
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
        if (s_tableheader != "" and horiz == 1 and (iter_in_table == 1 or split == 1) and s_tableheader.find("<tr>")==-1):
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
        tc -= 1
        print("ERROR (line %s): unknown element %s" % (lc+1, cmd[0]))
        a = 0


# -------------------------------------------------------------------------
def doField(field, params):
    global yaml_output, sheet_output, form_output, level, clevel, tabsize, table, horiz, iterf, iter, iter_in_table, lc, eo, mention, dots, split, s_tableheader, f_tableheader, s_table, f_table, width, tr_open

    fieldname_for_yaml = re.sub('[^a-zA-Z0-9\-\_ ]', '', field).replace("_", " ").replace("-", " ").lower()
    fieldname_for_class = fieldname_for_yaml.replace(" ", "-")
    fieldname_for_form = fieldname_for_yaml.replace(" ", "_")

    # parameters
    desc = ""
    label = ""
    max = ""
    min = ""
    mt = ""
    options = []
    pholder = ""
    render = ""
    required = ""
    rows = ""
    style = ""
    type = ""
    imgwidth = ""

    so = ""
    fo = ""

    if mention == 1:
        mt = "mention"

    # read all parameters
    x = len(params)
    i = 0
    while (i < x):
        line = params[i]
        i += 1
        line = line.strip()
        s = line.split(":", 1)
        k = s[0].strip()
        v = s[1].strip()
        if ("description" == k):
            desc = v.replace('"', '').replace("'", "")
        if ("input" == k):
            type = v.replace('"', '').lower()
        if ("label" == k):
            label = v.replace('"', '').replace("'", '')
        if ("max" == k):
            max = v.replace('"', '')
        if ("min" == k):
            min = v.replace('"', '')
        if ("options" == k):
            # loop over all options and save them to array for later
            while (i < x):
                options.append(params[i])
                i += 1
        if ("placeholder" == k):
            pholder = v.replace('"', '')
        # will render any number/string input as [img:xxx] in the presentation sheet
        if ("render" == k):
            render = v.replace('"', '')
        # makes any input field mandatory, preventing save as long as it is empty
        if ("required" == k):
            required = v.replace('"', '')
            if (required == "true"):
                required = "required=required"
            else:
                required = ''
        # rows for input:text - number of rows
        if ("rows" == k):
            rows = v.replace('"', '')
        # style for text: - this can be open/close tag like h1, h2, b
        if ("style" == k):
            style = re.sub('[\'"$%<>#]', '', v)
        # URL for image:
        if ("url" == k):
            url = v.replace('"', '')
        # width for image:
        if ("width" == k):
            imgwidth = v.replace('"', '').replace("'", '')

    # ### create output ############################################################

    if ("image" == field):
        if (imgwidth != ""):
            imgwidth = "width='" + imgwidth + "'"
        s = "<img class='%s' src='%s' title='%s' %s>" % (fieldname_for_class, url, label, imgwidth)
        sheet_output.append(s)
        form_output.append(s)
        return
    if ("text" == field):
        if (style != ""):
            s = "<span class='%s'><%s>%s</%s></span>" % (fieldname_for_class, style, label, style)
        else:
            s = "<span class='%s'>%s</span>" % (fieldname_for_class, label)
        sheet_output.append(s)
        form_output.append(s)
        return

    # ### generate yaml for WA import #############################################

    postfix = ""
    x = int(iterf)
    y = int(iter)
    if (y < 1):
        y = 1

    i = x
    while (i <= y):
        if (x != y):
            postfix = " %03d" % i

        # name:
        #   label: "<text>"         - mandatory
        #   input: <input type>     - mandatory
        #   description: "<text>"   - optional
        #   placeholder: "<text>"   - optional
        #   required: true          - optional
        #   rows: <rows>            - only for input: text
        #   render: <image>         - only for input: image
        #   min: <integer>          - only for input: integer
        #   max: <integer>          - only for input: integer
        #   options:                - only for input: select
        #     x: x ...              - only for input: select

        yaml_output.append("".ljust(1*tabsize)+fieldname_for_yaml+postfix+":")
        yaml_output.append("".ljust(2*tabsize)+'label: "'+fieldname_for_yaml+postfix+'"')
        yaml_output.append("".ljust(2*tabsize)+'input: '+type)

        if (desc != ""):
            yaml_output.append("".ljust(2*tabsize)+'description: "'+desc+'"')
        else:
            yaml_output.append("".ljust(2*tabsize)+'description: "'+label+'"')
        if (pholder != ""):
            yaml_output.append("".ljust(2*tabsize)+'placeholder: "'+pholder+'"')
        if (required == "required=required"):
            yaml_output.append("".ljust(2*tabsize)+'required: true')
        if (rows != ""):
            yaml_output.append("".ljust(2*tabsize)+'rows: '+rows)
        if (render != ""):
            yaml_output.append("".ljust(2*tabsize)+'render: '+render)
        if (min != ""):
            yaml_output.append("".ljust(2*tabsize)+'min: '+min)
        if (max != ""):
            yaml_output.append("".ljust(2*tabsize)+'max: '+max)
        if (options != []):
            yaml_output.append("".ljust(2*tabsize)+'options:')
            for s in options:
                yaml_output.append("".ljust(3*tabsize)+s.strip().replace("\n", ""))
        i += 1

    # --- basic for all ------------------------------------------------------------

    # always center checkboxes and numbers (css class '.c')
    align = ""
    if ("checkbox" == type or "number" == type):
        align = "c"

    # table column width gived, add it
    tdwidth = ""
    if (width != ""):
        tdwidth = "width='%s'" % (width)

    # table <tr>
    # for debugging table formatting: print("table %s iter %s horiz %s split %s" % (table, iter, horiz, split) )
    if (table == 1):
        if (iter == 0):
            if (horiz == 0):
                so += "<tr>"
                fo += "<tr>"
            else:
                if (split == 1):
                    if (tr_open == 0):
                        so += "<tr>"
                        fo += "<tr>"
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
    tdwith_orig=tdwidth
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
    elif ("integer" == type or "number" == type):
        type = "number"
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
                    if (tr_open == 0):
                        so += "</tr>"
                        tr_open = 0
        else:
            if (horiz == 0):
                so += "</tr>"
    else:
        so += "</div>"

    # === edit form =============================================================

    tdwidth=tdwith_orig

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
                    tdwidth = ""
                else:
                    fo += "<th class='ilbl %s ilbl-%s %s %s' title='$DESC'><label for='%s'>%s</label></th>" % (eo, fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
                    tdwidth = ""
            else:
                fo += "<th class='ilbl %s ilbl-%s %s' %s title='$DESC'><label for='%s'>%s</label></th>" % (eo, fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
                tdwidth = ""
        else:
            fo = "<div class='ilbl %s ilbl-%s %s' %s title='$DESC'><label for='%s'>%s</label></div>" % (eo, fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
            tdwidth = ""
        # if we have a label/th, do not use the width for the field value also

    # --- print the saved data, different per input type:
    if (table == 1):
        fo += "<td "
    else:
        fo += "<div "
    fo += "class='ivar %s ivar-%s %s' %s title='$DESC'>" % (eo, fieldname_for_class, align, tdwidth)

    # text field
    if ("text" == type):
        # not in a loop:
        if (iter == 0):
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s %s' id='%s' name='%s' placeholder='%s' $ROWS $REQUIRED >{{variables.%s|default}}</textarea></div>" % (
                fieldname_for_class, mt, fieldname_for_form, fieldname_for_form, pholder, fieldname_for_form)
        # in a loop, add the loop counter to variable names:
        else:
            fo += "<div class='iContent'><textarea class='form-control ivar ivar-%s %s' id='%s' name='%s_{{id}}' placeholder='%s' $ROWS $REQUIRED >{{attribute(variables, '%s_' ~ id)|default}}</textarea></div>" % (
                fieldname_for_class, mt, fieldname_for_form, fieldname_for_form, pholder, fieldname_for_form)
        s = ""
        if (rows != ""):
            s = "rows='"+rows+"'"
        fo = fo.replace("$ROWS", s)

    # select field
    if ("select" == type):
        level += 1
        # not in a loop:
        if (iter == 0):
            fo += "\n"+"".ljust(level*tabsize)+"<select $REQUIRED class='form-control ivar ivar-%s' id='%s' name='%s'>\n" % (
                fieldname_for_class, fieldname_for_form, fieldname_for_form)
        # in a loop, add the loop counter to variable names:
        else:
            fo += "\n"+"".ljust(+level*tabsize)+"<select $REQUIRED class='form-control ivar ivar-%s' id='%s' name='%s_{{id}}'>\n" % (
                fieldname_for_class, fieldname_for_form, fieldname_for_form)

        x1 = len(options)
        i1 = 0
        while (i1 < x1):
            s1 = options[i1].strip().split(":")
            k1 = s1[0].strip().replace('"','').replace("'",'')
            v1 = ""
            if len(s1) > 1:
                v1 = s1[1].strip().replace('"','').replace("'",'')
            else:
                v1 = k1
                print("WARN: select options should be: %s: <value>. Assuming they are the same." % k1)
            if (v1 == ""):
                v1 = k1
                print("WARN: select option must not be empty: %s: <value>. Assuming they are the same." % k1)
            k1 = k1.lower().replace(' ','_').replace('-','_')
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

    # string field
    elif ("string" == type):
        # not in a loop:
        if (iter == 0):
            fo += "<input value='{{variables.%s|default}}' class='form-control ivar ivar-%s' id='%s' name='%s' placeholder='%s' type='text' $REQUIRED />" % (
                fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder)
        # in a loop, add the loop counter to variable names:
        else:
            fo += "<input value='{{attribute(variables, '%s_' ~ id)|default}}' class='form-control ivar ivar-%s' id='%s' name='%s_{{id}}' placeholder='%s' type='text' $REQUIRED />" % (
                fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder)

    # number field
    elif ("number" == type):
        # fo += "<div class='iContent'>"
        # not in a loop:
        if (iter == 0):
            fo += "<input value='{{variables.%s|default}}' class='form-control ivar ivar-%s c' id='%s' name='%s' placeholder='%s' type='number' $MIN $MAX $REQUIRED />" % (
                fieldname_for_form, fieldname_for_class, fieldname_for_form, fieldname_for_form, pholder)
        # in a loop, add the loop counter to variable names:
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

    # checkbox field
    elif ("checkbox" == type):
        # not in a loop:
        if (iter == 0):
            fo += "<input value='0' id='%s' name='%s' type='hidden' />" % (fieldname_for_form, fieldname_for_form)
            fo += "<input value='1' class='c' {% if variables.$ID|default > 0 %} checked='checked'{% endif %} id='$ID' name='$ID' type='checkbox' />"
        # in a loop, add the loop counter to variable names:
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
                    if (tr_open == 0):
                        fo += "</tr>"
                        # f_tableheader += "</tr>"
                        tr_open = 0
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


print("- Read schema.yml")
file = open('schema.yml', mode='r', encoding='utf-8-sig')
lines = file.readlines()
file.close()

print("- Open result files for writing")
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
print("- Recognized YAML indent size: %s" % itabsize)

# loop over all schema lines and parse them
x = len(lines)
lc = 0
while (lc < x):
    line = lines[lc]
    if (lc == 0):
        if (line.startswith('fields')):
            # we found the start of the actual yaml data
            print("- Parse YAML data")
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
            s = line.split(":", 1)
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
                tmp = "#"
                if (lc < x):
                    tmp = lines[lc+1]
            # got field and parameters, expand them
            fc += 1
            doField(field, params)

        # write the output to the sheet file
        if (len(sheet_output) > 0):
            for s in sheet_output:
                if (s.lstrip()!=""):
                    file_sheet.write(clean(s, level))

        # write the output to the form file
        if (len(form_output) > 0):
            for s in form_output:
                if (s.lstrip()!=""):
                    file_form.write(clean(s, level))

        level += clevel
    lc += 1
    if (quit > 0):
        lc=x

print("- Write yaml file for WA import")
file_yaml.write("fields:\n")
for s in yaml_output:
    if (s.lstrip()!=""):
        file_yaml.write(s+"\n")

# close files
file_sheet.close()
file_form.close()
file_yaml.close()

for field in ["col", "row", "card", "card-body", "iter", "sheet", "table"]:
    value = counters[field]
    if (value > 0):
        print("ERROR: # /"+field+" elements missing: %d" % value)
    if (value < 0):
        print("ERROR: superfluous # /"+field+" elements: %d" % abs(value))

print("- Finished, %d lines, %d fields, and %d formatting tags processed." % (lc, fc, tc))
# eof