"""
========================================
TDZ DIVULGAÇÕES - BOT COMPLETO
========================================
Bot de divulgação com sistema de vendas VIP
Slash Commands | Python 3.8+ | discord.py 2.0+
========================================
"""

import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
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
    # Token do Bot (Railway usa DISCORD_TOKEN)
    "TOKEN": os.getenv("DISCORD_TOKEN", "SEU_TOKEN_AQUI"),
    
    # IDs do Servidor
    "GUILD_ID": 1465866618578932055,
    
    # Cargos Staff
    "CARGO_DONO": "Dono 👑",
    "CARGO_MOD": "Mod",
    
    # Categorias
    "CATEGORIA_TICKETS": "🛒 Compras",
    "CATEGORIA_LOGS": "📊 Logs",
    
    # Canais Específicos (nomes exatos)
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
    
    # Configurações de Vendas
    "PIX_CHAVE": "sua-chave-pix-aqui",  # Altere para sua chave PIX
    "PAYPAL_EMAIL": "seu-email@paypal.com",  # Altere para seu PayPal
    
    # Preços (R$)
    "PRECOS": {
        "vip_basico": 15,
        "vip_intermediario": 30,
        "vip_premium": 50,
        "divulgacao_global": 20
    },
    
    # Imagens (URLs atualizadas)
    "IMAGENS": {
        "regras": "https://i.imgur.com/Vq8OfY5.png",
        "info": "https://i.imgur.com/Vq8OfY5.png",
        "anuncio_bom": "https://i.imgur.com/DbgjpnR.png",
        "anuncio_ruim": "https://i.imgur.com/DbgjpnR.png",
        "vip": "https://i.imgur.com/DbgjpnR.png",
        "welcome": "https://i.imgur.com/DbgjpnR.png",
        "shop": "https://i.imgur.com/DbgjpnR.png",
        "giveaway": "https://i.imgur.com/DbgjpnR.png",
        "parceria": "https://i.imgur.com/DbgjpnR.png",
        "eventos": "https://i.imgur.com/DbgjpnR.png"
    }
}

# ========================================
# BANCO DE DADOS JSON
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
                "divulgacoes": [],
                "config": {}
            }
            self.salvar(dados_padrao)
            return dados_padrao
    
    def salvar(self, dados=None):
        if dados is None:
            dados = self.dados
        with open(self.arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    
    def get(self, chave, padrao=None):
        return self.dados.get(chave, padrao)
    
    def set(self, chave, valor):
        self.dados[chave] = valor
        self.salvar()

db = Database()

# ========================================
# CLIENT DO BOT
# ========================================

class TDZBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
    
    async def setup_hook(self):
        # Sincroniza comandos de barra
        guild = discord.Object(id=CONFIG["GUILD_ID"])
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("✅ Slash Commands sincronizados!")
    
    async def on_ready(self):
        print(f"🤖 Bot {self.user} online!")
        print(f"📊 Servidor: {CONFIG['GUILD_ID']}")
        print(f"🌐 Latência: {round(self.latency * 1000)}ms")
        
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="TDZ Divulgações | /painel"
            ),
            status=discord.Status.online
        )

bot = TDZBot()

# ========================================
# FUNÇÕES AUXILIARES
# ========================================

def is_staff(member: discord.Member) -> bool:
    """Verifica se membro é staff"""
    cargos_staff = [CONFIG["CARGO_DONO"], CONFIG["CARGO_MOD"]]
    return any(cargo.name in cargos_staff for cargo in member.roles)

def get_cargo_staff(guild: discord.Guild, nome: str):
    """Pega cargo staff pelo nome"""
    return discord.utils.get(guild.roles, name=nome)

def criar_embed(titulo: str, descricao: str, cor: discord.Color, imagem: str = None):
    """Cria embed padrão com imagem de banner"""
    embed = discord.Embed(
        title=f"**{titulo}**",
        description=descricao,
        color=cor,
        timestamp=datetime.datetime.now()
    )
    embed.set_footer(text="TDZ Divulgações © 2026", icon_url=CONFIG["IMAGENS"]["welcome"])
    if imagem:
        embed.set_image(url=imagem)
    return embed

# ========================================
# SISTEMA DE TICKETS/VENDAS
# ========================================

class TicketView(ui.View):
    def __init__(self, user_id: int, produto: str, valor: float):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.produto = produto
        self.valor = valor
        self.status = "aguardando"
    
    @ui.button(label="✅ Confirmar Pagamento", style=discord.ButtonStyle.green, custom_id="confirmar_pagamento")
    async def confirmar(self, interaction: discord.Interaction, button: ui.Button):
        if not is_staff(interaction.user):
            await interaction.response.send_message("❌ Apenas staff pode confirmar!", ephemeral=True)
            return
        
        self.status = "pago"
        await interaction.response.send_message("✅ Pagamento confirmado! Entregando produto...", ephemeral=True)
        
        # Aqui você adiciona a lógica de entrega (cargos, permissões, etc)
        await interaction.channel.send(f"🎉 {interaction.guild.get_member(self.user_id).mention} seu **{self.produto}** foi ativado!")
        
        # Log
        canal_logs = discord.utils.get(interaction.guild.channels, name="logs-vendas")
        if canal_logs:
            embed = criar_embed(
                "Venda Confirmada",
                f"**Produto:** {self.produto}\n**Valor:** R${self.valor}\n**Comprador:** <@{self.user_id}>\n**Staff:** {interaction.user.mention}",
                discord.Color.green(),
                CONFIG["IMAGENS"]["vip"]
            )
            await canal_logs.send(embed=embed)
    
    @ui.button(label="❌ Cancelar", style=discord.ButtonStyle.red, custom_id="cancelar_compra")
    async def cancelar(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id and not is_staff(interaction.user):
            await interaction.response.send_message("❌ Você não pode cancelar esta compra!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Compra cancelada. Fechando ticket...", ephemeral=True)
        await asyncio.sleep(3)
        await interaction.channel.delete()
    
    @ui.button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.gray, custom_id="fechar_ticket")
    async def fechar(self, interaction: discord.Interaction, button: ui.Button):
        if not is_staff(interaction.user):
            await interaction.response.send_message("❌ Apenas staff pode fechar!", ephemeral=True)
            return
        
        await interaction.response.send_message("🔒 Fechando ticket em 5 segundos...", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class ProdutoSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="⭐ VIP Básico",
                description="R$15 - Divulgação por 1 dia",
                value="vip_basico",
                emoji="⭐"
            ),
            discord.SelectOption(
                label="🔥 VIP Intermediário",
                description="R$30 - Divulgação 3 dias + Destaque",
                value="vip_intermediario",
                emoji="🔥"
            ),
            discord.SelectOption(
                label="💎 VIP Premium",
                description="R$50 - Divulgação 7 dias + Fixado + Destaque",
                value="vip_premium",
                emoji="💎"
            ),
            discord.SelectOption(
                label="🚀 Divulgação Global",
                description="R$20 - Divulgação em todos canais + Ping",
                value="divulgacao_global",
                emoji="🚀"
            )
        ]
        super().__init__(
            placeholder="🛒 Selecione um produto...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="select_produto"
        )
    
    async def callback(self, interaction: discord.Interaction):
        produto_nome = {
            "vip_basico": "⭐ VIP Básico",
            "vip_intermediario": "🔥 VIP Intermediário",
            "vip_premium": "💎 VIP Premium",
            "divulgacao_global": "🚀 Divulgação Global"
        }
        
        produto = produto_nome[self.values[0]]
        valor = CONFIG["PRECOS"][self.values[0]]
        
        # Responde ephemeral
        embed = criar_embed(
            "🛒 Produto Selecionado",
            f"**Produto:** {produto}\n**Valor:** R${valor},00\n\nClique em **Continuar** para criar seu ticket!",
            discord.Color.blue(),
            CONFIG["IMAGENS"]["shop"]
        )
        
        view = ContinuarView(produto, valor, self.values[0])
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ContinuarView(ui.View):
    def __init__(self, produto: str, valor: float, produto_id: str):
        super().__init__(timeout=120)
        self.produto = produto
        self.valor = valor
        self.produto_id = produto_id
    
    @ui.button(label="Continuar Compra", style=discord.ButtonStyle.green, emoji="🛒")
    async def continuar(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        categoria = discord.utils.get(guild.categories, name=CONFIG["CATEGORIA_TICKETS"])
        
        if not categoria:
            categoria = await guild.create_category(CONFIG["CATEGORIA_TICKETS"])
        
        # Cria canal do ticket
        canal_nome = f"🛒・compra-{interaction.user.name}".lower().replace(" ", "-")
        
        # Permissões: apenas comprador e staff
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        # Adiciona permissões para cargos staff
        for cargo_nome in [CONFIG["CARGO_DONO"], CONFIG["CARGO_MOD"]]:
            cargo = get_cargo_staff(guild, cargo_nome)
            if cargo:
                overwrites[cargo] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        canal = await guild.create_text_channel(
            name=canal_nome,
            category=categoria,
            overwrites=overwrites
        )
        
        # Mensagem do ticket
        embed = criar_embed(
            f"🛒 Ticket de Compra - {self.produto}",
            f"**Comprador:** {interaction.user.mention}\n"
            f"**Produto:** {self.produto}\n"
            f"**Valor:** R${self.valor},00\n\n"
            f"**💳 Formas de Pagamento:**\n"
            f"• **PIX:** `{CONFIG['PIX_CHAVE']}`\n"
            f"• **PayPal:** `{CONFIG['PAYPAL_EMAIL']}`\n\n"
            f"Após o pagamento, clique em **Confirmar Pagamento** e aguarde a verificação da staff!",
            discord.Color.gold(),
            CONFIG["IMAGENS"]["vip"]
        )
        
        view = TicketView(interaction.user.id, self.produto, self.valor)
        msg = await canal.send(f"🛒 {interaction.user.mention} bem-vindo ao seu ticket!", embed=embed, view=view)
        
        # Pin na mensagem principal
        await msg.pin()
        
        # Confirmação ephemeral
        await interaction.response.send_message(
            f"✅ Ticket criado em {canal.mention}! Complete seu pagamento lá.",
            ephemeral=True
        )
        
        # Salva no banco
        db.dados["tickets"][str(canal.id)] = {
            "user_id": interaction.user.id,
            "produto": self.produto,
            "valor": self.valor,
            "status": "aberto",
            "data": str(datetime.datetime.now())
        }
        db.salvar()
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.red, emoji="❌")
    async def cancelar(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("❌ Compra cancelada!", ephemeral=True)
        self.stop()

class PainelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProdutoSelect())

# ========================================
# COMANDOS SLASH
# ========================================

@bot.tree.command(name="painel", description="🛒 Abre o painel de compras VIP")
@app_commands.checks.has_permissions(administrator=True)
async def painel(interaction: discord.Interaction):
    """Envia o painel de vendas no canal"""
    embed = criar_embed(
        "🛒 TDZ SHOP - Loja de Divulgações",
        "**Bem-vindo à nossa loja!**\n\n"
        "Aqui você pode adquirir planos VIP para destacar suas divulgações no servidor.\n\n"
        "**📦 Produtos Disponíveis:**\n"
        "⭐ **VIP Básico** - R$15 (1 dia de divulgação)\n"
        "🔥 **VIP Intermediário** - R$30 (3 dias + destaque)\n"
        "💎 **VIP Premium** - R$50 (7 dias + fixado + destaque)\n"
        "🚀 **Divulgação Global** - R$20 (Todos canais + ping)\n\n"
        "**👇 Selecione abaixo:**",
        discord.Color.purple(),
        CONFIG["IMAGENS"]["shop"]
    )
    
    view = PainelView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="regras", description="📕 Mostra as regras do servidor")
async def regras(interaction: discord.Interaction):
    """Mostra embed de regras com banner"""
    embed = criar_embed(
        "📕 REGRAS DO SERVIDOR",
        "**Leia atentamente antes de divulgar:**\n\n"
        "**1.** Proibido conteúdo NSFW/18+\n"
        "**2.** Proibido divulgar sem usar os canais corretos\n"
        "**3.** Proibido spam/flood\n"
        "**4.** Respeite todos os membros\n"
        "**5.** Proibido links de phishing/scam\n"
        "**6.** Proibido divulgação de servidores rivais\n"
        "**7.** Use o bot para divulgar corretamente\n"
        "**8.** Proibido conteúdo ilegal\n\n"
        "**⚠️ Quebra de regras resultará em banimento!**",
        discord.Color.red(),
        CONFIG["IMAGENS"]["regras"]
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="infos", description="ℹ️ Informações sobre o servidor")
async def infos(interaction: discord.Interaction):
    """Mostra informações do servidor"""
    guild = interaction.guild
    
    embed = criar_embed(
        "ℹ️ INFORMAÇÕES DO SERVIDOR",
        f"**Nome:** {guild.name}\n"
        f"**ID:** `{guild.id}`\n"
        f"**Dono:** {guild.owner.mention if guild.owner else 'N/A'}\n"
        f"**Membros:** {guild.member_count}\n"
        f"**Criado em:** {guild.created_at.strftime('%d/%m/%Y')}\n\n"
        "**🎯 Objetivo:**\n"
        "Servidor dedicado à divulgação de comunidades, lives, canais e arte digital.\n\n"
        "**💎 Benefícios VIP:**\n"
        "• Divulgações destacadas\n"
        "• Acesso a canais exclusivos\n"
        "• Menção em anúncios\n"
        "• Suporte prioritário\n\n"
        "**👥 Staff:**\n"
        "• Dono 👑\n"
        "• Mod\n\n"
        "Use `/painel` para comprar VIP!",
        discord.Color.blue(),
        CONFIG["IMAGENS"]["info"]
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="anunciar", description="📢 Cria um anúncio no servidor")
@app_commands.describe(
    canal="Canal onde o anúncio será enviado",
    tipo="Tipo do anúncio (bom ou ruim)",
    titulo="Título do anúncio",
    mensagem="Conteúdo do anúncio"
)
@app_commands.choices(tipo=[
    app_commands.Choice(name="✅ Bom (Verde)", value="bom"),
    app_commands.Choice(name="❌ Ruim (Vermelho)", value="ruim")
])
@app_commands.checks.has_permissions(manage_messages=True)
async def anunciar(
    interaction: discord.Interaction,
    canal: discord.TextChannel,
    tipo: app_commands.Choice[str],
    titulo: str,
    mensagem: str
):
    """Comando para staff anunciar"""
    
    cor = discord.Color.green() if tipo.value == "bom" else discord.Color.red()
    imagem = CONFIG["IMAGENS"]["anuncio_bom"] if tipo.value == "bom" else CONFIG["IMAGENS"]["anuncio_ruim"]
    emoji = "✅" if tipo.value == "bom" else "❌"
    
    embed = criar_embed(
        f"{emoji} {titulo}",
        mensagem,
        cor,
        imagem
    )
    
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    
    await canal.send(embed=embed)
    await interaction.response.send_message(f"📢 Anúncio enviado em {canal.mention}!", ephemeral=True)

@bot.tree.command(name="divulgar", description="📢 Divulga seu servidor/canal")
@app_commands.describe(
    tipo="O que você quer divulgar",
    link="Link do servidor/canal/conteúdo",
    descricao="Descrição da sua divulgação"
)
@app_commands.choices(tipo=[
    app_commands.Choice(name="💬 Servidor Discord", value="servidor"),
    app_commands.Choice(name="📹 Canal YouTube", value="youtube"),
    app_commands.Choice(name="🎬 Live Twitch", value="twitch"),
    app_commands.Choice(name="📱 Redes Sociais", value="social"),
    app_commands.Choice(name="🖼️ Arte Digital", value="arte"),
    app_commands.Choice(name="🛠️ Serviço/Oferta", value="servico")
])
async def divulgar(
    interaction: discord.Interaction,
    tipo: app_commands.Choice[str],
    link: str,
    descricao: str
):
    """Comando para usuários divulgarem"""
    
    # Mapeia tipo para canal
    mapa_canais = {
        "servidor": CONFIG["CANAL_SERVIDORES"],
        "youtube": CONFIG["CANAL_YOUTUBE"],
        "twitch": CONFIG["CANAL_TWITCH"],
        "social": CONFIG["CANAL_SOCIAIS"],
        "arte": CONFIG["CANAL_ARTES"],
        "servico": CONFIG["CANAL_SERVICOS"]
    }
    
    canal_nome = mapa_canais.get(tipo.value)
    canal = discord.utils.get(interaction.guild.channels, name=canal_nome)
    
    if not canal:
        await interaction.response.send_message("❌ Canal de divulgação não encontrado! Contate um administrador.", ephemeral=True)
        return
    
    # Cria embed de divulgação
    embed = criar_embed(
        f"📢 Nova Divulgação - {tipo.name}",
        f"**Descrição:**\n{descricao}\n\n**Link:**\n{link}",
        discord.Color.green(),
        None
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url if interaction.user.avatar else None
    )
    embed.add_field(name="👤 Divulgador", value=interaction.user.mention, inline=True)
    embed.add_field(name="📅 Data", value=datetime.datetime.now().strftime("%d/%m/%Y"), inline=True)
    
    # Envia
    msg = await canal.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    
    # Confirmação
    await interaction.response.send_message(f"✅ Divulgado com sucesso em {canal.mention}!", ephemeral=True)
    
    # Salva estatísticas
    uid = str(interaction.user.id)
    if uid not in db.dados["usuarios"]:
        db.dados["usuarios"][uid] = {"divulgacoes": 0, "upvotes": 0}
    db.dados["usuarios"][uid]["divulgacoes"] += 1
    db.salvar()

@bot.tree.command(name="fechar_ticket", description="🔒 Fecha um ticket de compra")
@app_commands.checks.has_permissions(manage_channels=True)
async def fechar_ticket(interaction: discord.Interaction):
    """Fecha o canal de ticket atual"""
    if "compra-" not in interaction.channel.name:
        await interaction.response.send_message("❌ Este comando só funciona em canais de ticket!", ephemeral=True)
        return
    
    await interaction.response.send_message("🔒 Fechando ticket em 5 segundos...")
    await asyncio.sleep(5)
    await interaction.channel.delete()

@bot.tree.command(name="say", description="🤖 Faz o bot falar algo")
@app_commands.describe(mensagem="O que o bot deve dizer", canal="Canal de destino (opcional)")
@app_commands.checks.has_permissions(administrator=True)
async def say(interaction: discord.Interaction, mensagem: str, canal: Optional[discord.TextChannel] = None):
    """Comando say para admin"""
    destino = canal or interaction.channel
    await destino.send(mensagem)
    await interaction.response.send_message("✅ Mensagem enviada!", ephemeral=True)

@bot.tree.command(name="embed", description="📋 Cria um embed personalizado")
@app_commands.checks.has_permissions(administrator=True)
async def embed(
    interaction: discord.Interaction,
    titulo: str,
    descricao: str,
    cor: Optional[str] = "azul",
    imagem: Optional[str] = None
):
    """Cria embed customizado"""
    cores = {
        "azul": discord.Color.blue(),
        "vermelho": discord.Color.red(),
        "verde": discord.Color.green(),
        "roxo": discord.Color.purple(),
        "dourado": discord.Color.gold()
    }
    
    cor_final = cores.get(cor.lower(), discord.Color.blue())
    embed_msg = criar_embed(titulo, descricao, cor_final, imagem)
    
    await interaction.channel.send(embed=embed_msg)
    await interaction.response.send_message("✅ Embed enviado!", ephemeral=True)

@bot.tree.command(name="sorteio", description="🎉 Inicia um sorteio")
@app_commands.describe(
    premio="O que será sorteado",
    duracao="Duração em minutos",
    vencedores="Quantidade de vencedores"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def sorteio(
    interaction: discord.Interaction,
    premio: str,
    duracao: int,
    vencedores: int = 1
):
    """Inicia um sorteio"""
    
    embed = criar_embed(
        "🎉 SORTEIO INICIADO!",
        f"**Prêmio:** {premio}\n**Duração:** {duracao} minutos\n**Vencedores:** {vencedores}\n\nReaja com 🎉 para participar!",
        discord.Color.gold(),
        CONFIG["IMAGENS"]["giveaway"]
    )
    
    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("🎉")
    
    await interaction.response.send_message("🎉 Sorteio iniciado!", ephemeral=True)
    
    # Aguarda
    await asyncio.sleep(duracao * 60)
    
    # Busca participantes
    msg_atualizada = await interaction.channel.fetch_message(msg.id)
    reacao = discord.utils.get(msg_atualizada.reactions, emoji="🎉")
    
    if reacao:
        participantes = [user async for user in reacao.users() if not user.bot]
        if len(participantes) >= vencedores:
            ganhadores = random.sample(participantes, min(vencedores, len(participantes)))
            mencoes = ", ".join([g.mention for g in ganhadores])
            
            embed_final = criar_embed(
                "🎉 SORTEIO ENCERRADO!",
                f"**Prêmio:** {premio}\n**Ganhador(es):** {mencoes}\n**Participantes:** {len(participantes)}",
                discord.Color.green(),
                CONFIG["IMAGENS"]["giveaway"]
            )
            await msg.edit(embed=embed_final)
            await interaction.channel.send(f"🎉 Parabéns {mencoes}! Você(s) ganharam: **{premio}**!")
        else:
            await interaction.channel.send("❌ Não houve participantes suficientes!")

@bot.tree.command(name="parceria", description="🤝 Solicita uma parceria")
async def parceria(interaction: discord.Interaction):
    """Solicita parceria"""
    embed = criar_embed(
        "🤝 SOLICITAÇÃO DE PARCERIA",
        f"**Solicitante:** {interaction.user.mention}\n\n"
        f"Nossa equipe analisará seu pedido em breve!\n"
        f"Requisitos mínimos:\n"
        f"• 100+ membros\n"
        f"• Servidor ativo\n"
        f"• Temática compatível\n\n"
        f"Aguarde contato da staff!",
        discord.Color.blue(),
        CONFIG["IMAGENS"]["parceria"]
    )
    
    canal_parcerias = discord.utils.get(interaction.guild.channels, name="parcerias")
    if canal_parcerias:
        await canal_parcerias.send(embed=embed)
    
    await interaction.response.send_message("✅ Solicitação enviada! Aguarde contato da staff.", ephemeral=True)

@bot.tree.command(name="perfil", description="👤 Mostra seu perfil de divulgador")
async def perfil(interaction: discord.Interaction, membro: Optional[discord.Member] = None):
    """Mostra perfil com estatísticas"""
    alvo = membro or interaction.user
    uid = str(alvo.id)
    
    stats = db.dados["usuarios"].get(uid, {"divulgacoes": 0, "upvotes": 0})
    
    embed = criar_embed(
        f"👤 Perfil de {alvo.display_name}",
        f"**📢 Divulgações:** {stats.get('divulgacoes', 0)}\n"
        f"**👍 Upvotes:** {stats.get('upvotes', 0)}\n"
        f"**⭐ Nível:** {stats.get('nivel', 1)}\n\n"
        f"**📅 Entrou em:** {alvo.joined_at.strftime('%d/%m/%Y') if alvo.joined_at else 'N/A'}",
        discord.Color.purple(),
        alvo.avatar.url if alvo.avatar else None
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="🏓 Verifica a latência do bot")
async def ping(interaction: discord.Interaction):
    """Mostra ping"""
    latencia = round(bot.latency * 1000)
    embed = criar_embed(
        "🏓 PONG!",
        f"**Latência:** `{latencia}ms`\n**Status:** 🟢 Online",
        discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ajuda", description="❓ Mostra todos os comandos")
async def ajuda(interaction: discord.Interaction):
    """Menu de ajuda"""
    embed = criar_embed(
        "❓ CENTRAL DE AJUDA - TDZ BOT",
        "**📢 COMANDOS DE DIVULGAÇÃO:**\n"
        "`/divulgar` - Divulga seu conteúdo\n"
        "`/perfil` - Veja suas estatísticas\n\n"
        "**🛒 COMANDOS DE LOJA:**\n"
        "`/painel` - Abre a loja VIP (Admin)\n\n"
        "**📢 COMANDOS DE ANÚNCIOS:**\n"
        "`/anunciar` - Cria anúncio staff\n"
        "`/sorteio` - Inicia sorteio\n\n"
        "**ℹ️ INFORMAÇÕES:**\n"
        "`/regras` - Regras do servidor\n"
        "`/infos` - Informações gerais\n"
        "`/parceria` - Solicitar parceria\n"
        "`/ping` - Status do bot\n\n"
        "**🔧 STAFF:**\n"
        "`/fechar_ticket` - Fecha ticket\n"
        "`/say` - Bot fala algo\n"
        "`/embed` - Cria embed custom\n\n"
        "**💡 DICA:** Use os comandos com `/`",
        discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========================================
# EVENTOS (REMOVIDO ON_MEMBER_JOIN - WELCOME JÁ EXISTE)
# ========================================

@bot.event
async def on_member_remove(member):
    """Saída"""
    if member.guild.id != CONFIG["GUILD_ID"]:
        return
    
    canal = discord.utils.get(member.guild.channels, name=CONFIG["CANAL_SAIDA"])
    if canal:
        embed = criar_embed(
            "👋 ATÉ LOGO!",
            f"{member.display_name} saiu do servidor.\n\n"
            f"Agora somos **{member.guild.member_count}** membros!",
            discord.Color.red()
        )
        await canal.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Tratamento de erros"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏰ Aguarde {error.retry_after:.0f} segundos!")

# ========================================
# INICIAR BOT
# ========================================

if __name__ == "__main__":
    print("🚀 Iniciando TDZ Divulgações Bot...")
    print("📦 Verificando configurações...")
    
    # Verifica se token está configurado
    if CONFIG["TOKEN"] == "SEU_TOKEN_AQUI":
        print("❌ ERRO: Configure seu token na variável de ambiente DISCORD_TOKEN!")
    else:
        bot.run(os.getenv("DISCORD_TOKEN"))
