# Sound generator
*A tool to create Minecraft sounds mappings*


This was a side project needed for the development of [Conduit](https://github.com/1attila/Conduit).

It offers a set of classes that can be accesses to refers to Minecraft sounds.

This was done mainly to enable tab-completion and reduce typos, making [conduit plugin development](https://github.com/1attila/Conduit/wiki/Plugin-Development) faster.


## How to use

If you want to use this package, download the repo and import sounds in your project.

Then you can start typing the sound identifier starting from sounds.

### Modifications
Some sound names are prefixed/suffixed by `_`.

This only if the name starts with:
- **python keyword** (e.g: `block.amethyst_block.break` -> `block.amethyst_block.break_`)
- **number** (e.g: `item.goat_horn.sound.0` -> `item.goat_horn.sound._0`)

### Get version-specific mappings
- Select the right branch for the version you need (there is none rn)
- Download/clone that specific branch

### Create new mappings for new versions
- Download/clone the repo
- Deobfuscate Minecraft source code [from this tutorial](https://www.youtube.com/watch?v=7NuaLAG3fnc)
- Run the program (parameters are listed below)

**Tweakable parameters**:

| parameter | alias | default |
| --------- | ----- | ------- |
| `-version`  | `-v `   | `1.21.10` |
| `-input`    | `-i`    | `SoundEvents.java` |
| `-output`   | `-o`    | `sounds`  |