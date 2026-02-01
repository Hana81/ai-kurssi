from django.contrib.auth.models import User

u = User.objects.get(username='admin')
u.is_staff = True
u.is_superuser = True
u.is_active = True
u.save()

print('Admin-käyttäjä päivitetty!')
print(f'Username: {u.username}')
print(f'Is staff: {u.is_staff}')
print(f'Is superuser: {u.is_superuser}')
print(f'Is active: {u.is_active}')
