from maclinux.recipes import get_recipe, recipe_status, version_supported


def test_recipe_states():
    recipe = get_recipe("facetimehd")
    assert recipe is not None
    assert recipe_status(recipe, distribution="ubuntu", version="24.04", architecture="x86_64", kernel="6.8.0") == "buildable"
    assert recipe_status(recipe, distribution="ubuntu", version="24.04", architecture="aarch64", kernel="6.8.0") == "unsupported"
    assert recipe_status(recipe, distribution="alpine", version="3.23", architecture="x86_64", kernel="6.8.0") == "unsupported"


def test_recipe_version_is_explicit():
    recipe = get_recipe("facetimehd")
    assert recipe is not None
    assert version_supported(recipe, "ubuntu", "24.04")
    assert not version_supported(recipe, "ubuntu", "99.99")
    assert not version_supported(recipe, "ubuntu", "")
