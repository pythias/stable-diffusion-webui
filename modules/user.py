from pydantic import BaseModel, Field

class RequestUser(BaseModel):
    user_name: str = Field(default="", title="UserName", description="Login User Name", regex=r"^[a-zA-Z0-9_]{3,16}$")

    def get_prefix(self):
        return f"{self.user_name}-"

    def character_to_style(self, character_name):
        return self.get_prefix() + character_name
    
    def style_to_character(self, style_name):
        return style_name[len(self.get_prefix()):]

    def has_permission(self, style_name):
        prefix = self.get_prefix()
        return prefix == style_name[:len(prefix)]
