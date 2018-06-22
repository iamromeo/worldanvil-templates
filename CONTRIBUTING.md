# Contribution Guidelines
## Code of Conduct
By contributing to World Anvil public repositories you accept to conform to the [**Code of conduct**](./CODE_OF_CONDUCT.md)  

## Coding Conventions 
For better understanding of the history of the repository and to maintained readability a few naming template and conventions :
- Pull requests and Commit Message **MUST** start with [$system]   
(ie: [dnd35e] Adding stuff)
- Commit message **SHOULD** contain add, mod, del sections specifying impacted files.  
ie : 
```md
    ## ADD :
    - Schema/dnd35e/items.yml : adding a new data model
    ## MOD :
    - Display/dnd35e/items.html.twig : added support for living constructs

```
- yml value should be lowercase + eventually underscores for precision  
ie :
```YAML
faith:
speed_walking:
speed_flying:
```

_//-- probably others will come --//_

