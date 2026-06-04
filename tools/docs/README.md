# Curated Surface Evolver docs

Place selected Surface Evolver plain-text documentation pages here to make them
available to the `get_evolver_doc` tool during generation. The tool returns one
curated page by topic.

The tool recognizes these page filenames:

- `datafile.md` or `datafile.txt`
- `syntax.md` or `syntax.txt`
- `elements.md` or `elements.txt`
- `commands.md` or `commands.txt`
- `single.md` or `single.txt`
- `toggle.md` or `toggle.txt`
- `constraints.md` or `constraints.txt`
- `quantities.md` or `quantities.txt`
- `energies.md` or `energies.txt`

You can convert selected pages from an Evolver HTML documentation directory:

```bash
python tools/convert_evolver_docs.py /path/to/Evolver270-OSX/doc --topic datafile --topic syntax
```

The converter strips links and omits obvious examples/long samples by default,
while keeping short formal syntax blocks. Pass `--keep-examples` if a curated
page should retain examples.
