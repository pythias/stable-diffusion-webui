from pydantic import BaseModel, Field

class RequestUser(BaseModel):
    user_name: str = Field(default="", title="UserName", description="Login User Name")

    def get_prefix(self):
        return f"{self.user_name}-"

    def has_permission(self, style_name):
        prefix = self.get_prefix()
        return prefix == style_name[:len(prefix)]
