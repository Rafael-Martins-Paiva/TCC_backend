from accounts.models import User, UserRole

def run():
    try:
        user = User.objects.get(email='Rafael.martinsner@g.com')
        user.role = UserRole.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"User {user.email} updated to ADMIN role successfully.")
    except User.DoesNotExist:
        print("User with email Rafael.martinsner@g.com does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
