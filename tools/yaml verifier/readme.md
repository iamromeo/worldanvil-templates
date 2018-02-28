This tool will check if a specified yaml file adheres to the requirements of this project.
To use this tool, you will need to have python installed along with pykwalify.
If you are on a *nix system, run 
	verify.sh [YAML FILE]
As an example, 
	./verify.sh pathfinder/feat.yml
If you have any errors, it will list what it was and where it occurred.

Example output:
```
allen@SixteenColorServer:/media/Data2/programming/worldanvil-templates/tools/yaml verifier$ ./verify.sh genesys/achetype.yml
 ERROR - validation.invalid
 ERROR -  --- All found errors ---
 ERROR - [u"Cannot find required key 'display_template'. Path: ''", u"Cannot find required key 'instructions'. Path: ''"]
Traceback (most recent call last):
  File "/usr/local/bin/pykwalify", line 11, in <module>
    sys.exit(cli_entrypoint())
  File "/usr/local/lib/python2.7/dist-packages/pykwalify/cli.py", line 95, in cli_entrypoint
    run(parse_cli())
  File "/usr/local/lib/python2.7/dist-packages/pykwalify/cli.py", line 82, in run
    c.validate()
  File "/usr/local/lib/python2.7/dist-packages/pykwalify/core.py", line 176, in validate
    error_msg=u'.\n - '.join(self.validation_errors)))
pykwalify.errors.SchemaError: <SchemaError: error code 2: Schema validation failed:
 - Cannot find required key 'display_template'. Path: ''.
 - Cannot find required key 'instructions'. Path: ''.: Path: '/'>
```