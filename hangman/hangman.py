import discord
from redbot.core.data_manager import bundled_data_path
from redbot.core.data_manager import cog_data_path
from redbot.core import commands
from redbot.core import Config
from redbot.core import checks
from random import randint
import os

class Hangman(commands.Cog):
	"""Play hangman with the bot."""
	def __init__(self, bot):
		self.bot = bot
		self.config = Config.get_conf(self, identifier=7345167902)
		self.config.register_guild(
			fp = str(bundled_data_path(self) / 'words.txt'),
			doEdit = True
		)
		self.man = ['\
    ___    \n\
   |   |   \n\
   |   O   \n\
   |       \n\
   |       \n\
   |       \n\
   |       \n\
  ','\
    ___    \n\
   |   |   \n\
   |   O   \n\
   |   |   \n\
   |   |   \n\
   |       \n\
   |       \n\
  ','\
    ___    \n\
   |   |   \n\
   |   O   \n\
   |  \|   \n\
   |   |   \n\
   |       \n\
   |       \n\
  ','\
    ___    \n\
   |   |   \n\
   |   O   \n\
   |  \|/  \n\
   |   |   \n\
   |       \n\
   |       \n\
   ','\
    ___    \n\
   |   |   \n\
   |   O   \n\
   |  \|/  \n\
   |   |   \n\
   |  /    \n\
   |       \n\
   ','\
    ___    \n\
   |   |   \n\
   |   O   \n\
   |  \|/  \n\
   |   |   \n\
   |  / \  \n\
   |       \n\
   ','\
    ___    \n\
   |   |   \n\
   |   X   \n\
   |  \|/  \n\
   |   |   \n\
   |  / \  \n\
   |       \n\
   ']

	@commands.command()
	async def hangman(self, ctx):
		"""Play hangman with the bot."""
		if ctx.guild == None: #default vars in pms
			fp = str(bundled_data_path(self) / 'words.txt')
			doEdit = False #cant delete messages in pms
		else: #server specific vars
			fp = await self.config.guild(ctx.guild).fp()
			doEdit = await self.config.guild(ctx.guild).doEdit()
		x = open(fp)
		wordlist = []
		for line in x:
			wordlist.append(line.strip().lower())
		word = wordlist[randint(0,len(wordlist))] #pick and format random word
		guessed = ''
		fails = 0
		end = 0
		err = 0
		boardmsg = None
		while end == 0:
			p = ''
			for l in word:
				if l not in 'abcdefghijklmnopqrstuvwxyz': #auto print non letter characters
					p += l+' '
				elif l in guessed: #print already guessed characters
					p += l+' '
				else:
					p += '_ ' 
			p += '    ('
			for l in guessed:
				if l not in word:
					p += l
			p += ')'
			p = '```'+self.man[fails]+'\n'+p+'```'
			if err == 1:
				p += 'You already guessed that letter.\n'
			elif err == 2:
				p += 'Pick a letter.\n'
			check = lambda m: m.channel == ctx.message.channel and m.author == ctx.message.author
			if boardmsg == None or doEdit == False:
				boardmsg = await ctx.send(p+'Guess:')
			else:
				await boardmsg.edit(content=str(p+'Guess:'))
			try:
				umsg = await self.bot.wait_for('message', check=check, timeout=60)
			except:
				return await ctx.send('Canceling selection. You took too long.\nThe word was '+word+'.')
			t = umsg.content[0].lower()
			if doEdit:
				await umsg.delete()
			if t in guessed:
				err = 1
			elif t not in 'abcdefghijklmnopqrstuvwxyz':
				err = 2
			else:
				err = 0
				if t not in word:
					fails += 1
					if fails == 6: #too many fails
						if doEdit:
							await boardmsg.edit(content=str('```'+self.man[6]+'```Game Over\nThe word was '+word+'.'))
						else:
							await ctx.send(str('```'+self.man[6]+'```Game Over\nThe word was '+word+'.'))
						end = 1
				guessed += t
				if word.strip(guessed) == word.strip('abcdefghijklmnopqrstuvwxyz'): #guessed entire word
					if doEdit:
						await boardmsg.edit(content=str('```'+self.man[fails]+'```You win!\nThe word was '+word+'.'))
					else:
						await ctx.send(str('```'+self.man[fails]+'```You win!\nThe word was '+word+'.'))
					end = 1
	
	@commands.guild_only()
	@checks.guildowner()
	@commands.group()
	async def hangmanset(self, ctx):
		"""Config options for hangman."""
		pass
	
	@commands.guild_only()
	@checks.guildowner()
	@hangmanset.command(name='wordlist')
	async def wordlist(self, ctx, value: str=None):
		"""
		Change the wordlist used.
		Extra wordlists can be put in the data folder of this cog.
		Wordlists are a text file with every new line being a new word.
		Use default to restore the default wordlist.
		Use list to list available wordlists.
		This value is server specific.
		"""
		if value == None:
			v = await self.config.guild(ctx.guild).fp()
			if str(v) == str(bundled_data_path(self) / 'words.txt'):
				await ctx.send('The wordlist is set to the default list.')
			else:
				await ctx.send('The wordlist is set to `'+v[::-1].split('\\')[0][::-1][:-4]+'`.')
		elif value.lower() == 'default':
			set = str(bundled_data_path(self) / 'words.txt')
			await self.config.guild(ctx.guild).fp.set(set)
			await ctx.send('The wordlist is now the default list.')
		else:
			y = []
			for x in os.listdir(cog_data_path(self)):
				if x[-4:] == '.txt':
					y.append(x[:-4])
			if y == []:
				await ctx.send('You do not have any wordlists.')
			elif value.lower() == 'list':
				z = ''
				for x in y:
					z += x+'\n'
				await ctx.send('Available wordlists:\n`'+z+'`')
			else:
				if value in y:
					set = str(cog_data_path(self) / str(value+'.txt'))
					await self.config.guild(ctx.guild).fp.set(set)
					await ctx.send('The wordlist is now set to `'+value+'`.')
				else:
					await ctx.send('Wordlist not found.')
	
	@commands.guild_only()
	@checks.guildowner()
	@hangmanset.command(name='edit')
	async def edit(self, ctx, value: bool=None):
		"""
		Set if hangman messages should be one edited message or many individual messages.
		Defaults to True.
		This value is server specific.
		"""
		if value == None:
			v = await self.config.guild(ctx.guild).doEdit()
			if v:
				await ctx.send('Games are currently being played on a single, edited message.')
			else:
				await ctx.send('Games are currently being played on multiple messages.')
		else:
			await self.config.guild(ctx.guild).doEdit.set(value)
			if value:
				await ctx.send('Games will now be played on a single, edited message.')
			else:
				await ctx.send('Games will now be played on multiple messages.')
