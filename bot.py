"""
========================================
TDZ DIVULGAÇÕES - BOT COMPLETO
========================================
Bot de divulgação com sistema de vendas VIP
Slash Commands | Python 3.11.9 | discord.py 2.5.2
========================================
"""

import discord
from discord import app_commands, ui
from discord.ext import commands
import json
import os
import datetime
import asyncio
from typing import Optional
import random

# ========================================
# CONFIGURAÇÕES DO SERVIDOR
# ========================================

CONFIG = {
    # IDs
    "GUILD_ID": 1465866618578932055,
    "DONO_ID": 1327679436128129159,  # Apenas você pode confirmar
    
    # Cargos
    "CARGO_DONO": "Dono 👑",
    "CARGO_MOD": "Mod",
    "CARGO_VIP": "ᴅɪᴠᴜʟɢᴀᴅᴏʀ ᴠɪᴘ 💎",  # Cargo exato com fonte
    
    # Categorias
    "CATEGORIA_TICKETS": "🛒 Compras",
    
    # Canais (nomes exatos que você mandou)
    "CANAL_REGRAS": "📕・regras",
    "CANAL_ANUNCIOS": "📢・ANUNCIOS",
    "CANAL_NOVIDADES": "🎉・NOVIDADES",
    "CANAL_INFO": "ℹ️・INFORMACOES",
    "CANAL_ENTRADA": "✈️・--ENTRADA",
    "CANAL_SAIDA": "👋・--SAIDA",
    "CANAL_CHAT": "💬・CHAT-GERAL",
    "CANAL_GAMING": "🎮・GAMING",
    "CANAL_MUSICA": "🎵・MUSICA",
    "CANAL_MIDIAS": "🖼️・MIDIAS",
    "CANAL_COMANDOS": "🤖・COMANDOS-BOT",
    "CANAL_TICKETS": "🎫・TICKETS",
    "CANAL_AJUDA": "❓・AJUDA",
    "CANAL_SUGESTOES": "💡・SUGESTOES",
    "CANAL_SOCIAIS": "📱・MIDIAS-SOCIAIS",
    "CANAL_SERVIDORES": "💬・SERVIDORES-DISCORD",
    "CANAL_YOUTUBE": "📹・CANAIS-YOUTUBE",
    "CANAL_TWITCH": "🎬・LIVES-TWITCH",
    "CANAL_ARTES": "🖼️・ARTES-DIGITAIS",
    "CANAL_SERVICOS": "🛠️・SERVICOS-OFERTAS",
    "CANAL_FEEDBACK": "🌟-Feedback",
    
    # Pagamento
    "PIX_CHAVE": "999049883",
    "EMOJI_PIX": "<:emoji_2:1486128219504513066>",
    
    # Preços
    "PRECOS": {
        "destacar_mensagem": 15,
        "vip": 30,              # VIP único
        "divulgacao_global": 20
    },
    
    # Imagens
    "IMAGENS": {
        "regras": "https://i.imgur.com/Vq8OfY5.png",
        "info": "https://i.imgur.com/JOy0zXZ.png",
        "anuncio": "https://i.imgur.com/DbgjpnR.png",
        "vip": "https://i.imgur.com/ryeKviZ.png",
        "shop": "https://i.imgur.com/ryeKviZ.png",
        "giveaway": "https://i.imgur.com/DbgjpnR.png",
        "welcome": "https://i.imgur.com/DbgjpnR.png"
    }
}

# ========================================
# BANCO DE DADOS
# ========================================

class Database:
    def __init__(self):
        self.arquivo = "tdz_database.json"
        self.dados = self.carregar()
    
    def carregar(self):
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            dados_padrao = {
                "tickets": {},
                "vendas": [],
                "usuarios": {},
                "feedbacks": []
            }
            self.salvar(dados_padrao)
            return dados_padrao
    
    def salvar(self, dados=None):
        if dados is None:
            dados = self.dados
        with open(self.arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

db = Database()

# ========================================
# BOT
# ========================================

class TDZBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
    
    async def setup_hook(self):
        guild = discord.Object(id=CONFIG["GUILD_ID"])
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("✅ Slash Commands sincronizados!")
    
    async def on_ready(self):
        print(f"🤖 Bot {self.user} online!")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="TDZ Divulgações | /painel"),
            status=discord.Status.online
        )

bot = TDZBot()

# ========================================
# FUNÇÕES
# ========================================

def is_dono(member: discord.Member) -> bool:
    return member.id == CONFIG["DONO_ID"]

def is_vip(member: discord.Member) -> bool:
    return any(cargo.name == CONFIG["CARGO_VIP"] for cargo in member.roles)

def get_cargo(guild: discord.Guild, nome: str):
    return discord.utils.get(guild.roles, name=nome)

def criar_embed(titulo: str, descricao: str, cor: discord.Color, imagem: str = None):
    embed = discord.Embed(title=titulo, description=descricao, color=cor, timestamp=datetime.datetime.now())
    embed.set_footer(text="TDZ Divulgações © 2026")
    if imagem:
        embed.set_image(url=imagem)
    return embed

def get_star_emoji(qtd: int) -> str:
    return "★" * qtd + "☆" * (5 - qtd)

# ========================================
# MODAL AVALIAÇÃO
# ========================================

class AvaliacaoModal(ui.Modal, title="🌟 Avaliar Atendimento"):
    staff = ui.TextInput(label="Staff Responsável", placeholder="Quem te atendeu?", required=True, max_length=100)
    descricao = ui.TextInput(label="Como foi o atendimento?", placeholder="Sua experiência...", required=True, style=discord.TextStyle.paragraph, max_length=1000)
    estrelas = ui.TextInput(label="Estrelas (0 a 5)", placeholder="0-5", required=True, max_length=1)
    
    def __init__(self, user_id: int, user_name: str, user_avatar: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.user_avatar = user_avatar
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            estrelas_num = int(self.estrelas.value)
            if estrelas_num < 0 or estrelas_num > 5:
                await interaction.response.send_message("❌ Digite 0-5!", ephemeral=True)
                return
            
            canal = discord.utils.get(interaction.guild.channels, name=CONFIG["CANAL_FEEDBACK"])
            if canal:
                stars = get_star_emoji(estrelas_num)
                embed = discord.Embed(title="🌟 Nova Avaliação", color=discord.Color.gold(), timestamp=datetime.datetime.now())
                embed.add_field(name="👤 Usuário", value=f"`{self.user_name}`", inline=True)
                embed.add_field(name="🛡️ Staff", value=f"`{self.staff.value}`", inline=True)
                embed.add_field(name="📝 Descrição", value=f"```{self.descricao.value}```", inline=False)
                embed.set_thumbnail(url=self.user_avatar)
                embed.set_footer(text=f"{stars} ({estrelas_num}/5)")
                await canal.send(embed=embed)
            
            await interaction.response.send_message("✅ Obrigado!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Apenas números!", ephemeral=True)

class AvaliacaoView(ui.View):
    def __init__(self, user_id: int, user_name: str, user_avatar: str):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.user_name = user_name
        self.user_avatar = user_avatar
    
    @ui.button(label="🌟 Avaliar Atendimento", style=discord.ButtonStyle.green)
    async def avaliar(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Apenas você!", ephemeral=True)
            return
        await interaction.response.send_modal(AvaliacaoModal(self.user_id, self.user_name, self.user_avatar))

# ========================================
# TICKET VIEW
# ========================================

class TicketView(ui.View):
    def __init__(self, user_id: int, produto: str, valor: float, user_name: str):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.produto = produto
        self.valor = valor
        self.user_name = user_name
        self.staff_responsavel = None
    
    @ui.button(label="🙋 Assumir Ticket", style=discord.ButtonStyle.blurple)
    async def assumir(self, interaction: discord.Interaction, button: ui.Button):
        if self.staff_responsavel:
            await interaction.response.send_message(f"❌ Já assumido por {self.staff_responsavel}!", ephemeral=True)
            return
        
        self.staff_responsavel = interaction.user.display_name
        
        embed = criar_embed(
            f"🛒 Ticket - {self.produto}",
            f"**Comprador:** <@{self.user_id}> (`{self.user_name}`)\n"
            f"**Produto:** {self.produto}\n"
            f"**Valor:** R${self.valor},00\n"
            f"**🛡️ Staff:** `{self.staff_responsavel}`\n\n"
            f"{CONFIG['EMOJI_PIX']} **PIX:** `{CONFIG['PIX_CHAVE']}`",
            discord.Color.gold(),
            CONFIG["IMAGENS"]["vip"]
        )
        
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("✅ Assumido!", ephemeral=True)
    
    @ui.button(label="✅ Confirmar Pagamento", style=discord.ButtonStyle.green)
    async def confirmar(self, interaction: discord.Interaction, button: ui.Button):
        # APENAS O DONO ESPECÍFICO PODE CONFIRMAR
        if interaction.user.id != CONFIG["DONO_ID"]:
            await interaction.response.send_message("❌ Apenas <@1327679436128129159> pode confirmar!", ephemeral=True)
            return
        
        member = interaction.guild.get_member(self.user_id)
        if not member:
            await interaction.response.send_message("❌ Usuário não encontrado!", ephemeral=True)
            return
        
        # ADICIONA CARGO VIP AUTOMATICAMENTE
        cargo_vip = get_cargo(interaction.guild, CONFIG["CARGO_VIP"])
        if cargo_vip:
            try:
                await member.add_roles(cargo_vip)
                cargo_adicionado = True
            except:
                cargo_adicionado = False
        else:
            cargo_adicionado = False
        
        await interaction.response.send_message("✅ Confirmado! Entregando...", ephemeral=True)
        
        # Mensagem no canal
        msg_cargo = " + Cargo VIP adicionado!" if cargo_adicionado else ""
        await interaction.channel.send(f"🎉 {member.mention} seu **{self.produto}** foi ativado!{msg_cargo}")
        
        # DM com avaliação
        try:
            embed_dm = criar_embed(
                "🎉 Compra Finalizada!",
                f"**Produto:** {self.produto}\n"
                f"**Valor:** R${self.valor},00\n"
                f"**Staff:** `{self.staff_responsavel}`\n\n"
                f"Obrigado! Avalie abaixo:",
                discord.Color.green(),
                CONFIG["IMAGENS"]["vip"]
            )
            view_avaliacao = AvaliacaoView(self.user_id, self.user_name, member.avatar.url if member.avatar else None)
            await member.send(embed=embed_dm, view=view_avaliacao)
        except:
            pass
        
        # Botão fechar
        view_final = ui.View(timeout=None)
        btn_fechar = ui.Button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.gray)
        
        async def fechar_callback(interact):
            if interact.user.id != CONFIG["DONO_ID"]:
                await interact.response.send_message("❌ Apenas o Dono!", ephemeral=True)
                return
            await interact.response.send_message("🔒 Fechando...")
            await asyncio.sleep(3)
            await interact.channel.delete()
        
        btn_fechar.callback = fechar_callback
        view_final.add_item(btn_fechar)
        await interaction.message.edit(view=view_final)
    
    @ui.button(label="❌ Cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id and interaction.user.id != CONFIG["DONO_ID"]:
            await interaction.response.send_message("❌ Sem permissão!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Cancelando...", ephemeral=True)
        await asyncio.sleep(2)
        await interaction.channel.delete()

class ProdutoSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="⭐ Destacar Mensagem",
                description=f"R${CONFIG['PRECOS']['destacar_mensagem']} - Destaque nas divulgações",
                value="destacar_mensagem",
                emoji="⭐"
            ),
            discord.SelectOption(
                label="💎 VIP",
                description=f"R${CONFIG['PRECOS']['vip']} - Acesso /divulgarvip + Prioridade",
                value="vip",
                emoji="💎"
            ),
            discord.SelectOption(
                label="🚀 Divulgação Global",
                description=f"R${CONFIG['PRECOS']['divulgacao_global']} - Todos canais + Ping",
                value="divulgacao_global",
                emoji="🚀"
            )
        ]
        super().__init__(placeholder="🛒 Selecione...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        produtos = {
            "destacar_mensagem": ("⭐ Destacar Mensagem", CONFIG["PRECOS"]["destacar_mensagem"]),
            "vip": ("💎 VIP", CONFIG["PRECOS"]["vip"]),
            "divulgacao_global": ("🚀 Divulgação Global", CONFIG["PRECOS"]["divulgacao_global"])
        }
        
        produto, valor = produtos[self.values[0]]
        
        embed = criar_embed(
            "🛒 Produto Selecionado",
            f"**{produto}** - R${valor},00\n\nClique em **Continuar**!",
            discord.Color.blue(),
            CONFIG["IMAGENS"]["shop"]
        )
        
        view = ContinuarView(produto, valor)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ContinuarView(ui.View):
    def __init__(self, produto: str, valor: float):
        super().__init__(timeout=120)
        self.produto = produto
        self.valor = valor
    
    @ui.button(label="Continuar", style=discord.ButtonStyle.green, emoji="🛒")
    async def continuar(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        categoria = discord.utils.get(guild.categories, name=CONFIG["CATEGORIA_TICKETS"])
        
        if not categoria:
            categoria = await guild.create_category(CONFIG["CATEGORIA_TICKETS"])
        
        canal_nome = f"🛒・compra-{interaction.user.name}".lower().replace(" ", "-")[:100]
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        # Dono tem acesso
        dono = guild.get_member(CONFIG["DONO_ID"])
        if dono:
            overwrites[dono] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        canal = await guild.create_text_channel(name=canal_nome, category=categoria, overwrites=overwrites)
        
        embed = criar_embed(
            f"🛒 Ticket - {self.produto}",
            f"**Comprador:** <@{interaction.user.id}> (`{interaction.user.display_name}`)\n"
            f"**Produto:** {self.produto}\n"
            f"**Valor:** R${self.valor},00\n"
            f"**🛡️ Staff:** `Aguardando...`\n\n"
            f"{CONFIG['EMOJI_PIX']} **PIX:** `{CONFIG['PIX_CHAVE']}`",
            discord.Color.gold(),
            CONFIG["IMAGENS"]["vip"]
        )
        
        view = TicketView(interaction.user.id, self.produto, self.valor, interaction.user.display_name)
        msg = await canal.send(f"🛒 {interaction.user.mention} bem-vindo!", embed=embed, view=view)
        await msg.pin()
        
        await interaction.response.send_message(f"✅ Ticket: {canal.mention}", ephemeral=True)
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.red, emoji="❌")
    async def cancelar(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("❌ Cancelado!", ephemeral=True)

class PainelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProdutoSelect())

# ========================================
# COMANDOS
# ========================================

@bot.tree.command(name="painel", description="🛒 Painel de compras")
async def painel(interaction: discord.Interaction):
    if not is_dono(interaction.user):
        await interaction.response.send_message("❌ Apenas Dono!", ephemeral=True)
        return
    
    embed = criar_embed(
        "🛒 TDZ SHOP",
        "**Planos:**\n\n"
        f"⭐ **Destacar Mensagem** - R${CONFIG['PRECOS']['destacar_mensagem']}\n"
        f"💎 **VIP** - R${CONFIG['PRECOS']['vip']} (Acesso /divulgarvip)\n"
        f"🚀 **Divulgação Global** - R${CONFIG['PRECOS']['divulgacao_global']}\n\n"
        "**👇 Selecione:**",
        discord.Color.purple(),
        CONFIG["IMAGENS"]["shop"]
    )
    await interaction.response.send_message(embed=embed, view=PainelView())

@bot.tree.command(name="divulgar", description="📢 Divulgação normal")
@app_commands.describe(canal="Canal de destino", link="Link do Discord", texto="Descrição")
async def divulgar(
    interaction: discord.Interaction,
    canal: discord.TextChannel,
    link: str,
    texto: str
):
    embed = criar_embed(
        "📢 Nova Divulgação",
        f"{texto}\n\n{link}",
        discord.Color.green()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    
    msg = await canal.send(content=f"📢 {interaction.user.mention}:", embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    
    await interaction.response.send_message(f"✅ Divulgado em {canal.mention}!", ephemeral=True)

@bot.tree.command(name="divulgarvip", description="💎 Divulgação VIP colorida")
@app_commands.describe(texto="Texto", cor="Cor do embed")
@app_commands.choices(cor=[
    app_commands.Choice(name="🔵 Azul", value="0x3498db"),
    app_commands.Choice(name="🔴 Vermelho", value="0xe74c3c"),
    app_commands.Choice(name="🟢 Verde", value="0x2ecc71"),
    app_commands.Choice(name="🟣 Roxo", value="0x9b59b6"),
    app_commands.Choice(name="🟡 Amarelo", value="0xf1c40f"),
    app_commands.Choice(name="🟠 Laranja", value="0xe67e22")
])
async def divulgarvip(interaction: discord.Interaction, texto: str, cor: app_commands.Choice[str]):
    # VERIFICA SE TEM CARGO VIP
    if not is_vip(interaction.user):
        await interaction.response.send_message(
            f"❌ Você precisa do cargo **{CONFIG['CARGO_VIP']}** para usar este comando!\n"
            f"Compre no `/painel`!", 
            ephemeral=True
        )
        return
    
    cor_int = int(cor.value, 16)
    
    embed = discord.Embed(
        title="💎 DIVULGAÇÃO VIP",
        description=texto,
        color=cor_int,
        timestamp=datetime.datetime.now()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.set_footer(text="⭐ VIP")
    
    # Envia em todos os canais de divulgação
    canais = [
        CONFIG["CANAL_SERVIDORES"],
        CONFIG["CANAL_YOUTUBE"],
        CONFIG["CANAL_TWITCH"],
        CONFIG["CANAL_SOCIAIS"],
        CONFIG["CANAL_ARTES"],
        CONFIG["CANAL_SERVICOS"]
    ]
    
    enviados = 0
    for nome in canais:
        canal = discord.utils.get(interaction.guild.channels, name=nome)
        if canal:
            await canal.send(content=f"💎 {interaction.user.mention}:", embed=embed)
            enviados += 1
    
    await interaction.response.send_message(f"✅ VIP enviado em {enviados} canais!", ephemeral=True)

@bot.tree.command(name="anunciar", description="📢 Anúncio staff")
@app_commands.describe(canal="Canal", titulo="Título", mensagem="Texto")
@app_commands.checks.has_permissions(manage_messages=True)
async def anunciar(interaction: discord.Interaction, canal: discord.TextChannel, titulo: str, mensagem: str):
    try:
        embed = criar_embed(f"📢 {titulo}", mensagem, discord.Color.blue(), CONFIG["IMAGENS"]["anuncio"])
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await canal.send(embed=embed)
        await interaction.response.send_message(f"✅ Enviado em {canal.mention}!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erro: {str(e)}", ephemeral=True)

@bot.tree.command(name="regras", description="📕 Regras")
async def regras(interaction: discord.Interaction):
    embed = criar_embed(
        "📕 REGRAS",
        "**1.** Proibido NSFW\n**2.** Use canais corretos\n**3.** Proibido spam\n**4.** Respeite todos\n**5.** Proibido scam\n**6.** Proibido rivais\n**7.** Use `/divulgar`\n**8.** Proibido ilegal\n\n**⚠️ Quebra = Ban!**",
        discord.Color.red(),
        CONFIG["IMAGENS"]["regras"]
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="infos", description="ℹ️ Informações")
async def infos(interaction: discord.Interaction):
    guild = interaction.guild
    embed = criar_embed(
        "ℹ️ INFORMAÇÕES",
        f"**Nome:** {guild.name}\n**Membros:** {guild.member_count}\n**Dono:** {guild.owner.mention if guild.owner else 'N/A'}\n\n"
        f"⭐ Destacar - R${CONFIG['PRECOS']['destacar_mensagem']}\n"
        f"💎 VIP - R${CONFIG['PRECOS']['vip']}\n"
        f"🚀 Global - R${CONFIG['PRECOS']['divulgacao_global']}\n\n"
        "**👥 Staff:** Dono 👑 | Mod",
        discord.Color.blue(),
        CONFIG["IMAGENS"]["info"]
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="say", description="🤖 Bot fala")
@app_commands.describe(mensagem="Texto", canal="Canal (opcional)")
@app_commands.checks.has_permissions(administrator=True)
async def say(interaction: discord.Interaction, mensagem: str, canal: Optional[discord.TextChannel] = None):
    destino = canal or interaction.channel
    await destino.send(mensagem)
    await interaction.response.send_message("✅ Enviado!", ephemeral=True)

@bot.tree.command(name="sorteio", description="🎉 Sorteio")
@app_commands.describe(premio="Prêmio", duracao="Minutos", vencedores="Qtd")
@app_commands.checks.has_permissions(manage_messages=True)
async def sorteio(interaction: discord.Interaction, premio: str, duracao: int, vencedores: int = 1):
    embed = criar_embed("🎉 SORTEIO!", f"**Prêmio:** {premio}\n**Duração:** {duracao}min\n**Vencedores:** {vencedores}\n\nReaja com 🎉!", discord.Color.gold(), CONFIG["IMAGENS"]["giveaway"])
    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("🎉")
    await interaction.response.send_message("🎉 Iniciado!", ephemeral=True)
    
    await asyncio.sleep(duracao * 60)
    
    msg_atual = await interaction.channel.fetch_message(msg.id)
    reacao = discord.utils.get(msg_atual.reactions, emoji="🎉")
    
    if reacao:
        users = [u async for u in reacao.users() if not u.bot]
        if len(users) >= vencedores:
            ganhadores = random.sample(users, min(vencedores, len(users)))
            mencoes = ", ".join([g.mention for g in ganhadores])
            await interaction.channel.send(f"🎉 {mencoes} ganhou: **{premio}**!")

@bot.tree.command(name="fechar_ticket", description="🔒 Fecha ticket")
@app_commands.checks.has_permissions(manage_channels=True)
async def fechar_ticket(interaction: discord.Interaction):
    if "compra-" not in interaction.channel.name:
        await interaction.response.send_message("❌ Não é ticket!", ephemeral=True)
        return
    await interaction.response.send_message("🔒 Fechando...")
    await asyncio.sleep(3)
    await interaction.channel.delete()

@bot.tree.command(name="perfil", description="👤 Perfil")
async def perfil(interaction: discord.Interaction, membro: Optional[discord.Member] = None):
    alvo = membro or interaction.user
    stats = db.dados["usuarios"].get(str(alvo.id), {"divulgacoes": 0})
    embed = criar_embed(f"👤 {alvo.display_name}", f"**Divulgações:** {stats.get('divulgacoes', 0)}", discord.Color.purple())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="🏓 Ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

@bot.tree.command(name="ajuda", description="❓ Ajuda")
async def ajuda(interaction: discord.Interaction):
    embed = criar_embed(
        "❓ AJUDA",
        "**📢 Divulgação:**\n`/divulgar` - Normal (seleciona canal)\n`/divulgarvip` - VIP colorido (precisa de cargo)\n\n"
        "**🛒 Loja:**\n`/painel` - Comprar (Dono only)\n\n"
        "**📢 Admin:**\n`/anunciar` `/say` `/sorteio`\n\n"
        "**ℹ️ Info:**\n`/regras` `/infos` `/perfil` `/ping`",
        discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========================================
# EVENTOS
# ========================================

@bot.event
async def on_member_remove(member):
    if member.guild.id != CONFIG["GUILD_ID"]:
        return
    canal = discord.utils.get(member.guild.channels, name=CONFIG["CANAL_SAIDA"])
    if canal:
        embed = criar_embed("👋 Saída", f"{member.display_name} saiu.", discord.Color.red())
        await canal.send(embed=embed)

# ========================================
# INICIAR
# ========================================

if __name__ == "__main__":
    print("🚀 TDZ Bot iniciando...")
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN não encontrado!")
    else:
        bot.run(token)
