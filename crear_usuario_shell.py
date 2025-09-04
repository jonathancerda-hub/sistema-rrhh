from django.contrib.auth.models import User

# Eliminar usuario si existe
if User.objects.filter(username='admin').exists():
    User.objects.filter(username='admin').delete()
    print("Usuario admin eliminado")

# Crear nuevo superusuario
user = User.objects.create_superuser(
    username='admin',
    email='admin@empresa.com',
    password='admin123'
)

print(f"Superusuario creado: {user.username}")
print(f"Email: {user.email}")
print(f"Es superusuario: {user.is_superuser}")
print("Credenciales: admin / admin123")
