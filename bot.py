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
    "CANAL_FEEDBACK": "🌟-Feedback",
    
    # Configurações de Vendas
    "PIX_CHAVE": "sua-chave-pix-aqui",
    "PAYPAL_EMAIL": "seu-email@paypal.com",
    
    # Preço VIP
    "PRECO_VIP": 15,
    
    # Imagens (URLs atualizadas)
    "IMAGENS": {
        "regras": "https://i.imgur.com/Vq8OfY5.png",
        "info": "https://i.imgur.com/Vq8OfY5.png",
        "anuncio_bom": "https://i.imgur.com/DbgjpnR.png",
        "anuncio_ruim": "https://i.imgur.com/DbgjpnR.png",
        "vip": "https://i.imgur.com/ryeKviZ.png",
        "shop": "https://i.imgur.com/ryeKviZ.png",
        "giveaway": "https://i.imgur.com/DbgjpnR.png",
        "parceria": "https://i.imgur.com/DbgjpnR.png",
        "welcome": "https://i.imgur.com/DbgjpnR.png"
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
                "feedbacks": []
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

def is_dono(member: discord.Member) -> bool:
    """Verifica se é Dono 👑"""
    return any(cargo.name == CONFIG["CARGO_DONO"] for cargo in member.roles)

def is_staff(member: discord.Member) -> bool:
    """Verifica se é staff (Dono ou Mod)"""
    cargos_staff = [CONFIG["CARGO_DONO"], CONFIG["CARGO_MOD"]]
    return any(cargo.name in cargos_staff for cargo in member.roles)

def get_cargo(guild: discord.Guild, nome: str):
    """Pega cargo pelo nome"""
    return discord.utils.get(guild.roles, name=nome)

def criar_embed(titulo: str, descricao: str, cor: discord.Color, imagem: str = None, thumbnail: str = None):
    """Cria embed padrão"""
    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=cor,
        timestamp=datetime.datetime.now()
    )
    embed.set_footer(text="TDZ Divulgações © 2026")
    if imagem:
        embed.set_image(url=imagem)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    return embed

def get_star_emoji(qtd: int) -> str:
    """Retorna emojis de estrela baseado na quantidade"""
    return "★" * qtd + "☆" * (5 - qtd)

# ========================================
# MODAL DE AVALIAÇÃO
# ========================================

class AvaliacaoModal(ui.Modal, title="🌟 Avaliar Atendimento"):
    staff = ui.TextInput(
        label="Staff Responsável",
        placeholder="Nome do staff que te atendeu",
        required=True,
        max_length=100
    )
    
    descricao = ui.TextInput(
        label="Descreva como foi o atendimento",
        placeholder="Conte-nos sua experiência...",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=1000
    )
    
    estrelas = ui.TextInput(
        label="Quantas estrelas (0 a 5)?",
        placeholder="Digite um número de 0 a 5",
        required=True,
        max_length=1
    )
    
    def __init__(self, user_id: int, user_name: str, user_avatar: str):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        self.user_avatar = user_avatar
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            estrelas_num = int(self.estrelas.value)
            if estrelas_num < 0 or estrelas_num > 5:
                await interaction.response.send_message("❌ Digite um número entre 0 e 5!", ephemeral=True)
                return
            
            # Envia para canal de feedback
            canal_feedback = discord.utils.get(interaction.guild.channels, name=CONFIG["CANAL_FEEDBACK"])
            
            if canal_feedback:
                stars = get_star_emoji(estrelas_num)
                
                embed = discord.Embed(
                    title="🌟 Nova Avaliação",
                    color=discord.Color.gold(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="👤 Usuário", value=f"`{self.user_name}`", inline=True)
                embed.add_field(name="🛡️ Staff", value=f"`{self.staff.value}`", inline=True)
                embed.add_field(name="📝 Descrição", value=f"```{self.descricao.value}```", inline=False)
                embed.set_thumbnail(url=self.user_avatar)
                embed.set_footer(text=f"{stars} ({estrelas_num}/5)")
                
                await canal_feedback.send(embed=embed)
            
            # Salva no banco
            db.dados["feedbacks"].append({
                "user_id": self.user_id,
                "user_name": self.user_name,
                "staff": self.staff.value,
                "descricao": self.descricao.value,
                "estrelas": estrelas_num,
                "data": str(datetime.datetime.now())
            })
            db.salvar()
            
            await interaction.response.send_message("✅ Obrigado pela avaliação!", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Digite apenas números!", ephemeral=True)

class AvaliacaoView(ui.View):
    def __init__(self, user_id: int, user_name: str, user_avatar: str):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.user_name = user_name
        self.user_avatar = user_avatar
    
    @ui.button(label="🌟 Avaliar Atendimento", style=discord.ButtonStyle.green)
    async def avaliar(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Apenas quem foi atendido pode avaliar!", ephemeral=True)
            return
        
        await interaction.response.send_modal(AvaliacaoModal(self.user_id, self.user_name, self.user_avatar))

# ========================================
# VIEWS DOS TICKETS
# ========================================

class TicketView(ui.View):
    def __init__(self, user_id: int, produto: str, valor: float, user_name: str):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.produto = produto
        self.valor = valor
        self.user_name = user_name
        self.staff_responsavel = None
        self.status = "aguardando"
    
    @ui.button(label="🙋 Assumir Ticket", style=discord.ButtonStyle.blurple, custom_id="assumir_ticket")
    async def assumir(self, interaction: discord.Interaction, button: ui.Button):
        if not is_staff(interaction.user):
            await interaction.response.send_message("❌ Apenas staff pode assumir!", ephemeral=True)
            return
        
        if self.staff_responsavel:
            await interaction.response.send_message(f"❌ Este ticket já foi assumido por {self.staff_responsavel}!", ephemeral=True)
            return
        
        self.staff_responsavel = interaction.user.display_name
        
        # Atualiza embed com staff responsável
        embed = criar_embed(
            f"🛒 Ticket de Compra - {self.produto}",
            f"**Comprador:** <@{self.user_id}> (`{self.user_name}`)\n"
            f"**Produto:** {self.produto}\n"
            f"**Valor:** R${self.valor},00\n"
            f"**🛡️ Staff Responsável:** `{self.staff_responsavel}`\n\n"
            f"**💳 Formas de Pagamento:**\n"
            f"• **PIX:** `{CONFIG['PIX_CHAVE']}`\n"
            f"• **PayPal:** `{CONFIG['PAYPAL_EMAIL']}`\n\n"
            f"Após o pagamento, clique em **Confirmar Pagamento**!",
            discord.Color.gold(),
            CONFIG["IMAGENS"]["vip"]
        )
        
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message(f"✅ Você assumiu este ticket!", ephemeral=True)
    
    @ui.button(label="✅ Confirmar Pagamento", style=discord.ButtonStyle.green, custom_id="confirmar_pagamento")
    async def confirmar(self, interaction: discord.Interaction, button: ui.Button):
        if not is_staff(interaction.user):
            await interaction.response.send_message("❌ Apenas staff pode confirmar!", ephemeral=True)
            return
        
        self.status = "pago"
        member = interaction.guild.get_member(self.user_id)
        
        await interaction.response.send_message("✅ Pagamento confirmado! Finalizando...", ephemeral=True)
        
        # Mensagem no canal
        await interaction.channel.send(f"🎉 {member.mention} seu **{self.produto}** foi ativado!")
        
        # DM para usuário com avaliação
        if member:
            try:
                embed_dm = criar_embed(
                    "🎉 Compra Finalizada!",
                    f"**Produto:** {self.produto}\n"
                    f"**Valor:** R${self.valor},00\n"
                    f"**Staff:** `{self.staff_responsavel or 'N/A'}`\n\n"
                    f"Obrigado por comprar conosco! 💜\n"
                    f"Avalie seu atendimento abaixo:",
                    discord.Color.green(),
                    CONFIG["IMAGENS"]["vip"]
                )
                
                view_avaliacao = AvaliacaoView(self.user_id, self.user_name, member.avatar.url if member.avatar else None)
                await member.send(embed=embed_dm, view=view_avaliacao)
            except:
                pass
        
        # Log
        canal_logs = discord.utils.get(interaction.guild.channels, name="logs-vendas")
        if canal_logs:
            embed_log = criar_embed(
                "✅ Venda Confirmada",
                f"**Produto:** {self.produto}\n"
                f"**Valor:** R${self.valor},00\n"
                f"**Comprador:** <@{self.user_id}>\n"
                f"**Staff:** `{self.staff_responsavel}`",
                discord.Color.green()
            )
            await canal_logs.send(embed=embed_log)
        
        # Remove botões e adiciona fechar
        view_final = ui.View(timeout=None)
        btn_fechar = ui.Button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.gray)
        
        async def fechar_callback(interact):
            if not is_staff(interact.user):
                await interact.response.send_message("❌ Apenas staff!", ephemeral=True)
                return
            await interact.response.send_message("🔒 Fechando em 3s...")
            await asyncio.sleep(3)
            await interact.channel.delete()
        
        btn_fechar.callback = fechar_callback
        view_final.add_item(btn_fechar)
        
        await interaction.message.edit(view=view_final)
    
    @ui.button(label="❌ Cancelar", style=discord.ButtonStyle.red, custom_id="cancelar_compra")
    async def cancelar(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id and not is_staff(interaction.user):
            await interaction.response.send_message("❌ Você não pode cancelar!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Cancelando...", ephemeral=True)
        await asyncio.sleep(2)
        await interaction.channel.delete()

class ProdutoSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="💎 VIP Destaque",
                description=f"R${CONFIG['PRECO_VIP']} - Destaque suas mensagens + Divulgação Prioritária",
                value="vip_destaque",
                emoji="💎"
            )
        ]
        super().__init__(
            placeholder="🛒 Selecione o produto...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="select_produto_vip"
        )
    
    async def callback(self, interaction: discord.Interaction):
        produto = "💎 VIP Destaque"
        valor = CONFIG["PRECO_VIP"]
        
        embed = criar_embed(
            "🛒 Produto Selecionado",
            f"**Produto:** {produto}\n"
            f"**Valor:** R${valor},00\n\n"
            f"**Benefícios:**\n"
            f"• Destaque suas mensagens\n"
            f"• Divulgação prioritária\n"
            f"• Embed personalizado\n"
            f"• Ping em divulgações\n\n"
            f"Clique em **Continuar** para criar seu ticket!",
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
    
    @ui.button(label="Continuar Compra", style=discord.ButtonStyle.green, emoji="🛒")
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
        
        for cargo_nome in [CONFIG["CARGO_DONO"], CONFIG["CARGO_MOD"]]:
            cargo = get_cargo(guild, cargo_nome)
            if cargo:
                overwrites[cargo] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        canal = await guild.create_text_channel(
            name=canal_nome,
            category=categoria,
            overwrites=overwrites
        )
        
        embed = criar_embed(
            f"🛒 Ticket de Compra - {self.produto}",
            f"**Comprador:** <@{interaction.user.id}> (`{interaction.user.display_name}`)\n"
            f"**Produto:** {self.produto}\n"
            f"**Valor:** R${self.valor},00\n"
            f"**🛡️ Staff Responsável:** `Aguardando...`\n\n"
            f"**💳 Formas de Pagamento:**\n"
            f"• **PIX:** `{CONFIG['PIX_CHAVE']}`\n"
            f"• **PayPal:** `{CONFIG['PAYPAL_EMAIL']}`\n\n"
            f"Aguarde um staff assumir seu ticket!",
            discord.Color.gold(),
            CONFIG["IMAGENS"]["vip"]
        )
        
        view = TicketView(interaction.user.id, self.produto, self.valor, interaction.user.display_name)
        msg = await canal.send(f"🛒 {interaction.user.mention} bem-vindo!", embed=embed, view=view)
        await msg.pin()
        
        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)
        
        db.dados["tickets"][str(canal.id)] = {
            "user_id": interaction.user.id,
            "user_name": interaction.user.display_name,
            "produto": self.produto,
            "valor": self.valor,
            "status": "aberto",
            "data": str(datetime.datetime.now())
        }
        db.salvar()
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.red, emoji="❌")
    async def cancelar(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message("❌ Cancelado!", ephemeral=True)
        self.stop()

class PainelView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProdutoSelect())

# ========================================
# COMANDOS SLASH
# ========================================

@bot.tree.command(name="painel", description="🛒 Abre o painel de compras VIP")
async def painel(interaction: discord.Interaction):
    """Apenas Dono 👑 pode usar"""
    if not is_dono(interaction.user):
        await interaction.response.send_message("❌ Apenas o Dono pode usar este comando!", ephemeral=True)
        return
    
    embed = criar_embed(
        "🛒 TDZ SHOP - Loja VIP",
        "**Bem-vindo à loja oficial!**\n\n"
        "Aqui você pode adquirir o plano VIP para destacar suas divulgações.\n\n"
        "**💎 Produto Disponível:**\n"
        f"**VIP Destaque** - R${CONFIG['PRECO_VIP']},00\n"
        "• Destaque suas mensagens\n" 
        "• Divulgação prioritária\n"
        "• Embed personalizado com ping\n\n"
        "**👇 Selecione abaixo:**",
        discord.Color.purple(),
        CONFIG["IMAGENS"]["shop"]
    )
    
    view = PainelView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="regras", description="📕 Mostra as regras do servidor")
async def regras(interaction: discord.Interaction):
    embed = criar_embed(
        "📕 REGRAS DO SERVIDOR",
        "**Leia atentamente:**\n\n"
        "**1.** Proibido NSFW/18+\n"
        "**2.** Use os canais corretos\n"
        "**3.** Proibido spam\n"
        "**4.** Respeite todos\n"
        "**5.** Proibido phishing/scam\n"
        "**6.** Proibido rivais diretos\n"
        "**7.** Use `/divulgar` corretamente\n"
        "**8.** Proibido conteúdo ilegal\n\n"
        "**⚠️ Quebra = Ban!**",
        discord.Color.red(),
        CONFIG["IMAGENS"]["regras"]
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="infos", description="ℹ️ Informações do servidor")
async def infos(interaction: discord.Interaction):
    guild = interaction.guild
    embed = criar_embed(
        "ℹ️ INFORMAÇÕES",
        f"**Nome:** {guild.name}\n"
        f"**Membros:** {guild.member_count}\n"
        f"**Dono:** {guild.owner.mention if guild.owner else 'N/A'}\n\n"
        "**💎 VIP:** Destaque + Prioridade\n"
        "**👥 Staff:** Dono 👑 | Mod\n\n"
        f"Use `/painel` para comprar VIP!",
        discord.Color.blue(),
        CONFIG["IMAGENS"]["info"]
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="anunciar", description="📢 Cria um anúncio")
@app_commands.describe(
    canal="Canal de destino",
    tipo="Tipo do anúncio",
    titulo="Título",
    mensagem="Conteúdo"
)
@app_commands.choices(tipo=[
    app_commands.Choice(name="✅ Bom", value="bom"),
    app_commands.Choice(name="❌ Ruim", value="ruim")
])
@app_commands.checks.has_permissions(manage_messages=True)
async def anunciar(
    interaction: discord.Interaction,
    canal: discord.TextChannel,
    tipo: app_commands.Choice[str],
    titulo: str,
    mensagem: str
):
    await interaction.response.defer(ephemeral=True)
    
    cor = discord.Color.green() if tipo.value == "bom" else discord.Color.red()
    emoji = "✅" if tipo.value == "bom" else "❌"
    
    embed = criar_embed(
        f"{emoji} {titulo}",
        mensagem,
        cor,
        CONFIG["IMAGENS"]["anuncio_bom"] if tipo.value == "bom" else CONFIG["IMAGENS"]["anuncio_ruim"]
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    
    await canal.send(embed=embed)
    await interaction.followup.send(f"📢 Enviado em {canal.mention}!", ephemeral=True)

@bot.tree.command(name="divulgar", description="📢 Divulgação normal")
@app_commands.describe(
    tipo="Tipo",
    link="Link",
    descricao="Descrição"
)
@app_commands.choices(tipo=[
    app_commands.Choice(name="💬 Discord", value="servidor"),
    app_commands.Choice(name="📹 YouTube", value="youtube"),
    app_commands.Choice(name="🎬 Twitch", value="twitch"),
    app_commands.Choice(name="📱 Social", value="social"),
    app_commands.Choice(name="🖼️ Arte", value="arte"),
    app_commands.Choice(name="🛠️ Serviço", value="servico")
])
async def divulgar(
    interaction: discord.Interaction,
    tipo: app_commands.Choice[str],
    link: str,
    descricao: str
):
    await interaction.response.defer(ephemeral=True)
    
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
        await interaction.followup.send("❌ Canal não encontrado!", ephemeral=True)
        return
    
    embed = criar_embed(
        f"📢 {tipo.name}",
        f"{descricao}\n\n{link}",
        discord.Color.green()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    
    msg = await canal.send(content=f"📢 Divulgação de {interaction.user.mention}:", embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")
    
    await interaction.followup.send(f"✅ Divulgado em {canal.mention}!", ephemeral=True)

@bot.tree.command(name="divulgavip", description="💎 Divulgação VIP com embed colorido")
@app_commands.describe(
    texto="Texto da divulgação",
    cor="Cor do embed"
)
@app_commands.choices(cor=[
    app_commands.Choice(name="🔵 Azul", value="0x3498db"),
    app_commands.Choice(name="🔴 Vermelho", value="0xe74c3c"),
    app_commands.Choice(name="🟢 Verde", value="0x2ecc71"),
    app_commands.Choice(name="🟣 Roxo", value="0x9b59b6"),
    app_commands.Choice(name="🟡 Amarelo", value="0xf1c40f"),
    app_commands.Choice(name="🟠 Laranja", value="0xe67e22"),
    app_commands.Choice(name="⚫ Preto", value="0x2c3e50"),
    app_commands.Choice(name="⚪ Branco", value="0xecf0f1")
])
async def divulgavip(
    interaction: discord.Interaction,
    texto: str,
    cor: app_commands.Choice[str]
):
    """Apenas para VIPs (verificação manual por enquanto)"""
    await interaction.response.defer(ephemeral=True)
    
    cor_int = int(cor.value, 16)
    
    embed = discord.Embed(
        title="💎 DIVULGAÇÃO VIP",
        description=texto,
        color=cor_int,
        timestamp=datetime.datetime.now()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    embed.set_footer(text="⭐ VIP Destaque")
    
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
    
    await interaction.followup.send(f"✅ Divulgação VIP enviada em {enviados} canais!", ephemeral=True)

@bot.tree.command(name="say", description="🤖 Faz o bot falar")
@app_commands.describe(mensagem="Texto", canal="Canal (opcional)")
@app_commands.checks.has_permissions(administrator=True)
async def say(
    interaction: discord.Interaction,
    mensagem: str,
    canal: Optional[discord.TextChannel] = None
):
    await interaction.response.defer(ephemeral=True)
    destino = canal or interaction.channel
    await destino.send(mensagem)
    await interaction.followup.send("✅ Enviado!", ephemeral=True)

@bot.tree.command(name="embed", description="📋 Cria embed")
@app_commands.checks.has_permissions(administrator=True)
async def embed_cmd(
    interaction: discord.Interaction,
    titulo: str,
    descricao: str,
    cor: Optional[str] = "azul"
):
    await interaction.response.defer(ephemeral=True)
    
    cores = {
        "azul": discord.Color.blue(),
        "vermelho": discord.Color.red(),
        "verde": discord.Color.green(),
        "roxo": discord.Color.purple()
    }
    
    embed = criar_embed(titulo, descricao, cores.get(cor, discord.Color.blue()))
    await interaction.channel.send(embed=embed)
    await interaction.followup.send("✅ Embed enviado!", ephemeral=True)

@bot.tree.command(name="sorteio", description="🎉 Sorteio")
@app_commands.describe(premio="Prêmio", duracao="Minutos", vencedores="Qtd")
@app_commands.checks.has_permissions(manage_messages=True)
async def sorteio(
    interaction: discord.Interaction,
    premio: str,
    duracao: int,
    vencedores: int = 1
):
    await interaction.response.defer(ephemeral=True)
    
    embed = criar_embed(
        "🎉 SORTEIO!",
        f"**Prêmio:** {premio}\n**Duração:** {duracao}min\n**Vencedores:** {vencedores}\n\nReaja com 🎉!",
        discord.Color.gold(),
        CONFIG["IMAGENS"]["giveaway"]
    )
    
    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("🎉")
    
    await interaction.followup.send("🎉 Sorteio iniciado!", ephemeral=True)
    
    await asyncio.sleep(duracao * 60)
    
    msg_atual = await interaction.channel.fetch_message(msg.id)
    reacao = discord.utils.get(msg_atual.reactions, emoji="🎉")
    
    if reacao:
        users = [u async for u in reacao.users() if not u.bot]
        if len(users) >= vencedores:
            ganhadores = random.sample(users, min(vencedores, len(users)))
            mencoes = ", ".join([g.mention for g in ganhadores])
            
            embed_final = criar_embed(
                "🎉 FIM!",
                f"**Ganhadores:** {mencoes}\n**Prêmio:** {premio}",
                discord.Color.green(),
                CONFIG["IMAGENS"]["giveaway"]
            )
            await msg.edit(embed=embed_final)
            await interaction.channel.send(f"🎉 {mencoes} ganhou: **{premio}**!")

@bot.tree.command(name="fechar_ticket", description="🔒 Fecha ticket")
@app_commands.checks.has_permissions(manage_channels=True)
async def fechar_ticket(interaction: discord.Interaction):
    if "compra-" not in interaction.channel.name:
        await interaction.response.send_message("❌ Não é um ticket!", ephemeral=True)
        return
    
    await interaction.response.send_message("🔒 Fechando em 3s...")
    await asyncio.sleep(3)
    await interaction.channel.delete()

@bot.tree.command(name="perfil", description="👤 Perfil")
async def perfil(interaction: discord.Interaction, membro: Optional[discord.Member] = None):
    alvo = membro or interaction.user
    uid = str(alvo.id)
    stats = db.dados["usuarios"].get(uid, {"divulgacoes": 0})
    
    embed = criar_embed(
        f"👤 {alvo.display_name}",
        f"**Divulgações:** {stats.get('divulgacoes', 0)}",
        discord.Color.purple(),
        thumbnail=alvo.avatar.url if alvo.avatar else None
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="🏓 Ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

@bot.tree.command(name="ajuda", description="❓ Ajuda")
async def ajuda(interaction: discord.Interaction):
    embed = criar_embed(
        "❓ AJUDA",
        "**📢 Divulgação:**\n`/divulgar` - Normal\n`/divulgavip` - VIP (cor+embed)\n\n"
        "**🛒 Loja:**\n`/painel` - Comprar VIP (Dono)\n\n"
        "**📢 Admin:**\n`/anunciar` `/say` `/embed` `/sorteio`\n\n"
        "**🔧 Util:**\n`/regras` `/infos` `/perfil` `/ping`",
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
        embed = criar_embed(
            "👋 Saída",
            f"{member.display_name} saiu.\n**Membros:** {member.guild.member_count}",
            discord.Color.red()
        )
        await canal.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Sem permissão!")

# ========================================
# INICIAR
# ========================================

if __name__ == "__main__":
    print("🚀 Iniciando TDZ Bot...")
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN não encontrado!")
    else:
        bot.run(token)
