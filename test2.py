from loadstructure import ConfigManager, SchemaError
import os

# ---------- Test Setup ----------
test_file = "test_config.json"

# Remove old test file if exists
if os.path.exists(test_file):
    os.remove(test_file)

# ---------- Define schema ----------
schema = {
    "user": {"name": str, "age": int},
    "skills": list,
    "meta": dict  # allow any dict for meta
}

# Initialize ConfigManager
cfg_mgr = ConfigManager(test_file, schema=schema)
cfg = cfg_mgr.load()  # Load or create empty config

# ---------- Test 1: Attribute-style creation ----------
try:
    cfg.user.name = "Anmol"
    cfg.user.age = 21
    cfg.skills = ["python", "c++"]
    cfg.meta.info = "Test metadata"   # nested dict auto-created
    print("Test 1 Passed: Attribute-style creation works.")
except SchemaError as e:
    print("Test 1 Failed:", e)

# ---------- Test 2: Dotted-path set ----------
try:
    cfg.set("user.name", "Anmolkumar")  # overwrite
    cfg.set("user.age", 22)
    cfg.set("meta.version", 1.0)
    print("Test 2 Passed: Dotted-path set works.")
except SchemaError as e:
    print("Test 2 Failed:", e)

# ---------- Test 3: Attribute access ----------
try:
    assert cfg.user.name == "Anmolkumar"
    assert cfg.user.age == 22
    assert cfg.skills == ["python", "c++"]
    assert cfg.meta.info == "Test metadata"
    assert cfg.meta.version == 1.0
    print("Test 3 Passed: Attribute access works.")
except AssertionError:
    print("Test 3 Failed: Attribute access incorrect.")

# ---------- Test 4: Schema validation ----------
try:
    cfg.user.age = 22  # invalid type
    print("Test 4 Failed: Schema validation did not raise error!")
except SchemaError:
    print("Test 4 Passed: Schema validation works.")

# ---------- Save to file ----------
cfg_mgr.save()

# ---------- Test 5: Reload and check ----------
cfg2 = cfg_mgr.load()
try:
    assert cfg2.user.name == "Anmolkumar"
    assert cfg2.user.age == 22
    assert cfg2.skills == ["python", "c++"]
    assert cfg2.meta.info == "Test metadata"
    assert cfg2.meta.version == 1.0
    print("Test 5 Passed: Reload works correctly.")
except AssertionError:
    print("Test 5 Failed: Reload did not preserve data.")

# ---------- Print final config dict ----------
print("\nFinal Config Dictionary:")
print(cfg_mgr.to_dict())
