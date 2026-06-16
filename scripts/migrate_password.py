# scripts/migrate_password.py
import sys
import os

# Adiciona o diretório pai ao path para poder importar dundie
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dundie.database import get_session
from dundie.models import User
from dundie.utils.user import get_password_hash
from sqlmodel import select

def migrate_passwords():
    """Migra todas as senhas em texto puro para hash"""
    print("🔐 Starting password migration...")
    
    with get_session() as session:
        users = session.exec(select(User)).all()
        
        if not users:
            print("❌ No users found in database!")
            return
        
        migrated_count = 0
        for user in users:
            # Verifica se a senha já é um hash (começa com $2b$ ou $argon2id$)
            is_hashed = user.password.startswith('$2b$') or user.password.startswith('$argon2id$')
            
            if not is_hashed:
                old_password = user.password
                user.password = get_password_hash(old_password)
                migrated_count += 1
                print(f"✅ Migrated user ID {user.id}: {old_password} -> {user.password[:30]}...")
            else:
                print(f"⏭️  Skipping user ID {user.id} (already hashed)")
        
        if migrated_count > 0:
            session.commit()
            print(f"\n🎉 Successfully migrated {migrated_count} passwords!")
        else:
            print("\n✨ All passwords are already hashed!")
        
        # Mostrar resumo com verificação correta
        print("\n📊 Migration Summary:")
        users = session.exec(select(User)).all()
        for user in users:
            is_hashed = user.password.startswith('$2b$') or user.password.startswith('$argon2id$')
            status = "✅ hashed" if is_hashed else "⚠️  plain text"
            print(f"   User ID {user.id}: {status} - {user.password[:20]}...")

if __name__ == "__main__":
    print("=" * 50)
    print("Dundie Rewards - Password Migration Tool")
    print("=" * 50)
    migrate_passwords()