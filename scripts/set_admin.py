from accounts.models import User, UserRole

def run():
    try:
        user = User.objects.get(email='rafael.martins.paiva0@gmail.com')
        user.role = UserRole.ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"User {user.email} updated to ADMIN role successfully.")
    except User.DoesNotExist:
        print("User with email rafael.martins6431@gmail.com does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")