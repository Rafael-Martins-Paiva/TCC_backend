from rest_framework_simplejwt.tokens import RefreshToken


class LogoutService:
    def logout(self, refresh_token):
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return {"success": "User logged out successfully."}
        except Exception as e:
            return {"error": str(e)}
