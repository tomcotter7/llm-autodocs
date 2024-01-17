# auto-docs

run `generate_docs.bat/sh` to build the docstring for `democode` - you will need to add your openai api key to `.env.template` and rename it to `.env` for this to work.

See example system design below:

![system design](./imgs/system-design.png)

## Roadmap

    - [X] Python functions
    - [ ] Aliased python functions
    - [ ] Python classes
    - [ ] Module level docstring
    - [ ] Package level docstring
    - [ ] Custom pydeps parser using ast
    - [ ] Alternate language functions (probably godoc)
