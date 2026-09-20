from maclinux.recipes import get_recipe, recipe_status


def test_recipe_states():
    recipe = get_recipe("facetimehd")
    assert recipe is not None
    assert recipe_status(recipe, distribution="ubuntu", architecture="x86_64", kernel="6.8.0") == "buildable"
    assert recipe_status(recipe, distribution="ubuntu", architecture="aarch64", kernel="6.8.0") == "unsupported"
    assert recipe_status(recipe, distribution="alpine", architecture="x86_64", kernel="6.8.0") == "unsupported"
