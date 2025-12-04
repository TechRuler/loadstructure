from loadstructure import ConfigManager

# -----------------------------
# 1) Load (auto-creates empty file if not exists)
# -----------------------------
cfg_manager = ConfigManager("data.tkproj", "xml")
cfg = cfg_manager.load()

# -----------------------------
# 2) Assign values normally
# -----------------------------
cfg.name = "Anmol"
cfg.age = 21

# -----------------------------
# 3) Auto-create nested attributes
# -----------------------------
cfg.skill.language = ["python", "c++"]       # auto creates skill + language
cfg.skill.experience.years = 3               # auto creates experience + years

# -----------------------------
# 4) Dict assignment works
# -----------------------------
cfg.database = {
    "host": "localhost",
    "port": 3306,
    "enabled": True
}

# -----------------------------
# 5) Update part of config
# -----------------------------
cfg.update({
    "theme": "dark",
    "version": 1.0
})

# -----------------------------
# 6) Deep set using dotted notation
# -----------------------------
cfg.set("editor.font.size", 14)
cfg.set("editor.font.family", "Consolas")

# -----------------------------
# 7) Replace whole config
# -----------------------------
# cfg.replace({"app": {"name": "DemoApp", "version": 1}})

# Uncomment to test replace:
# cfg.replace({
#     "app": {
#         "name": "MyApp",
#         "version": 2
#     }
# })

# -----------------------------
# 8) Print config as dict
# -----------------------------
print(cfg.to_dict())

# -----------------------------
# 9) Save to JSON
# -----------------------------
cfg_manager.save()
