import pytest

# This option controls whether manual tests will be run.
def pytest_addoption(parser):
  parser.addoption("--manual", action = "store_true", default = False, help = "run manual tests")

def pytest_collection_modifyitems(config, items):
  if config.getoption("--manual"):
    # --manual given in cli: do not skip manual tests
    return
  skip_manual = pytest.mark.skip(reason = "need --manual option to run")
  for item in items:
    if "manual" in item.keywords:
      item.add_marker(skip_manual)