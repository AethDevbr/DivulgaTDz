"""
========================================
TDZ DIVULGAÇÕES - BOT COMPLETO (ATUALIZADO)
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
    "DONO_ID": 1327679436128129159,
    
    # Cargos
    "CARGO_DONO": "Dono 👑",
    "CARGO_MOD": "Mod",
    "CARGO_VIP": "ᴅɪᴠᴜʟɢᴀᴅᴏʀ ᴠɪᴘ 💎",
    
    # Categorias
    "CATEGORIA_TICKETS": "🛒 Compras",
    
    # Canais
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
    "CANAL_COMPRAS_REALIZADAS_ID": 1486065492538953888,  # NOVO - ID do canal de compras
    
    # Pagamento
    "PIX_CHAVE": "999049883",
    "EMOJI_PIX": "<:emoji_2:1486128219504513066>",
    "EMOJI_CARRINHO": "<:emoji_3:1486164433679155402>",  # NOVO - Emoji carrinho
    
    # Preços
    "PRECOS": {
        "destacar_mensagem": 15,
        "vip": 30,
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
        "welcome": "https://i.imgur.com/DbgjpnR.png",
        "compra_realizada": "https://i.imgur.com/1oyHhIM.png"  # NOVO
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

def criar_embed(titulo: str, descricao: str, cor: discord.Color, imagem: str = None, thumbnail: str = None):
    embed = discord.Embed(title=titulo, description=descricao, color=cor, timestamp=datetime.datetime.now())
    embed.set_footer(text="TDZ Divulgações © 2026")
    if imagem:
        embed.set_image(url=imagem)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    return embed

def get_star_emoji(qtd: int) -> str:
    # CORRIGIDO: Garante que qtd está entre 0 e 5
    qtd = max(0, min(5, qtd))
    return "★" * qtd + "☆" * (5 - qtd)

# ========================================
# MODAL AVALIAÇÃO (CORRIGIDO)
# ========================================

class AvaliacaoModal(ui.Modal, title="🌟 Avaliar Atendimento"):
    staff = ui.TextInput(
        label="Staff Responsável", 
        placeholder="Quem te atendeu?", 
        required=True, 
        max_length=100
    )
    descricao = ui.TextInput(
        label="Como foi o atendimento?", 
        placeholder="Sua experiência...", 
        required=True, 
        style=discord.TextStyle.paragraph, 
        max_length=1000
    )
    estrelas = ui.TextInput(
        label="Estrelas (1 a 5)", 
        placeholder="Digite 1, 2, 3, 4 ou 5", 
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
            # CORRIGIDO: Validação mais robusta
            estrelas_str = self.estrelas.value.strip()
            
            if not estrelas_str.isdigit():
                await interaction.response.send_message("❌ Digite apenas números de 1 a 5!", ephemeral=True)
                return
            
            estrelas_num = int(estrelas_str)
            
            if estrelas_num < 1 or estrelas_num > 5:
                await interaction.response.send_message("❌ Digite um número entre 1 e 5!", ephemeral=True)
                return
            
            # Buscar canal de feedback
            canal = discord.utils.get(interaction.guild.channels, name=CONFIG["CANAL_FEEDBACK"])
            
            if not canal:
                await interaction.response.send_message("❌ Canal de feedback não encontrado!", ephemeral=True)
                return
            
            # Criar embed de avaliação
            stars = get_star_emoji(estrelas_num)
            
            embed = discord.Embed(
                title="🌟 Nova Avaliação Recebida",
                color=discord.Color.gold(),
                timestamp=datetime.datetime.now()
            )
            
            # CORRIGIDO: Usando ` em todos os campos conforme solicitado
            embed.add_field(name="👤 Usuário", value=f"`{self.user_name}`", inline=True)
            embed.add_field(name="🛡️ Staff", value=f"`{self.staff.value}`", inline=True)
            embed.add_field(name="⭐ Nota", value=f"`{estrelas_num}/5`", inline=True)
            embed.add_field(name="📝 Descrição", value=f"```{self.descricao.value}```", inline=False)
            
            if self.user_avatar:
                embed.set_thumbnail(url=self.user_avatar)
            
            embed.set_footer(text=f"Avaliação #{len(db.dados['feedbacks']) + 1}")
            
            await canal.send(embed=embed)
            
            # Salvar no banco de dados
            db.dados["feedbacks"].append({
                "user_id": self.user_id,
                "user_name": self.user_name,
                "staff": self.staff.value,
                "estrelas": estrelas_num,
                "descricao": self.descricao.value,
                "data": datetime.datetime.now().isoformat()
            })
            db.salvar()
            
            await interaction.response.send_message("✅ Obrigado pela sua avaliação!", ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Erro: Digite apenas números!", ephemeral=True)
        except Exception as e:
            print(f"Erro no modal: {e}")
            await interaction.response.send_message(f"❌ Erro ao enviar avaliação: {str(e)}", ephemeral=True)

class AvaliacaoView(ui.View):
    def __init__(self, user_id: int, user_name: str, user_avatar: str):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.user_name = user_name
        self.user_avatar = user_avatar
    
    @ui.button(label="🌟 Avaliar Atendimento", style=discord.ButtonStyle.green)
    async def avaliar(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Apenas você pode avaliar!", ephemeral=True)
            return
        await interaction.response.send_modal(AvaliacaoModal(self.user_id, self.user_name, self.user_avatar))

# ========================================
# TICKET VIEW (ATUALIZADO COM COMPRAS REALIZADAS)
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
            await interaction.response.send_message(f"❌ Já assumido por `{self.staff_responsavel}`!", ephemeral=True)
            return
        
        self.staff_responsavel = interaction.user.display_name
        
        embed = criar_embed(
            f"🛒 Ticket - {self.produto}",
            f"**Comprador:** <@{self.user_id}> (`{self.user_name}`)" + chr(10) +
            f"**Produto:** `{self.produto}`" + chr(10) +
            f"**Valor:** `R${self.valor},00`" + chr(10) +
            f"**🛡️ Staff:** `{self.staff_responsavel}`" + chr(10) + chr(10) +
            f"{CONFIG['EMOJI_PIX']} **PIX:** `{CONFIG['PIX_CHAVE']}`",
            discord.Color.gold(),
            CONFIG["IMAGENS"]["vip"]
        )
        
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.send_message("✅ Ticket assumido!", ephemeral=True)
    
    @ui.button(label="✅ Confirmar Pagamento", style=discord.ButtonStyle.green)
    async def confirmar(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != CONFIG["DONO_ID"]:
            await interaction.response.send_message(f"❌ Apenas <@{CONFIG['DONO_ID']}> pode confirmar!", ephemeral=True)
            return
        
        member = interaction.guild.get_member(self.user_id)
        if not member:
            await interaction.response.send_message("❌ Usuário não encontrado!", ephemeral=True)
            return
        
        cargo_adicionado = False
        if "VIP" in self.produto:
            cargo_vip = get_cargo(interaction.guild, CONFIG["CARGO_VIP"])
            if cargo_vip:
                try:
                    await member.add_roles(cargo_vip)
                    cargo_adicionado = True
                except Exception as e:
                    print(f"Erro ao adicionar cargo: {e}")
        
        await interaction.response.send_message("✅ Pagamento confirmado! Processando...", ephemeral=True)
        
        # Mensagem no ticket
        msg_cargo = ""
        if cargo_adicionado:
            msg_cargo = chr(10) + "🎉 **Seu cargo VIP foi ativado automaticamente!**"
        
        await interaction.channel.send(
            f"🎉 {member.mention} **Pagamento Confirmado!**" + chr(10) + chr(10) +
            f"**Produto:** `{self.produto}`" + chr(10) +
            f"**Valor:** `R${self.valor},00`" + chr(10) +
            f"**Status:** ✅ Aprovado" + msg_cargo + chr(10) + chr(10) +
            "Obrigado pela compra! 💜"
        )
        
        # ========================================
        # NOVO: ENVIAR EMBED NO CANAL DE COMPRAS REALIZADAS
        # ========================================
        try:
            canal_compras = bot.get_channel(CONFIG["CANAL_COMPRAS_REALIZADAS_ID"])
            
            if canal_compras:
                # Criar embed de compra realizada
                embed_compra = discord.Embed(
                    title=f"{CONFIG['EMOJI_CARRINHO']} Compra Realizada",
                    description=f"Uma nova compra foi aprovada!",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
                
                # Campos com ` conforme solicitado
                embed_compra.add_field(name="👤 Usuário", value=f"`{member.display_name}`", inline=True)
                embed_compra.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
                embed_compra.add_field(name="📦 Produto", value=f"`{self.produto}`", inline=True)
                embed_compra.add_field(name="💰 Valor", value=f"`R${self.valor},00`", inline=True)
                embed_compra.add_field(name="📊 Quantidade", value="`1`", inline=True)  # Quantidade fixa em 1
                embed_compra.add_field(name="🛡️ Atendente", value=f"`{self.staff_responsavel or 'N/A'}`", inline=True)
                
                # Avatar no canto (thumbnail)
                if member.avatar:
                    embed_compra.set_thumbnail(url=member.avatar.url)
                else:
                    embed_compra.set_thumbnail(url=member.default_avatar.url)
                
                # Imagem embaixo
                embed_compra.set_image(url=CONFIG["IMAGENS"]["compra_realizada"])
                
                # Footer com #
                embed_compra.set_footer(text=f"#{len(db.dados['vendas']) + 1}")
                
                await canal_compras.send(embed=embed_compra)
                
                # Salvar venda no banco de dados
                db.dados["vendas"].append({
                    "user_id": member.id,
                    "user_name": member.display_name,
                    "produto": self.produto,
                    "valor": self.valor,
                    "quantidade": 1,
                    "staff": self.staff_responsavel,
                    "data": datetime.datetime.now().isoformat()
                })
                db.salvar()
                
        except Exception as e:
            print(f"Erro ao enviar para canal de compras: {e}")
            await interaction.channel.send(f"⚠️ Erro ao registrar compra no canal: {e}")
        
        # DM para o comprador
        msg_vip = ""
        if cargo_adicionado:
            msg_vip = f"🎊 **Seu cargo VIP já está ativo!** Use `/divulgarvip` para divulgar com estilo!" + chr(10) + chr(10)
        
        try:
            data_atual = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            staff_nome = self.staff_responsavel or 'N/A'
            
            embed_dm = criar_embed(
                "🎉 Compra Finalizada - TDZ Divulgações",
                f"Olá **{member.display_name}**!" + chr(10) + chr(10) +
                "✅ **Pagamento Confirmado**" + chr(10) + chr(10) +
                f"**📦 Produto:** `{self.produto}`" + chr(10) +
                f"**💰 Valor:** `R${self.valor},00`" + chr(10) +
                f"**🛡️ Atendente:** `{staff_nome}`" + chr(10) +
                f"**📅 Data:** `{data_atual}`" + chr(10) + chr(10) +
                msg_vip +
                "💜 Obrigado por comprar conosco!" + chr(10) +
                "🌟 Avalie seu atendimento abaixo:",
                discord.Color.green(),
                CONFIG["IMAGENS"]["vip"]
            )
            
            view_avaliacao = AvaliacaoView(self.user_id, self.user_name, member.avatar.url if member.avatar else None)
            await member.send(embed=embed_dm, view=view_avaliacao)
        except Exception as e:
            print(f"Erro ao enviar DM: {e}")
            await interaction.channel.send(f"⚠️ Não consegui enviar DM para {member.mention}.")
        
        # Botão fechar
        view_final = ui.View(timeout=None)
        btn_fechar = ui.Button(label="🔒 Fechar Ticket", style=discord.ButtonStyle.gray)
        
        async def fechar_callback(interact):
            if interact.user.id != CONFIG["DONO_ID"]:
                await interact.response.send_message("❌ Apenas o Dono!", ephemeral=True)
                return
            await interact.response.send_message("🔒 Fechando ticket...")
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
        
        await interaction.response.send_message("❌ Cancelando ticket...", ephemeral=True)
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
        super().__init__(placeholder="🛒 Selecione um produto...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        produtos = {
            "destacar_mensagem": ("⭐ Destacar Mensagem", CONFIG["PRECOS"]["destacar_mensagem"]),
            "vip": ("💎 VIP", CONFIG["PRECOS"]["vip"]),
            "divulgacao_global": ("🚀 Divulgação Global", CONFIG["PRECOS"]["divulgacao_global"])
        }
        
        produto, valor = produtos[self.values[0]]
        
        embed = criar_embed(
            "🛒 Produto Selecionado",
            f"**{produto}** - `R${valor},00`" + chr(10) + chr(10) + "Clique em **Continuar** para prosseguir!",
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
        
        canal_nome = f"🛒・compra-{interaction.user.name.lower().replace(' ', '-')[:100]}"
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        dono = guild.get_member(CONFIG["DONO_ID"])
        if dono:
            overwrites[dono] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        canal = await guild.create_text_channel(name=canal_nome, category=categoria, overwrites=overwrites)
        
        embed = criar_embed(
            f"🛒 Ticket - {self.produto}",
            f"**Comprador:** <@{interaction.user.id}> (`{interaction.user.display_name}`)" + chr(10) +
            f"**Produto:** `{self.produto}`" + chr(10) +
            f"**Valor:** `R${self.valor},00`" + chr(10) +
            "**🛡️ Staff:** `Aguardando...`" + chr(10) + chr(10) +
            f"{CONFIG['EMOJI_PIX']} **PIX:** `{CONFIG['PIX_CHAVE']}`",
            discord.Color.gold(),
            CONFIG["IMAGENS"]["vip"]
        )
        
        view = TicketView(interaction.user.id, self.produto, self.valor, interaction.user.display_name)
        msg = await canal.send(f"🛒 {interaction.user.mention} bem-vindo ao seu ticket!", embed=embed, view=view)
        await msg.pin()
        
        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)
    
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
        "**Planos Disponíveis:**" + chr(10) + chr(10) +
        f"⭐ **Destacar Mensagem** - `R${CONFIG['PRECOS']['destacar_mensagem']},00`" + chr(10) +
        f"💎 **VIP** - `R${CONFIG['PRECOS']['vip']},00` (Acesso /divulgarvip)" + chr(10) +
        f"🚀 **Divulgação Global** - `R${CONFIG['PRECOS']['divulgacao_global']},00`" + chr(10) + chr(10) +
        "**👇 Selecione um produto abaixo:**",
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
        texto + chr(10) + chr(10) + link,
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
    if not is_vip(interaction.user):
        await interaction.response.send_message(
            f"❌ Você precisa do cargo **{CONFIG['CARGO_VIP']}**!" + chr(10) +
            "Compre no `/painel`!", 
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
        await interaction.response.send_message(f"❌ Erro: {e}", ephemeral=True)

@bot.tree.command(name="regras", description="📕 Regras")
async def regras(interaction: discord.Interaction):
    embed = criar_embed(
        "📕 REGRAS TDZ DIVULGAÇÕES",
        "**1.** Proibido conteúdo NSFW/18+" + chr(10) +
        "**2.** Use os canais corretos para divulgar" + chr(10) +
        "**3.** Proibido spam ou flood" + chr(10) +
        "**4.** Respeite todos os membros" + chr(10) +
        "**5.** Proibido links de phishing/scam" + chr(10) +
        "**6.** Proibido divulgar servidores rivais" + chr(10) +
        "**7.** Use `/divulgar` para divulgar corretamente" + chr(10) +
        "**8.** Proibido qualquer conteúdo ilegal" + chr(10) + chr(10) +
        "**⚠️ Quebra de regras = Banimento permanente!**" + chr(10) + chr(10) +
        "**💡 Dica:** Leia as informações em `/infos`",
        discord.Color.red(),
        CONFIG["IMAGENS"]["regras"]
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="infos", description="ℹ️ Informações do servidor")
async def infos(interaction: discord.Interaction):
    guild = interaction.guild
    dono = guild.get_member(CONFIG["DONO_ID"])
    
    embed = discord.Embed(
        title="ℹ️ INFORMAÇÕES - TDZ DIVULGAÇÕES",
        description="**Servidor oficial de divulgações e parcerias**",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(
        name="👑 Dono",
        value=f"**@slknumcompensa0743**" + chr(10) + f"<@{CONFIG['DONO_ID']}>",
        inline=False
    )
    
    embed.add_field(
        name="📊 Estatísticas",
        value=f"**Membros:** `{guild.member_count}`" + chr(10) + f"**Criado em:** `{guild.created_at.strftime('%d/%m/%Y')}`",
        inline=True
    )
    
    embed.add_field(
        name="🎯 Objetivo",
        value="Divulgar servidores Discord, canais YouTube, lives Twitch, artes digitais e serviços de forma organizada e profissional.",
        inline=False
    )
    
    embed.add_field(
        name="💎 Planos VIP",
        value=f"⭐ **Destacar Mensagem** - `R${CONFIG['PRECOS']['destacar_mensagem']},00`" + chr(10) +
              f"💎 **VIP** - `R${CONFIG['PRECOS']['vip']},00`" + chr(10) +
              f"🚀 **Divulgação Global** - `R${CONFIG['PRECOS']['divulgacao_global']},00`",
        inline=False
    )
    
    embed.add_field(
        name="📱 Canais de Divulgação",
        value="💬 Servidores Discord" + chr(10) + "📹 Canais YouTube" + chr(10) + "🎬 Lives Twitch" + chr(10) + "🖼️ Artes Digitais" + chr(10) + "🛠️ Serviços/Ofertas",
        inline=True
    )
    
    embed.add_field(
        name="💳 Pagamento",
        value=f"{CONFIG['EMOJI_PIX']} **PIX:** `{CONFIG['PIX_CHAVE']}`",
        inline=True
    )
    
    embed.add_field(
        name="🔗 Links Úteis",
        value="Use `/painel` para comprar VIP" + chr(10) + "Use `/divulgar` para divulgar" + chr(10) + "Use `/ajuda` para ver todos os comandos",
        inline=False
    )
    
    embed.set_image(url=CONFIG["IMAGENS"]["info"])
    embed.set_footer(text="TDZ Divulgações © 2026 | Criado por @slknumcompensa0743")
    
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
    embed = criar_embed(
        "🎉 SORTEIO!",
        f"**Prêmio:** `{premio}`" + chr(10) + f"**Duração:** `{duracao}min`" + chr(10) + f"**Vencedores:** `{vencedores}`" + chr(10) + chr(10) + "Reaja com 🎉!",
        discord.Color.gold(),
        CONFIG["IMAGENS"]["giveaway"]
    )
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
    
    vip_status = "💎 Sim" if is_vip(alvo) else "❌ Não"
    
    embed = criar_embed(
        f"👤 Perfil de {alvo.display_name}",
        f"**📢 Divulgações:** `{stats.get('divulgacoes', 0)}`" + chr(10) +
        f"**💎 VIP:** `{vip_status}`" + chr(10) +
        f"**📅 Entrou:** `{(alvo.joined_at.strftime('%d/%m/%Y') if alvo.joined_at else 'N/A')}`",
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
        "❓ CENTRAL DE AJUDA",
        "**📢 Divulgação:**" + chr(10) +
        "`/divulgar` - Divulgação normal (escolhe canal)" + chr(10) +
        "`/divulgarvip` - Divulgação colorida (apenas VIP)" + chr(10) + chr(10) +
        "**🛒 Loja:**" + chr(10) +
        "`/painel` - Comprar planos (Dono only)" + chr(10) + chr(10) +
        "**📢 Admin:**" + chr(10) +
        "`/anunciar` - Criar anúncio" + chr(10) +
        "`/say` - Bot fala algo" + chr(10) +
        "`/sorteio` - Iniciar sorteio" + chr(10) + chr(10) +
        "**ℹ️ Informações:**" + chr(10) +
        "`/regras` - Regras do servidor" + chr(10) +
        "`/infos` - Informações completas" + chr(10) +
        "`/perfil` - Seu perfil" + chr(10) +
        "`/ping` - Status do bot" + chr(10) + chr(10) +
        "**💡 Dica:** Compre VIP para usar `/divulgarvip`!",
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
        embed = criar_embed("👋 Saída", f"{member.display_name} saiu." + chr(10) + f"**Membros:** `{member.guild.member_count}`", discord.Color.red())
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
