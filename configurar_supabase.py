#!/usr/bin/env python
"""
Script para migrar a Supabase - Configuración rápida
"""

import os

def main():
    print("🚀 CONFIGURACIÓN DE SUPABASE")
    print("=" * 50)
    
    supabase_url = "postgresql://postgres:3jbxqfv$2gyW$yG@db.mwjdmmowllmxygscgcex.supabase.co:5432/postgres"
    
    print(f"✅ URL de Supabase configurada:")
    print(f"   {supabase_url}")
    
    print(f"\n📋 PASOS PARA COMPLETAR LA MIGRACIÓN:")
    print(f"")
    print(f"1. 🌐 Ve al dashboard de Render:")
    print(f"   https://dashboard.render.com")
    print(f"")
    print(f"2. 🔧 Busca tu servicio web (sistema-rrhh)")
    print(f"")
    print(f"3. ⚙️ Ve a Environment Variables")
    print(f"")
    print(f"4. 🔄 Actualiza la variable DATABASE_URL con:")
    print(f"   {supabase_url}")
    print(f"")
    print(f"5. 🚀 Haz clic en 'Save, rebuild, and deploy'")
    print(f"")
    print(f"6. ⏳ Espera que termine el deploy (2-3 minutos)")
    print(f"")
    print(f"7. 👥 Ve a https://sistema-rrhh.onrender.com/setup/organigrama/")
    print(f"   para cargar los usuarios")
    print(f"")
    print("=" * 50)
    print("🎯 ¡Eso es todo! Supabase será tu nueva base de datos.")
    print("📊 Ventajas: Más confiable, sin pérdida de datos, mejor rendimiento")

if __name__ == '__main__':
    main()
