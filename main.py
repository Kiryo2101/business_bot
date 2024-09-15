import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput, Select, View

from myserver import server_on

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "File not found."

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        await bot.tree.sync()
        print(f'We have logged in as {bot.user}')
    except Exception as e:
        print(f"Error syncing commands: {e}")
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="You <3"))

@bot.tree.command(name="ping", description="Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"ปั้งหัวพ่อมึง, {interaction.user.mention}!")

@bot.tree.command(name="list_name_business_class", description="รายชื่อห้องอังกฤษธุรกิจ")
async def list_name_business_class(interaction: discord.Interaction):
    file_content = read_file('List Name.txt')
    embed = discord.Embed(
        title="รายชื่อ ม.4/5 วชิรธรรมสาธิตทั้งหมด",
        description=f"```{file_content}```",
        color=discord.Color.red()  # Embed color
    )
    embed.set_footer(text="Bot made by @itbigzwtf")
    embed.set_thumbnail(url="https://media.tenor.com/Rp0U7bdOhSUAAAAi/anime.gif")

    await interaction.response.send_message(embed=embed)

class FeedbackModal(discord.ui.Modal, title="ส่งข้อความไปใน DM"):
    def __init__(self, recipient: discord.User):
        super().__init__(title="ส่งข้อความไปใน DM")
        self.recipient = recipient
        self.message_input = discord.ui.TextInput(
            style=discord.TextStyle.long,
            label="Message",
            required=True,
            max_length=500,
            placeholder="กรอกข้อความ"
        )
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        await self.recipient.send(f"มีคนฝากบอกว่า: {self.message_input.value}")
        await interaction.response.send_message(f"ส่ง '{self.message_input.value}' ไปหา <@{self.recipient.id}>", ephemeral=True)
        
class MemberSelect(Select):
    def __init__(self, guild: discord.Guild):
        options = [discord.SelectOption(label=member.name, value=str(member.id)) for member in guild.members if not member.bot]
        super().__init__(placeholder="Select a member...", min_values=1, max_values=1, options=options)
        self.guild = guild

    async def callback(self, interaction: discord.Interaction):
        member_id = int(self.values[0])
        member = discord.utils.get(self.guild.members, id=member_id)
        if member:
            feedback_modal = FeedbackModal(recipient=member)
            await interaction.response.send_modal(feedback_modal)
        else:
            await interaction.response.send_message("Member not found.", ephemeral=True)

class MemberSelectView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.add_item(MemberSelect(guild=guild))

@bot.tree.command(name="send_dm", description="ส่งข้อความไปใน DM ไม่ระบุชื่อ")
async def send_dm(interaction: discord.Interaction):
    guild = interaction.guild
    if guild:
        view = MemberSelectView(guild=guild)
        await interaction.response.send_message("เลือกคนในเซิฟเวอร์ที่จะส่งไป:", view=view, ephemeral=True)
    else:
        await interaction.response.send_message("Guild not found.", ephemeral=True)

server_on()

bot.run(os.getenv('Token'))