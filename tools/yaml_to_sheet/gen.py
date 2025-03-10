#
# @name: yaml to sheet
# @version: 1.6
# @date: 2025-03-10
#

import re
import os
from datetime import date
today = date.today().strftime("%Y-%m-%d")

# VS Code (Windows) might not switch to the folder the script is in, depending on the user's settings and environment, so we need to do it ourselves
from sys import platform
if (platform == 'win32' or platform == 'cygwin'):
    os.chdir(os.path.dirname(__file__))

# Create a dictionary to hold all the variables
context = {
    "debug" : 0, # Set this to 1 to see some additional debug output
    "yaml_output": [],
    "sheet_output": [],
    "form_output": [],
    "level": 0,
    "clevel": 0,
    "tabsize": 2,
    "table": 0,
    "horiz": 0,
    "iterf": 1,
    "iter": 0,
    "iter_in_table": 0,
    "fc": 0,
    "lc": 0,
    "tc": 0,
    "eo": "",
    "mention": 0,
    "dots": 0,
    "split": 1,
    "s_tableheader": "",
    "f_tableheader": "",
    "s_table": "",
    "f_table": "",
    "width": "",
    "tr_open": 0,
    "quit": 0,
    "counters": {
        'col': 0,
        'row': 0,
        'card': 0,
        'card-body': 0,
        'iter': 0,
        'sheet': 0,
        'table': 0
    }
}

# -------------------------------------------------------------------------
def clean(line, level):
    """
    Cleans up the output line a bit
    Args:
        line (str): The input line.
        level (int): Indent level for the line.
    Returns:
        Formatted line.
    """
    global today
    line = "".ljust(level*context["tabsize"])+s.replace("TIMESTAMP", today)+"\n"

    # remove superfluous spaces
    line = line.replace("' >", "'>")
    line = line.replace(" '>", "'>")
    for _ in range(3):
        line = line.replace("  />", " />")
    return line


# -------------------------------------------------------------------------
def doLayout(line, context):
    """
    Cleans up the output line a bit
    Args:
        line (str): The input line.
        context (dict): A dictionary containing context information for processing the line.
    Returns:
        None, updates context, writes result to output files (sheet, form).
    """
    context["tc"] += 1
    line = line.strip().replace("# ", "", 1).strip()
    cmd = line.split(':', 3)
    cmd[0] = cmd[0].lower()

    if context["debug"] == 1:
        print(f"    DEBUG:" + "".ljust(+context["level"] * context["tabsize"]) + str(cmd))

    # linebreak (html)
    if cmd[0] == 'br':
        context["sheet_output"].append("<br class='linebreak'>")

    # card (bootstrap)
    elif cmd[0] == 'card':
        context["counters"]["card"] += 1
        s = ""
        if len(cmd) > 1:
            s = cmd[1].strip().lower()
        else:
            print(f"ERROR (line {context['lc']+1}): {cmd[0]} needs a class name as parameter")
        context["sheet_output"].append(f"<div class='card {s}' id='card-{s}'>")
        if len(cmd) == 3:
            context["sheet_output"].append("".ljust(context["tabsize"]) + f"<div class='card-header {cmd[1].strip().lower()}'>{cmd[2].strip().title()}</div>")
        context["clevel"] = 1
    elif cmd[0] == '/card':
        context["counters"]["card"] -= 1
        context["sheet_output"].append('</div>')
        context["level"] -= 1
        context["eo"] = ""

    # card-body (bootstrap)
    elif cmd[0] == 'card-body':
        if len(cmd) > 1:
            s = cmd[1].strip()
            if s == "mention":
                context["mention"] = 1
        context["counters"]["card-body"] += 1
        context["sheet_output"].append("<div class='card-body of'>")
        context["clevel"] = 1
    elif cmd[0] == '/card-body':
        context["mention"] = 0
        context["counters"]["card-body"] -= 1
        context["sheet_output"].append('</div>')
        context["level"] -= 1
        context["eo"] = ""

    # col (bootstrap)
    elif cmd[0] == 'col':
        context["counters"]["col"] += 1
        s = "col-12"
        if len(cmd) > 1:
            s = cmd[1].strip()
        else:
            print(f"WARN (line {context['lc']+1}): {cmd[0]} has no parameter, using {s} as default")
        context["sheet_output"].append(f"<div class='{s}'>")
        context["clevel"] = 1
    elif cmd[0] == '/col':
        context["counters"]["col"] -= 1
        context["sheet_output"].append('</div>')
        context["level"] -= 1
        context["eo"] = ""

    # dots (if you want 1 to x dots instead of a number shown)
    elif cmd[0] == 'dots':
        if len(cmd) > 1:
            context["dots"] = cmd[1].strip()

    # hr (separator line, html)
    elif cmd[0] == 'hr':
        context["sheet_output"].append("<hr class='separator'>")

    # include (include another file, this file is not processed)
    elif cmd[0] == 'include':
        try:
            ifile = open(cmd[1].strip(), mode='r', encoding='utf-8-sig')
            lines = ifile.readlines()
            ifile.close()
            if len(lines) > 0:
                for s in lines:
                    if s.strip() != "":
                        context["sheet_output"].append(s.rstrip())
                        context["form_output"].append(s.rstrip())
        except Exception as e:
            print(f"ERROR: cannot open include file {cmd[1]}: {e}")

    # iter (loop, script internal)
    elif cmd[0] == 'iter':
        context["counters"]["iter"] += 1
        context["iterf"] = 1
        context["iter"] = 10
        if len(cmd) > 1:
            context["iter"] = int(cmd[1].strip())
            if len(cmd) > 2:
                context["iterf"] = int(cmd[1].strip())
                context["iter"] = int(cmd[2].strip())
        else:
            print(f"WARN (line {context['lc']+1}): {cmd[0]} has no parameter, using 1 .. {context['iter']} as default")
        if context["table"] == 1 and context["horiz"] == 1:
            s1 = "{% " + f"for i in {context['iterf']}..{context['iter']}" + " %}###"
            s2 = "".ljust(context["tabsize"]) + "{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}{% if id < 100 %}{% set id = '0' ~ id %}{% endif %}###"
            context["s_table"] += s1
            context["s_table"] += s2
            context["f_table"] += s1
            context["f_table"] += s2
        else:
            context["sheet_output"].append("{% " + f"for i in {context['iterf']}..{context['iter']}" + " %}")
            context["sheet_output"].append("".ljust(context["tabsize"]) + "{% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}{% if id < 100 %}{% set id = '0' ~ id %}{% endif %}")
        if context["table"] == 1 and context["horiz"] == 1:
            s1 = "".ljust(context["tabsize"]) + "{% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}###<tr>###"
            context["s_table"] += s1
            context["f_table"] += s1
        else:
            context["sheet_output"].append("".ljust(context["tabsize"]) + "{% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}")
        context["clevel"] = 1
    elif cmd[0] == '/iter':
        context["counters"]["iter"] -= 1
        if context["table"] == 1:
            context["iter_in_table"] = 1
            if context["horiz"] == 1:
                context["s_table"] += "###</tr>###{% endfor %}###"
                context["f_table"] += "###</tr>###{% endfor %}###"
            else:
                context["sheet_output"].append("{% endfor %}")
        else:
            context["sheet_output"].append("{% endfor %}")
        context["iter"] = 0
        context["level"] -= 1
        context["eo"] = ""

    # row (bootstrap)    
    elif cmd[0] == 'row':
        context["counters"]["row"] += 1
        context["sheet_output"].append("<div class='row'>")
        context["clevel"] = 1
    elif cmd[0] == '/row':
        context["counters"]["row"] -= 1
        context["sheet_output"].append('</div>')
        context["level"] -= 1
        context["eo"] = ""

    # sheet (script internal)
    elif cmd[0] == 'sheet':
        context["counters"]["sheet"] += 1
        s = "sheetname"
        if len(cmd) > 1:
            s = cmd[1].strip().lower().replace(" ", "-")
        else:
            print(f"WARN (line {context['lc']+1}): {cmd[0]} has no parameter, using {s} as default")
        context["sheet_output"].append(f"<div class='container-fluid sheet-{s}'>")
        context["clevel"] = 1
    elif cmd[0] == '/sheet':
        context["counters"]["sheet"] -= 1
        context["sheet_output"].append('</div>')
        context["level"] -= 1
        context["quit"] = 1

    # table (html)
    elif cmd[0] == 'table':
        context["sheet_output"].append("<table class='table'>")
        context["form_output"].append("<table class='table'>")
        context["counters"]["table"] += 1
        context["eo"] = "ev"
        context["horiz"] = 0
        context["split"] = 1
        context["tr_open"] = 0
        context["s_tableheader"] = ""
        context["f_tableheader"] = ""
        context["s_table"] = "$TABLEHEADER"
        context["f_table"] = "$TABLEHEADER"
        if len(cmd) > 1:
            if cmd[1].strip() == "horiz":
                context["horiz"] = 1
                if len(cmd) > 2:
                    if cmd[2].strip() == "nosplit":
                        context["split"] = 0
        context["table"] = 1
        context["clevel"] = 1
    elif cmd[0] == '/table':
        context["counters"]["table"] -= 1
        tro_h = ""
        trc_h = ""
        if context["s_tableheader"] != "" and context["horiz"] == 1 and (context["iter_in_table"] == 1 or context["split"] == 1) and context["s_tableheader"].find("<tr>") == -1:
            tro_h = "<tr>"
            trc_h = "</tr>"
        if context["s_table"] != "":
            context["s_table"] = context["s_table"].replace("$TABLEHEADER", tro_h + "###" + context["s_tableheader"] + "###" + trc_h + "###")
            tmp = re.split('###', context["s_table"])
            for s in tmp:
                context["sheet_output"].append(s)
        if context["f_table"] != "":
            context["f_table"] = context["f_table"].replace("$TABLEHEADER", tro_h + "###" + context["f_tableheader"] + "###" + trc_h + "###")
            tmp = re.split('###', context["f_table"])
            for s in tmp:
                context["form_output"].append(s)
        if context["tr_open"] == 1:
            context["sheet_output"].append('</tr>')
            context["form_output"].append('</tr>')
        context["sheet_output"].append('</table>')
        context["form_output"].append('</table>')
        context["iter_in_table"] = 0
        context["horiz"] = 0
        context["split"] = 1
        context["tr_open"] = 0
        context["table"] = 0
        context["level"] -= 1
        context["eo"] = "ev"
    
    # width (script internal, for table column width)
    elif cmd[0] == 'width':
        if len(cmd) > 1:
            context["width"] = cmd[1].strip().lower().replace(" ", "")

    # unknown tag
    else:
        context["tc"] -= 1
        print(f"ERROR (line {context['lc']+1}): unknown element {cmd[0]}")


# -------------------------------------------------------------------------
def doField(field, params, context):
    """
    Processes a field and generates corresponding YAML, sheet, and form outputs.
    Args:
        field (str): The name of the field to process.
        params (list): A list of parameters associated with the field.
        context (dict): A dictionary containing context information for processing the field.
    Context Keys:
        mention (int): Indicates if the field should be a 'mention' field that displays the editor buttons.
        iterf (int): The starting iteration index.
        iter (int): The ending iteration index.
        tabsize (int): The size of indentation for YAML output.
        width (str): The width of the table column.
        table (int): Indicates if the output should be in table format.
        horiz (int): Indicates if the table should be horizontal.
        split (int): Indicates if the table should be split.
        tr_open (int): Indicates if a table row is open.
        eo (str): Even or odd row indicator.
        s_tableheader (str): The header for the sheet table.
        s_table (str): The sheet table content.
        sheet_output (list): The list to append sheet output.
        f_tableheader (str): The header for the form table.
        f_table (str): The form table content.
        form_output (list): The list to append form output.
        level (int): The current indentation level.
        dots (int): The number of dots for rendering.
    Returns:
        None, updates context
    """

    # limit yaml field names to a-zA-Z0-9-_ and convert to lower case
    fieldname_for_yaml = re.sub('[^a-zA-Z0-9\-\_ ]', '', field).replace("_", " ").replace("-", " ").lower()

    # limit form field names to a-z0-9, convert to lower case and concatenate words with -
    fieldname_for_class = fieldname_for_yaml.replace(" ", "-")

    # limit form field names to a-z0-9, convert to lower case and concatenate words with _
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

    if context["mention"] == 1:
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
        # form field parameters
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
        # wa image parameter: will render any number/string input as [img:xxx] in the presentation sheet
        if ("render" == k):
            render = v.replace('"', '')
        # makes any input field mandatory, preventing saving the form as long as the field is empty
        if ("required" == k):
            required = v.replace('"', '')
            if (required == "true"):
                required = "required=required"
            else:
                required = ''
        # input rows:text - number of rows
        if ("rows" == k):
            rows = v.replace('"', '')
        # text style: - this can be open/close tag like h1, h2, b
        if ("style" == k):
            style = re.sub('[\'"$%<>#]', '', v)
        # URL for image:
        if ("url" == k):
            url = v.replace('"', '')
        # width of image, html image parameter
        if ("width" == k):
            imgwidth = v.replace('"', '').replace("'", '')

    # ### create output ############################################################

    if ("image" == field):
        if (imgwidth != ""):
            imgwidth = "width='" + imgwidth + "'"
        s = "<img class='%s' src='%s' title='%s' %s>" % (fieldname_for_class, url, label, imgwidth)
        context["sheet_output"].append(s)
        context["form_output"].append(s)
        return
    if ("text" == field):
        if (style != ""):
            s = "<span class='%s'><%s>%s</%s></span>" % (fieldname_for_class, style, label, style)
        else:
            s = "<span class='%s'>%s</span>" % (fieldname_for_class, label)
        context["sheet_output"].append(s)
        context["form_output"].append(s)
        return

    # ### generate yaml for WA import #############################################

    postfix = ""
    x = int(context["iterf"])
    y = int(context["iter"])
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

        context["yaml_output"].append("".ljust(1*context["tabsize"])+fieldname_for_yaml+postfix+":")
        context["yaml_output"].append("".ljust(2*context["tabsize"])+'label: "'+fieldname_for_yaml+postfix+'"')
        context["yaml_output"].append("".ljust(2*context["tabsize"])+'input: '+type)

        if (desc != ""):
            context["yaml_output"].append("".ljust(2*context["tabsize"])+'description: "'+desc+'"')
        else:
            context["yaml_output"].append("".ljust(2*context["tabsize"])+'description: "'+label+'"')
        if (pholder != ""):
            context["yaml_output"].append("".ljust(2*context["tabsize"])+'placeholder: "'+pholder+'"')
        if (required == "required=required"):
            context["yaml_output"].append("".ljust(2*context["tabsize"])+'required: true')
        if (rows != ""):
            context["yaml_output"].append("".ljust(2*context["tabsize"])+'rows: '+rows)
        if (render != ""):
            context["yaml_output"].append("".ljust(2*context["tabsize"])+'render: '+render)
        if (min != ""):
            context["yaml_output"].append("".ljust(2*context["tabsize"])+'min: '+min)
        if (max != ""):
            context["yaml_output"].append("".ljust(2*context["tabsize"])+'max: '+max)
        if (options != []):
            context["yaml_output"].append("".ljust(2*context["tabsize"])+'options:')
            for s in options:
                context["yaml_output"].append("".ljust(3*context["tabsize"])+s.strip().replace("\n", ""))
        i += 1

    # --- basic for all ------------------------------------------------------------

    # always center checkboxes and numbers (css class '.c')
    align = ""
    if ("checkbox" == type or "number" == type):
        align = "c"

    # table column width gived, add it
    tdwidth = ""
    if (context["width"] != ""):
        tdwidth = "width='%s'" % (context["width"])

    # table <tr>
    # for debugging table formatting: print("table %s iter %s horiz %s split %s" % (table, iter, horiz) )
    if (context["table"] == 1):
        if (context["iter"] == 0):
            if (context["horiz"] == 0):
                so += "<tr>"
                fo += "<tr>"
            else:
                if (context["split"] == 1):
                    if (context["tr_open"] == 0):
                        so += "<tr>"
                        fo += "<tr>"
                        context["tr_open"] = 1
        else:
            if (context["horiz"] == 0):
                so += "<tr>"
                fo += "<tr>"

    if (context["iter"] > 0 or (context["table"] == 1 and context["horiz"] == 1)):
        context["eo"] = "{{eo}}"
    else:
        if context["eo"] == "od":
            context["eo"] = "ev"
        else:
            context["eo"] = "od"
    eo2 = context["eo"]

    # === basic sheet ==============================================================

    # --- print the label
    tdwith_orig=tdwidth
    if (label != ""):
        lalign = align
        if (context["iter"] == 0):
            lalign = ""
        if (context["table"] == 1):
            if (context["horiz"] == 1):
                if (context["split"] == 1):
                    eo2 = "od"
                    context["s_tableheader"] += "<th class='lbl %s lbl-%s %s' %s> %s </th>###" % (eo2, fieldname_for_class, lalign, tdwidth, label)
                else:
                    so += "<th class='lbl %s lbl-%s %s' %s title='$DESC'> %s </th>" % (context["eo"], fieldname_for_class, lalign, tdwidth, label)
            else:
                so += "<th class='lbl %s lbl-%s %s' %s title='$DESC'> %s </th>" % (context["eo"], fieldname_for_class, lalign, tdwidth, label)
        else:
            so += "<div class='lbl %s lbl-%s %s' %s title='$DESC'> %s </div>" % (context["eo"], fieldname_for_class, lalign, tdwidth, label)
        # if we have a label/th, do not use the width for the field value also
        tdwidth = ""

    # --- print the saved data, different per input type:
    if (context["table"] == 1):
        so += "<td "
    else:
        so += "<div "
    so += "class='var %s var-%s %s' %s title='$DESC'>" % (context["eo"], fieldname_for_class, align, tdwidth)

    if ("text" == type):
        if (context["iter"] == 0):
            so += " {{variables.%s|default|nl2br}} " % fieldname_for_form
        else:
            so += " {{attribute(variables, '%s_' ~ id)|default|nl2br}} " % fieldname_for_form

    if ("select" == type):
        if (context["iter"] == 0):
            so += " {{variables.%s|default}} " % fieldname_for_form
        else:
            so += " {{attribute(variables, '%s_' ~ id)|default}} " % fieldname_for_form

    elif ("checkbox" == type):
        if (context["iter"] == 0):
            so += "{% if variables.$ID|default == 1 %}<i class='fa-regular fa-square-check'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}"
        else:
            so += "{% if attribute(variables, '$ID_' ~ id)|default|default == 1 %}<i class='fa-regular fa-square-check'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}"
        so = so.replace("$ID", fieldname_for_form)

    elif ("string" == type):
        if (context["dots"] == 0):
            if (context["iter"] == 0):
                so += " {{variables.%s|default}} " % fieldname_for_form
            else:
                so += " {{attribute(variables, '%s_' ~ id)|default}} " % fieldname_for_form
        else:
            # make a line of boxes:
            if (context["iter"] == 0):
                so += "{% set curr = variables."+fieldname_for_form+"|default %}"
            else:
                so += "{% set curr = attribute(variables, '"+fieldname_for_form+"_' ~ id)|default %}"
            so += "{% for i in 1.."+context["dots"]+" %}{% if i <= curr %}<i class='fa-solid fa-square'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}{% endfor %}"
            context["dots"] = 0

    elif ("integer" == type or "number" == type):
        type = "number"
        if (context["dots"] == 0):
            prefix = ""
            postfix = ""
            # if it is an image, render it as such:
            if ("image" == render):
                prefix = "[img:"
                postfix = "]"
            if (context["iter"] == 0):
                so += prefix+("{{variables.%s|default}}" % fieldname_for_form)+postfix
            else:
                so += prefix+("{{attribute(variables, '%s_' ~ id)|default}}" % fieldname_for_form)+postfix
        else:
            # make a line of boxes:
            if (context["iter"] == 0):
                so += "{% set curr = variables."+fieldname_for_form+"|default %}"
            else:
                so += "{% set curr = attribute(variables, '"+fieldname_for_form+"_' ~ id)|default %}"
            so += "{% for i in 1.."+context["dots"]+" %}{% if i <= curr %}<i class='fa-solid fa-square'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}{% endfor %}"
            context["dots"] = 0

    # table
    if (context["table"] == 1):
        so += "</td>"
        if (context["iter"] == 0):
            if (context["horiz"] == 0):
                so += "</tr>"
            else:
                if (context["split"] == 1):
                    if (context["tr_open"] == 0):
                        so += "</tr>"
                        context["tr_open"] = 0
        else:
            if (context["horiz"] == 0):
                so += "</tr>"
    else:
        so += "</div>"

    # === edit form =============================================================

    tdwidth=tdwith_orig

    # --- print the label
    if (label != ""):
        lalign = align
        if (context["iter"] == 0):
            lalign = ""
        if (context["table"] == 1):
            if (context["horiz"] == 1):
                if (context["split"] == 1):
                    eo2 = "od"
                    context["f_tableheader"] += "<th class='ilbl %s ilbl-%s %s' %s><label for='%s'>%s</label></th>###" % (eo2, fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
                    tdwidth = ""
                else:
                    fo += "<th class='ilbl %s ilbl-%s %s %s' title='$DESC'><label for='%s'>%s</label></th>" % (context["eo"], fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
                    tdwidth = ""
            else:
                fo += "<th class='ilbl %s ilbl-%s %s' %s title='$DESC'><label for='%s'>%s</label></th>" % (context["eo"], fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
                tdwidth = ""
        else:
            fo = "<div class='ilbl %s ilbl-%s %s' %s title='$DESC'><label for='%s'>%s</label></div>" % (context["eo"], fieldname_for_class, lalign, tdwidth, fieldname_for_form, label)
            tdwidth = ""
        # if we have a label/th, do not use the width for the field value also

    # --- print the saved data, different per input type:
    if (context["table"] == 1):
        fo += "<td "
    else:
        fo += "<div "
    fo += "class='ivar %s ivar-%s %s' %s title='$DESC'>" % (context["eo"], fieldname_for_class, align, tdwidth)

    # text field
    if ("text" == type):
        # not in a loop:
        if (context["iter"] == 0):
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
        context["level"] += 1
        # not in a loop:
        if (context["iter"] == 0):
            fo += "\n"+"".ljust(context["level"]*context["tabsize"])+"<select $REQUIRED class='form-control ivar ivar-%s' id='%s' name='%s'>\n" % (
                fieldname_for_class, fieldname_for_form, fieldname_for_form)
        # in a loop, add the loop counter to variable names:
        else:
            fo += "\n"+"".ljust(+context["level"]*context["tabsize"])+"<select $REQUIRED class='form-control ivar ivar-%s' id='%s' name='%s_{{id}}'>\n" % (
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
            if (context["iter"] == 0):
                fo += "".ljust((context["level"]+1)*context["tabsize"])+"<option value='" + k1 + \
                    "' {% if variables."+fieldname_for_form+"|default == '" + k1 + \
                    "' %}selected='selected' {% endif %} > " + v1 + " </option>\n"
            else:
                fo += "".ljust((context["level"]+1)*context["tabsize"])+"<option value='" + k1 + \
                    "' {% if attribute(variables, '"+fieldname_for_form+"_' ~ id)|default == '" + k1 + \
                    "' %}selected='selected' {% endif %} > " + v1 + " </option>\n"
            i1 += 1
        fo += "".ljust(context["level"]*context["tabsize"])+"</select>"
        context["level"] -= 1

    # string field
    elif ("string" == type):
        # not in a loop:
        if (context["iter"] == 0):
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
        if (context["iter"] == 0):
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
        if (context["iter"] == 0):
            fo += "<input value='0' id='%s' name='%s' type='hidden' />" % (fieldname_for_form, fieldname_for_form)
            fo += "<input value='1' class='c' {% if variables.$ID|default > 0 %} checked='checked'{% endif %} id='$ID' name='$ID' type='checkbox' />"
        # in a loop, add the loop counter to variable names:
        else:
            fo += "<input value='0' id='%s' name='%s_{{id}}' type='hidden' />" % (fieldname_for_form, fieldname_for_form)
            fo += "<input value='1' class='c' {% if attribute(variables, '$ID_' ~ id)|default > 0 %} checked='checked'{% endif %} id='$ID' name='$ID_{{id}}' type='checkbox' />"
        fo = fo.replace("$ID", fieldname_for_form)

    # table
    if (context["table"] == 1):
        fo += "</td>"
        if (context["iter"] == 0):
            if (context["horiz"] == 0):
                fo += "</tr>"
            else:
                if (context["split"] == 1):
                    if (context["tr_open"] == 0):
                        fo += "</tr>"
                        # context["f_tableheader"] += "</tr>"
                        context["tr_open"] = 0
        else:
            if (context["horiz"] == 0):
                fo += "</tr>"
    else:
        fo += "</div>"

    # --- end form -----------------------------------------------------------------

    context["width"]=""
  
    # append output to sheet
    if (so != ""):
        # replace variables
        so = so.replace("$DESC", desc)
        # remove empty parameters
        so = so.replace(" title=''", "")

        if (context["table"] == 1 and context["horiz"] == 1):
            context["s_table"] += so
        else:
            context["sheet_output"].append(so)
    # append output to form
    if (fo != ""):
        # replace variables
        fo = fo.replace("$REQUIRED", required)
        fo = fo.replace("$DESC", desc)
        # remove empty parameters
        fo = fo.replace(" title=''", "")
        fo = fo.replace(" placeholder=''", "")

        if (context["table"] == 1 and context["horiz"] == 1):
            context["f_table"] += fo
        else:
            context["form_output"].append(fo)


# main() ------------------------------------------------------------------

fn_schema = "schema.yml"
fn_yaml = "import-to-wa.yml"
fn_sheet = "basic-sheet.html.twig"
fn_form = "edit-form.html.twig"

print(f"- Read schema yaml file {fn_schema}")
try:
    file = open(fn_schema, mode='r', encoding='utf-8-sig')
except Exception as e:
    print(f"ERROR: could not read {fn_schema}: {e}")
lines = file.readlines()
file.close()

try:
    file_yaml = open(fn_yaml, mode='w', encoding='utf-8-sig')
    file_sheet = open(fn_sheet, mode='w', encoding='utf-8-sig')
    file_form = open(fn_form, mode='w', encoding='utf-8-sig')
except Exception as e:
    print(f"ERROR: could not open one or more of the result files for writing: {e}")
    exit(1)

# get the indent size inside the yaml file
itabsize=2
x = len(lines)
context["lc"] = 0
while context["lc"] < x:
    line = lines[context["lc"]]
    if line.strip() != "" and not line.lower().startswith("fields:") and not line.lstrip().startswith("#"):
        itabsize = len(line) - len(line.lstrip())
        context["lc"] = x
    context["lc"] += 1
print(f"- Detected YAML indent size: {itabsize}")

# loop over all schema lines and parse them
x = len(lines)
context["lc"] = 0
while context["lc"] < x:
    line = lines[context["lc"]]
    if context["lc"] == 0:
        if line.startswith('fields'):
            # we found the start of the actual yaml data
            print("- Parse YAML data")
        else:
            print(f"ERROR (line {context['lc']+1}): file must start with fields: in the first line.")
            exit(0)
    elif line.strip() != "":
        # remember the current indentation level
        indent = len(line) - len(line.lstrip())
        line = line.strip()
        context["sheet_output"] = []
        context["form_output"] = []
        context["clevel"] = 0

        # all lines starting with # are for layout
        if (line.startswith('# ')):
            doLayout(line, context)
            # we want to use the layout for the form too
            if (len(context["sheet_output"]) > 0 and len(context["form_output"]) < 1):
                context["form_output"] = context["sheet_output"]
        elif (line.startswith('###!')):
            # special comment, this is being printed to stdout during the parsing process
            print(line)
        elif (not line.startswith('###')):
            # parse everything else
            s = line.split(":", 1)
            field = s[0]
            # looking for a key: line
            if (len(s) > 1 and s[1] != ""):
                print(f"ERROR (line {context['lc']+1}): field '{field}' has more than one parameter, it should not.")
            # looking for indented key:value parameter lines, reading them all into a list
            z = (indent-1)*2
            params = []
            tmp = lines[context["lc"]+1]
            while (tmp[:z+itabsize].isspace() and not tmp.lstrip().startswith("#")):
                params.append(tmp)
                context["lc"] += 1
                tmp = "#"
                if (context["lc"] < x):
                    tmp = lines[context["lc"]+1]
            # got field and parameters, expand them
            context["fc"] += 1
            doField(field, params, context)

        # write the output to the sheet file
        if (len(context["sheet_output"]) > 0):
            for s in context["sheet_output"]:
                if (s.lstrip()!=""):
                    file_sheet.write(clean(s, context["level"]))

        # write the output to the form file
        if (len(context["form_output"]) > 0):
            for s in context["form_output"]:
                if (s.lstrip()!=""):
                    file_form.write(clean(s, context["level"]))

        context["level"] += context["clevel"]
    context["lc"] += 1
    if (context["quit"] > 0):
        context["lc"]=x

# close files
print("- Write result files")
file_sheet.close()
file_form.close()

file_yaml.write("fields:\n")
for s in context["yaml_output"]:
    if (s.lstrip()!=""):
        file_yaml.write(s+"\n")
file_yaml.close()

for field in ["col", "row", "card", "card-body", "iter", "sheet", "table"]:
    value = context["counters"][field]
    if value > 0:
        print(f"ERROR: # /{field} elements missing: {value}")
    elif value < 0:
        print(f"ERROR: superfluous # /{field} elements: {abs(value)}")

print(f"- Finished, {context['lc']} lines, {context['fc']} fields, and {context['tc']} formatting tags processed")
print(f"\n- Upload these files to WA: {fn_yaml}, {fn_sheet}, {fn_form}")

# eof