"""Dunder Mifflin CLI Interface"""

import os
import sys
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from dundie.core import add, read, load, transfer, get_balance, get_statement
from dundie.utils.auth import (
    authenticate,
    check_admin_role,
    get_current_user,
    login_required,
    admin_required,
    require_password_verification
)
from dundie.utils.session import save_session, load_session, clear_session, get_session_email
from dundie.utils.user import set_initial_password

# Carrega variáveis de ambiente
load_dotenv()

console = Console()

# Configuração do logger
from dundie.utils.log import get_logger
log = get_logger()


@click.group()
@click.version_option()
def main():
    """Dunder Mifflin CLI - Sistema de Pontuação de Funcionários"""
    pass


@main.command()
@click.argument("filepath", required=False)
def load_cmd(filepath: Optional[str] = None):
    """Carrega dados de funcionários a partir de um arquivo CSV
    
    Se FILEPATH não for fornecido, usa o arquivo padrão em assets/people.csv
    """
    try:
        result = load(filepath)
        
        if result:
            table = Table(title="✅ Funcionários Carregados")
            table.add_column("Nome", style="cyan", no_wrap=True)
            table.add_column("Departamento", style="green")
            table.add_column("Cargo", style="yellow")
            table.add_column("Email", style="blue")
            table.add_column("Moeda", style="magenta")
            table.add_column("Status", style="white")
            
            for person in result:
                status = "✅ Novo" if person.get("created", False) else "🔄 Existente"
                table.add_row(
                    person["name"],
                    person["dept"],
                    person["role"],
                    person["email"],
                    person["currency"],
                    status
                )
            
            console.print(table)
            log.info(f"Loaded {len(result)} people")
        else:
            console.print("[yellow]Nenhum dado carregado[/yellow]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Arquivo não encontrado: {filepath}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Erro ao carregar dados: {e}[/red]")
        log.error(f"Error loading data: {e}")
        sys.exit(1)


@main.command()
@click.option("--dept", help="Filtrar por departamento")
@click.option("--email", help="Filtrar por email")
@login_required
def show(dept: Optional[str] = None, email: Optional[str] = None, current_user=None):
    """Mostra informações dos funcionários com pontos acumulados"""
    
    # Verifica permissões para visualizar dados
    is_admin, role, name = check_admin_role(current_user.email)
    
    if not is_admin:
        # Se não for admin, só pode ver seus próprios dados
        if email and email != current_user.email:
            console.print("[red]❌ Você só pode visualizar seus próprios dados![/red]")
            return
        if dept:
            console.print("[red]❌ Você só pode visualizar seus próprios dados![/red]")
            return
        # Força a busca apenas pelo email do usuário atual
        email = current_user.email
        dept = None
    
    try:
        result = read(dept=dept, email=email)
        
        if not result:
            console.print("[yellow]Nenhum funcionário encontrado com os filtros fornecidos[/yellow]")
            return
        
        # Criar tabela
        table = Table(title="📊 Relatório de Pontos")
        table.add_column("Nome", style="cyan", no_wrap=True)
        table.add_column("Departamento", style="green")
        table.add_column("Cargo", style="yellow")
        table.add_column("Email", style="blue")
        table.add_column("Moeda", style="magenta")
        table.add_column("Saldo", style="bold white", justify="right")
        table.add_column("💰 USD", style="bold green", justify="right")
        table.add_column("Último Movimento", style="dim")
        
        for person in result:
            table.add_row(
                person["name"],
                person["dept"],
                person["role"],
                person["email"],
                person["currency"],
                str(person["balance"]),
                f"${person['total_usd']:.2f}",
                person["last_movement"] or "-"
            )
        
        console.print(table)
        
        # Mostrar total de funcionários
        total_employees = len(result)
        total_points = sum(p["balance"] for p in result)
        console.print(f"\n[dim]Total de funcionários: {total_employees}[/dim]")
        console.print(f"[dim]Total de pontos: {total_points}[/dim]")
        
        # Informações de permissão
        if is_admin:
            console.print(f"\n[green]👑 Acessando como: {role} - {name}[/green]")
        else:
            console.print(f"\n[blue]👤 Acessando como: {name} ({current_user.email})[/blue]")
        
        log.info(f"Show command executed by {current_user.email}")
        
    except Exception as e:
        console.print(f"[red]❌ Erro ao mostrar dados: {e}[/red]")
        log.error(f"Error in show command: {e}")
        sys.exit(1)


@main.command()
@click.option("--email", required=True, help="Email do usuário")
@click.option("--value", required=True, type=int, help="Quantidade de pontos")
@login_required
@admin_required
def add_cmd(email: str, value: int, current_user=None):
    """Adiciona pontos a um funcionário (apenas CEO/Manager)"""
    
    # Verificação extra de segurança
    is_admin, role, name = check_admin_role(current_user.email)
    if not is_admin:
        console.print("[red]❌ Apenas CEO e Managers podem adicionar pontos![/red]")
        return
    
    try:
        # Mostrar informações do usuário que está adicionando
        console.print(f"[dim]👑 Adicionando por: {name} ({role})[/dim]")
        console.print(f"[dim]📧 Para: {email}[/dim]")
        console.print(f"[dim]➕ Valor: +{value} pontos[/dim]")
        
        add(value, email=email)
        
        # Buscar saldo atualizado
        balance_info = get_balance(email)
        if balance_info:
            console.print(f"[green]✅ {value} pontos adicionados com sucesso![/green]")
            console.print(f"[cyan]Novo saldo de {balance_info['name']}: {balance_info['balance']} {balance_info['currency']}[/cyan]")
        else:
            console.print(f"[green]✅ {value} pontos adicionados com sucesso![/green]")
        
        log.info(f"Added {value} points to {email} by {current_user.email}")
        
    except RuntimeError as e:
        console.print(f"[red]❌ Usuário não encontrado: {email}[/red]")
        log.error(f"User not found: {email}")
    except Exception as e:
        console.print(f"[red]❌ Erro ao adicionar pontos: {e}[/red]")
        log.error(f"Error adding points: {e}")
        sys.exit(1)


@main.command()
@click.option("--email", required=True, help="Email do usuário")
@click.option("--value", required=True, type=int, help="Quantidade de pontos a remover")
@login_required
@admin_required
@require_password_verification
def remove(email: str, value: int, current_user=None):
    """Remove pontos de um funcionário (apenas CEO/Manager)"""
    
    # Verificação extra de segurança
    is_admin, role, name = check_admin_role(current_user.email)
    if not is_admin:
        console.print("[red]❌ Apenas CEO e Managers podem remover pontos![/red]")
        return
    
    if value <= 0:
        console.print("[red]❌ O valor deve ser positivo![/red]")
        return
    
    try:
        # Verificar saldo atual do usuário
        balance_info = get_balance(email)
        if not balance_info:
            console.print(f"[red]❌ Usuário não encontrado: {email}[/red]")
            return
        
        current_balance = balance_info["balance"]
        if current_balance < value:
            console.print(f"[red]❌ Saldo insuficiente! {balance_info['name']} tem apenas {current_balance} pontos.[/red]")
            return
        
        # Mostrar informações
        console.print(f"[dim]👑 Removendo por: {name} ({role})[/dim]")
        console.print(f"[dim]📧 De: {email}[/dim]")
        console.print(f"[dim]➖ Valor: -{value} pontos[/dim]")
        console.print(f"[dim]📊 Saldo atual: {current_balance} pontos[/dim]")
        
        # Remover pontos (adicionar valor negativo)
        add(-value, email=email)
        
        # Buscar saldo atualizado
        new_balance_info = get_balance(email)
        if new_balance_info:
            console.print(f"[green]✅ {value} pontos removidos com sucesso![/green]")
            console.print(f"[cyan]Novo saldo de {new_balance_info['name']}: {new_balance_info['balance']} {new_balance_info['currency']}[/cyan]")
        else:
            console.print(f"[green]✅ {value} pontos removidos com sucesso![/green]")
        
        log.info(f"Removed {value} points from {email} by {current_user.email}")
        
    except RuntimeError as e:
        console.print(f"[red]❌ Usuário não encontrado: {email}[/red]")
        log.error(f"User not found: {email}")
    except Exception as e:
        console.print(f"[red]❌ Erro ao remover pontos: {e}[/red]")
        log.error(f"Error removing points: {e}")
        sys.exit(1)


@main.command()
@click.option("--email", required=True, help="Email do usuário para transferência")
@click.option("--value", required=True, type=int, help="Quantidade de pontos")
@login_required
@require_password_verification
def transfer_cmd(email: str, value: int, current_user=None):
    """Transfere pontos para outro usuário"""
    
    if value <= 0:
        console.print("[red]❌ O valor deve ser positivo![/red]")
        return
    
    # Não pode transferir para si mesmo
    if email == current_user.email:
        console.print("[red]❌ Não é possível transferir pontos para si mesmo![/red]")
        return
    
    # Verificar saldo do usuário atual
    balance_info = get_balance(current_user.email)
    if not balance_info or balance_info["balance"] < value:
        console.print(f"[red]❌ Saldo insuficiente! Você tem {balance_info['balance'] if balance_info else 0} pontos.[/red]")
        return
    
    try:
        # Mostrar informações
        console.print(f"[dim]👤 Transferindo de: {current_user.name}[/dim]")
        console.print(f"[dim]📧 Para: {email}[/dim]")
        console.print(f"[dim]🔄 Valor: {value} pontos[/dim]")
        console.print(f"[dim]📊 Seu saldo: {balance_info['balance']} pontos[/dim]")
        
        result = transfer(current_user.email, email, value)
        
        if result["success"]:
            console.print("[green]✅ Transferência realizada com sucesso![/green]")
            console.print(f"[cyan]Seu novo saldo: {result['from_balance']} pontos[/cyan]")
            log.info(f"Transferred {value} points from {current_user.email} to {email}")
        else:
            console.print(f"[red]❌ Falha na transferência: {result['error']}[/red]")
            log.error(f"Transfer failed: {result['error']}")
            
    except Exception as e:
        console.print(f"[red]❌ Erro na transferência: {e}[/red]")
        log.error(f"Error in transfer: {e}")
        sys.exit(1)


@main.command()
@click.option("--email", help="Email do usuário (apenas CEO/Manager podem ver de outros)")
@click.option("--limit", default=10, help="Número de movimentos a mostrar")
@login_required
def statement(email: Optional[str] = None, limit: int = 10, current_user=None):
    """Mostra o extrato de movimentações do usuário"""
    
    # Verifica permissões
    is_admin, role, name = check_admin_role(current_user.email)
    
    # Se não for admin, só pode ver seu próprio extrato
    if not is_admin:
        if email and email != current_user.email:
            console.print("[red]❌ Você só pode ver seu próprio extrato![/red]")
            return
        email = current_user.email
    
    # Se não especificou email e é admin, pede o email
    if not email and is_admin:
        email = click.prompt("📧 Email do usuário para extrato", type=str)
    
    try:
        movements = get_statement(email, limit)
        
        if not movements:
            console.print(f"[yellow]Nenhum movimento encontrado para {email}[/yellow]")
            return
        
        # Buscar dados do usuário
        user_data = get_balance(email)
        
        # Título do extrato
        title = f"📋 Extrato de {user_data['name'] if user_data else email}"
        if is_admin and email != current_user.email:
            title += f" (visualizado por {current_user.name} - {role})"
        
        table = Table(title=title)
        table.add_column("Data", style="cyan", no_wrap=True)
        table.add_column("Valor", style="green", justify="right")
        table.add_column("Realizado por", style="yellow")
        table.add_column("Saldo", style="bold white", justify="right")
        
        # Calcular saldo acumulado
        running_balance = 0
        
        for mov in movements:
            running_balance += mov["value"]
            value_str = f"+{mov['value']}" if mov['value'] > 0 else str(mov['value'])
            
            # Cor do valor
            if mov['value'] > 0:
                value_color = "green"
            else:
                value_color = "red"
            
            table.add_row(
                mov["date"],
                f"[{value_color}]{value_str}[/{value_color}]",
                mov["actor"] or "Sistema",
                str(running_balance)
            )
        
        console.print(table)
        console.print(f"[dim]Total de movimentos: {len(movements)}[/dim]")
        
        if user_data:
            console.print(f"[bold]Saldo final: {user_data['balance']} {user_data['currency']}[/bold]")
        
        log.info(f"Statement shown for {email} by {current_user.email}")
        
    except Exception as e:
        console.print(f"[red]❌ Erro ao mostrar extrato: {e}[/red]")
        log.error(f"Error showing statement: {e}")
        sys.exit(1)


@main.command()
def login():
    """Faz login no sistema"""
    email = click.prompt("📧 Email", type=str)
    password = click.prompt("🔑 Senha", hide_input=True, type=str)
    
    if authenticate(email, password):
        # Salvar credenciais usando a função de sessão
        save_session(email, password)
        
        # Buscar informações do usuário
        is_admin, role, name = check_admin_role(email)
        user_data = get_current_user(email)
        
        console.print("[green]✅ Login realizado com sucesso![/green]")
        console.print(f"[cyan]👤 Usuário: {name if user_data else email}[/cyan]")
        
        if is_admin:
            console.print(f"[green]👑 Privilégios: {role}[/green]")
        else:
            console.print(f"[blue]🔹 Privilégios: Usuário Padrão[/blue]")
        
        log.info(f"User {email} logged in")
    else:
        console.print("[red]❌ Credenciais inválidas![/red]")
        sys.exit(1)


@main.command()
def logout():
    """Faz logout do sistema"""
    email = get_session_email()
    clear_session()
    if email:
        console.print(f"[green]✅ Logout realizado com sucesso! ({email})[/green]")
        log.info(f"User {email} logged out")
    else:
        console.print("[yellow]⚠️ Você não está logado[/yellow]")


@main.command()
@click.option("--email", required=True, help="Email do usuário")
@click.option("--password", help="Senha (se não fornecida, será solicitada)")
def set_password(email: str, password: Optional[str] = None):
    """Define a senha inicial para um usuário (apenas para setup)"""
    
    # Verificar se o usuário existe
    user_data = get_current_user(email)
    if not user_data:
        console.print(f"[red]❌ Usuário não encontrado: {email}[/red]")
        return
    
    if not password:
        password = click.prompt("🔑 Nova senha", hide_input=True, type=str)
        confirm = click.prompt("🔑 Confirmar senha", hide_input=True, type=str)
        
        if password != confirm:
            console.print("[red]❌ As senhas não coincidem![/red]")
            return
    
    try:
        set_initial_password(email, password)
        console.print(f"[green]✅ Senha definida com sucesso para {email}![/green]")
        log.info(f"Password set for {email}")
    except Exception as e:
        console.print(f"[red]❌ Erro ao definir senha: {e}[/red]")
        log.error(f"Error setting password: {e}")
        sys.exit(1)


@main.command()
def whoami():
    """Mostra o usuário atual logado"""
    # Tenta carregar a sessão
    email, _ = load_session()
    
    if email:
        user_data = get_current_user(email)
        is_admin, role, name = check_admin_role(email)
        
        console.print(Panel(
            Text.assemble(
                ("👤 ", "bold"),
                (f"{user_data.name if user_data else email}\n", "cyan"),
                ("📧 ", "bold"),
                (f"{email}\n", "blue"),
                ("🔹 ", "bold"),
                (f"Role: {role if role else 'N/A'}\n", "yellow"),
                ("👑 ", "bold"),
                (f"Admin: {'Sim' if is_admin else 'Não'}", "green" if is_admin else "red")
            ),
            title="🔐 Informações do Usuário"
        ))
    else:
        console.print("[yellow]⚠️ Você não está logado. Use 'dundie login'[/yellow]")


if __name__ == "__main__":
    main()