# scripts/restore_original_passwords.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dundie.database import get_session
from dundie.models import User, Person
from sqlmodel import select

def restore_original_passwords():
    """Restaura as senhas originais em texto puro"""
    
    # Mapeamento de person_id para senha original
    passwords = {
        1: "vAiQo79u",
        2: "tJmD3rWf", 
        3: "cirV13EY",
        4: "8DovGzLO",
        5: "LfRwIGJE",
        6: "g53nfhJj",
        7: "58WJE47S",
        8: "qv8A1uD6",
        9: "HAK6VeWF",
        10: "QNC8ohbL"
    }
    
    with get_session() as session:
        users = session.exec(select(User)).all()
        
        print("=" * 60)
        print("Restaurando senhas originais (texto puro)")
        print("=" * 60)
        
        for user in users:
            if user.person_id in passwords:
                # Buscar o email da pessoa
                person = session.exec(select(Person).where(Person.id == user.person_id)).first()
                email = person.email if person else "unknown"
                
                old_password_preview = user.password[:30] + "..." if len(user.password) > 30 else user.password
                user.password = passwords[user.person_id]  # Texto puro original!
                
                print(f"✅ User ID {user.id} - {email}")
                print(f"   Antiga: {old_password_preview}")
                print(f"   Nova: {passwords[user.person_id]}")
                print()
        
        session.commit()
        
        print("=" * 60)
        print("🎉 Senhas originais restauradas com sucesso!")
        print("\n📝 Credenciais restauradas:")
        print("   jim@dundermifflin.com → vAiQo79u")
        print("   schrute@dundermifflin.com → tJmD3rWf")
        print("   glewis@dundermifflin.com → cirV13EY")
        print("   pam@dm.com → 8DovGzLO")
        print("   vanessa@dm.com → QNC8ohbL")
        print("=" * 60)

if __name__ == "__main__":
    restore_original_passwords()
