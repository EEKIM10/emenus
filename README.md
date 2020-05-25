# Emenus
or simply, eek menus

emenus are a collection of [discord ext menus]() that I find could be 
very useful across bots, and simply installing a module that contains 
all of them is far easier than having to find the file, copy-paste the
classes, implement them, etc etc.

---

### Installing:
This can only be done through git, at the moment:
```shell script
$ pip install git+https://github.com/EEKIM10/emenus.git
```
(or your system equivalent)

### Using
#### case 1:
```python
import emenus as menus

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
from emenus import Confirm as C

@bot.command()
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):
    if await C.result(ctx):
        await member.ban()
```