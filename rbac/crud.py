from rbac import models
from crud.service import throne



throne.site.register(models.User)
throne.site.register(models.Role)
throne.site.register(models.Permission)
throne.site.register(models.Group)
throne.site.register(models.Menu)
