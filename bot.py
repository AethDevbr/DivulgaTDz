import os
import discord
from discord.ext import commands
import json

with open("config.json") as f:
    config = json.load(f)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

def ticket_permissions(guild, user):
    return {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True)
    }

class ConfirmView(discord.ui.View):
    def __init__(self, user, produto, valor):
        super().__init__(timeout=None)
        self.user = user
        self.produto = produto
        self.valor = valor

    @discord.ui.button(label="✅ Confirmar Pagamento", style=discord.ButtonStyle.green)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        vip_role = discord.utils.get(interaction.guild.roles, name=config["vip_role"])
        if vip_role:
            await self.user.add_roles(vip_role)

        await interaction.response.send_message("💎 Pagamento confirmado! VIP entregue.", ephemeral=True)

        log = discord.utils.get(interaction.guild.text_channels, name=config["log_channel"])
        if log:
            await log.send(f"✅ {self.user.mention} comprou {self.produto}")

        publico = discord.utils.get(interaction.guild.text_channels, name=config["public_channel"])
        if publico:
            embed = discord.Embed(
                title="🛒 COMPRA REALIZADA COM SUCESSO",
                description=f"👤 **Cliente:** {self.user.mention}\n📦 **Produto:** {self.produto}\n💰 **Valor:** {self.valor}",
                color=0x00ff88
            )
            embed.set_thumbnail(url=self.user.display_avatar.url)
            embed.set_footer(text="Obrigado por comprar na TDZ Divulgações 🚀")
            await publico.send(embed=embed)

    @discord.ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.red)
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

class VendaSelect(discord.ui.Select):
    def __init__(self):
        self.planos = {
            "⭐ VIP Básico": "R$15",
            "🔥 VIP Intermediário": "R$30",
            "💎 VIP Premium": "R$50"
        }

        options = [
            discord.SelectOption(label=k, description=v) for k,v in self.planos.items()
        ]

        super().__init__(placeholder="Escolha um plano...", options=options)

    async def callback(self, interaction: discord.Interaction):
        produto = self.values[0]
        valor = self.planos[produto]

        categoria = discord.utils.get(interaction.guild.categories, name=config["ticket_category"])

        canal = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=ticket_permissions(interaction.guild, interaction.user),
            category=categoria
        )

        embed = discord.Embed(
            title="🛒 Compra iniciada",
            description=f"📦 **Plano:** {produto}\n💰 **Valor:** {valor}",
            color=0x00ff88
        )

        embed.add_field(name="💳 Pagamento via PIX", value=config["pix"])
        embed.set_footer(text="Envie o comprovante e aguarde a staff")

        await canal.send(interaction.user.mention, embed=embed, view=ConfirmView(interaction.user, produto, valor))

        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)

class VendaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VendaSelect())

@bot.tree.command(name="painel", description="Enviar painel de vendas")
async def painel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="💎 Painel VIP TDZ",
        description="Selecione um plano abaixo",
        color=0x00ff88
    )
    await interaction.response.send_message(embed=embed, view=VendaView())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot online")

bot.run(os.getenv("DISCORD_TOKEN")) 
