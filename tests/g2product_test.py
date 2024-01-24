import json

import pytest
from pytest_schema import Regex, schema

from senzing import g2exception, g2product

# -----------------------------------------------------------------------------
# G2Product fixtures
# -----------------------------------------------------------------------------


@pytest.fixture(name="g2_product", scope="module")
def g2product_fixture(engine_vars):
    """
    Single engine object to use for all tests.
    engine_vars is returned from conftest.py.
    """
    result = g2product.G2Product(
        engine_vars["MODULE_NAME"],
        engine_vars["INI_PARAMS"],
    )
    return result


# -----------------------------------------------------------------------------
# G2Product schemas
# -----------------------------------------------------------------------------

license_schema = {
    "customer": str,
    "contract": str,
    "issueDate": Regex(r"^\d{4}-\d{2}-\d{2}$"),
    "licenseType": str,
    "licenseLevel": str,
    "billing": str,
    "expireDate": Regex(r"^\d{4}-\d{2}-\d{2}$"),
    "recordLimit": int,
}


version_schema = {
    "PRODUCT_NAME": str,
    "VERSION": Regex(
        r"^([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?$"
    ),
    "BUILD_VERSION": str,
    "BUILD_DATE": Regex(r"^\d{4}-\d{2}-\d{2}$"),
    "BUILD_NUMBER": str,
    "COMPATIBILITY_VERSION": {
        "CONFIG_VERSION": str,
    },
    "SCHEMA_VERSION": {
        "ENGINE_SCHEMA_VERSION": str,
        "MINIMUM_REQUIRED_SCHEMA_VERSION": str,
        "MAXIMUM_REQUIRED_SCHEMA_VERSION": str,
    },
}


# -----------------------------------------------------------------------------
# G2Product testcases
# -----------------------------------------------------------------------------


def test_exception(g2_product):
    """Test exceptions."""
    actual = g2_product.new_exception(0)
    assert isinstance(actual, Exception)


def test_constructor(engine_vars):
    """Test constructor."""
    actual = g2product.G2Product(
        engine_vars["MODULE_NAME"],
        engine_vars["INI_PARAMS"],
    )
    assert isinstance(actual, g2product.G2Product)


def test_constructor_bad_module_name(engine_vars):
    """Test constructor."""
    bad_module_name = ""
    with pytest.raises(g2exception.G2Exception):
        actual = g2product.G2Product(
            bad_module_name,
            engine_vars["INI_PARAMS"],
        )
        assert isinstance(actual, g2product.G2Product)


def test_constructor_bad_ini_params(engine_vars):
    """Test constructor."""
    bad_ini_params = ""
    with pytest.raises(g2exception.G2Exception):
        actual = g2product.G2Product(
            engine_vars["MODULE_NAME"],
            bad_ini_params,
        )
        assert isinstance(actual, g2product.G2Product)


def test_license(g2_product):
    """Test Senzing license."""
    actual = g2_product.license()
    assert isinstance(actual, str)
    actual_json = json.loads(actual)
    assert schema(license_schema) == actual_json


def test_license_as_json(g2_product):
    """Test Senzing license."""
    actual = g2_product.license().as_dict()
    assert isinstance(actual, dict)
    assert schema(license_schema) == actual


def test_version(g2_product):
    """Test Senzing version."""
    actual = g2_product.version()
    assert isinstance(actual, str)
    actual_json = json.loads(actual)
    assert schema(version_schema) == actual_json


def test_init_and_destroy(g2_product):
    """Test init/destroy cycle."""
    g2_product.init("Example", "{}", 0)
    g2_product.destroy()


def test_init_and_destroy_again(g2_product):
    """Test init/destroy cycle a second time."""
    g2_product.init("Example", "{}", 0)
    g2_product.destroy()
