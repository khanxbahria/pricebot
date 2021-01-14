import os
import datetime
import csv
from random import randint

import discord
from discord.ext import commands

from selfbot import SelfBot
from settings import Settings
import save_prices

settings = Settings()

bot = commands.Bot(command_prefix='>')
bot.remove_command('help')

selfbot = SelfBot()

def item_from_csv(item, sort_by='time', limit=settings.results_limit):
    found_rows = []
    color = randint(0, 0xffffff)
    with open('prices.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if item.lower() in row['item'].lower():
                row['seller_icon'] = f"https://cdn.discordapp.com/avatars/{row['seller_avipart']}.png?size=512"
                for server in settings.servers:
                    for channel_name, channel_id in server['channels'].items():
                        if row['channel_id'] == channel_id:
                            break
                    if row['channel_id'] == channel_id:
                        break
                row['channel_name'] = channel_name
                row['server_name'] = server['name']
                row['server_id'] = server['id']

                row['server_icon'] = f'https://cdn.discordapp.com/icons/{server["id"]}/{server["icon_file"]}.png?size=512'
                row['query'] = item.title()
                row['timestamp'] = datetime.datetime.strptime(row['time'], "%Y-%m-%dT%H:%M:%S")
                row['price'] = float(row['price'])
                row['color'] = color

                if "coin" in item.lower() and row['price'] < 10:
                    continue

                found_rows.append(row)

    if sort_by!='time':
        found_rows = sorted(found_rows, key=lambda k: k[sort_by])
    if len(found_rows) > limit:
        found_rows = found_rows[:limit]

    return found_rows



def create_item_embed(record):
    url = f"https://discord.com/channels/{record['server_id']}/{record['channel_id']}/{record['msg_id']}"
    title = f"{record['query']} - ${record['price']}"
    embed = discord.Embed(title=title, description=record['item'] + "\n\n" + url, color=record['color'], timestamp=record['timestamp'])
    embed.set_author(name=record['seller_tag'], icon_url=record['seller_icon'])
    embed.set_thumbnail(url=record['seller_icon'])
    embed.set_footer(text=f"{record['server_name']} | {record['channel_name']}", icon_url=record['server_icon'])

    return embed

def add_credits(embed):
    embed.set_author(name="PriceBot", url="https://github.com/khanxbahria/pricebot", icon_url="https://cdn.discordapp.com/avatars/773941765282725949/4c6d3b1e0182b4b71e7509a60d64357e.png?size=512")
    embed.set_footer(text="khanxbahria", icon_url="https://cdn.discordapp.com/avatars/593752934496337920/c9c19309250e4ac4d4c94817d4fef867.png?size=128")



def create_shop_embed(server_name, server_icon, channel_name, channel_id):
    embed = discord.Embed(title=channel_name, description=f"{server_name}\n{channel_id}")
    embed.set_thumbnail(url=server_icon)
    add_credits(embed)
    return embed

def create_msg_embed(msg):
    embed = discord.Embed(title=msg)
    add_credits(embed)
    return embed

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="$$$"))
    print(f"{bot.user} has connected to Discord.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Help", colour=discord.Colour(0x2dc42d), description="PriceBot will find any item being sold for USD across different USD channels in discord, so you don't have to scroll up on channels trying to look for a certain item.\n\nUse these commands to query item prices")
    embed.add_field(inline=False, name="```>find [max_results:Optional] <item>```", value=f"```Displays top <max_results> messages containing <item> sorted by recent first order.\nDefault value of max_results: {settings.results_limit}\nAlias: f\n\n>find 5 demons\n>find coins\n>f 15 vamp\n```")
    embed.add_field(inline=False, name="```>findcheap [max_results:Optional] <item>```", value="```\nDisplays top <max_results> messages containing <item> sorted by lowest price first order.\nAlias: fc\n\n>findcheap 5 demons\n>findcheap coins\n>fc 15 vt\n```")
    embed.add_field(inline=False, name="```>update```", value="```\nScrapes the channels to update the prices.\n```")
    embed.add_field(inline=False, name="```>listshops```", value="```\nLists the shop channels to be scraped.\nAlias: ls\n```")
    embed.add_field(inline=False, name="```>addshop```", value="```\nAdd shop.\nAlias: as\nAdmin command```")
    embed.add_field(inline=False, name="```>deleteshop```", value="```\nDelete shop.\nAlias: ds\nAdmin command```")


    add_credits(embed)
    await ctx.send(embed=embed)

@bot.command(name='update', aliases=['u'])
async def update_prices(ctx):
    save_prices.main()
    await ctx.send(embed=create_msg_embed('Prices updated!'))

@bot.command(name='find', aliases=['f'], desc='')
async def find_item(ctx,*args):
    try:
        limit = int(args[0])
    except ValueError:
        limit = settings.results_limit
        item = " ".join(args)
    else:
        item = " ".join(args[1:])

    item_dicts = item_from_csv(item,limit=limit)
    for item_dict in item_dicts:
        await ctx.send(embed=create_item_embed(item_dict))

@bot.command(name='findcheap', aliases=['fc'])
async def find_cheap(ctx,*args):
    try:
        limit = int(args[0])
    except ValueError:
        limit = settings.results_limit
        item = " ".join(args)
    else:
        item = " ".join(args[1:])

    item_dicts = item_from_csv(item,sort_by='price',limit=limit)
    for item_dict in item_dicts:
        await ctx.send(embed=create_item_embed(item_dict))

@bot.command(name='addshop', aliases=['as'])
async def add_channel(ctx, channel_name, channel_id, *, server_name):
    if ctx.author.id == 593752934496337920 or ctx.author.guild_permissions.administrator:
        try:
            settings.add_channel(server_name, channel_name, channel_id)
        except Exception as e:
            print(e)
            await ctx.send(embed=create_msg_embed("Error occured!"))
        else:
            await ctx.send(embed=create_msg_embed("Shop added."))
    else:
        await ctx.send(embed=create_msg_embed("Permission denied."))

@bot.command(name='deleteshop', aliases=['ds'])
async def delete_channel(ctx, channel_id):
    if ctx.author.id == 593752934496337920 or ctx.author.guild_permissions.administrator:
        try:
            channel = settings.delete_channel(channel_id)
        except Exception as e:
            print(e)
            await ctx.send(embed=create_msg_embed("Error occured!"))
        else:
            await ctx.send(embed=create_msg_embed(f"Shop - {channel} deleted."))
    else:
        await ctx.send(embed=create_msg_embed("Permission denied."))


@bot.command(name='listshops', aliases=['ls'])
async def list_channels(ctx):
    for server in settings.servers:
        for channel_name, channel_id in server['channels'].items():
            server_icon = f'https://cdn.discordapp.com/icons/{server["id"]}/{server["icon_file"]}.png?size=512'
            embed = create_shop_embed(server['name'], server_icon, channel_name, channel_id)
            await ctx.send(embed=embed)




bot.run(settings.bottoken)
