# Emenus
or simply, eek menus

emenus are a collection of [discord ext menus]() that I find could be 
very useful across bots, and simply installing a module that contains 
all of them is far easier than having to find the file, copy-paste the
classes, implement them, etc etc.

---

### Installing:
This can be done through git:
```shell script
$ pip install git+https://github.com/EEKIM10/emenus.git
```

Or from [PyPi](https://pypi.org/project/eekues):
```shell script
python -m pip install eekues>=0.1
```
(or your system equivalent)

### Using
#### case 1:
```python
import eekues as menus

@bot.command(name="delete?")
async def delete(ctx):
    yes = await menus.Confirm().result(ctx)
    if yes:
        return await ctx.send("Deleted stuff")
    else:
        return await ctx.send("Didn't do anything.")
```
#### case 2:
```python
from eekues import Confirm as C

@bot.command()
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):
    if await C().result(ctx):
        await member.ban()
```