#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de login
"""

import requests
import json

def test_login():
    """Probar el endpoint de login"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Probando sistema de login...")
    print("=" * 50)
    
    # Usuarios de prueba
    usuarios_prueba = [
        "Ana López",
        "Carlos García", 
        "María Rodríguez",
        "Juan Pérez",
        "Usuario Nuevo"  # Este debería crearse automáticamente
    ]
    
    for usuario in usuarios_prueba:
        print(f"\n🔐 Probando login para: {usuario}")
        
        try:
            response = requests.post(f"{base_url}/login", 
                                  json={"nombre": usuario},
                                  headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Login exitoso!")
                print(f"   ID: {data.get('id_usuario')}")
                print(f"   Token: {data.get('token')[:20]}...")
                print(f"   Perfil: {data.get('perfil', {}).get('genero')}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Error: No se puede conectar al servidor")
            print("   Asegúrate de que el servidor esté ejecutándose con: python app.py")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")

def test_users_endpoint():
    """Probar el endpoint de usuarios"""
    base_url = "http://127.0.0.1:5000"
    
    print("\n👥 Probando endpoint de usuarios...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/users")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Usuarios obtenidos: {data.get('total', 0)}")
            for usuario in data.get('usuarios', []):
                print(f"   - {usuario.get('nombre')} (ID: {usuario.get('id_usuario')})")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 AliMentor AI - Pruebas del Sistema de Login")
    print("=" * 60)
    
    test_login()
    test_users_endpoint()
    
    print("\n💡 Para usar el sistema:")
    print("   1. Ejecuta: python app.py")
    print("   2. Abre: http://127.0.0.1:5000")
    print("   3. Usa cualquiera de estos usuarios:")
    print("      - Ana López")
    print("      - Carlos García")
    print("      - María Rodríguez")
    print("      - Juan Pérez")
    print("      - O cualquier otro nombre (se creará automáticamente)")
