from django.urls import path

from . import views


app_name = "production"


urlpatterns = [

    # =====================================================
    # GOAT WEIGHT
    # =====================================================

    path("goat-weight/",views.goat_weight_list,name="goat_weight_list"),
    path("goat-weight/create/",views.goat_weight_create,name="goat_weight_create"),
    path("goat-weight/voice/create/",views.goat_weight_voice_create,name="goat_wight_voice_create"),
    path("goat-weight/<uuid:id>/edit/",views.goat_weight_update,name="goat_weight_update"),
    path("goat-weight/<uuid:id>/delete/",views.goat_weight_delete,name="goat_weight_delete"),

    # =====================================================
    # GOAT MILK
    # =====================================================

    path("goat-milk/",views.goat_milk_list,name="goat_milk_list"),
    path("goat-milk/create/",views.goat_milk_create,name="goat_milk_create"),
    path("goat-milk/voice/create/", views.goat_milk_voice_create,   name="goat_milk_voice_create"),
    path("goat-milk/<uuid:id>/edit/",views.goat_milk_update,name="goat_milk_update"),
    path("goat-milk/<uuid:id>/delete/",views.goat_milk_delete,name="goat_milk_delete"),
    
    path("goat-milk-batches/",views.goat_milk_batch_list,name="goat_milk_batch_list"),
    path("goat-milk-batches/create/",views.goat_milk_batch_create,name="goat_milk_batch_create"),
    path("goat-milk-batches/<uuid:pk>/edit/",views.goat_milk_batch_edit,name="goat_milk_batch_edit"),
    path("goat-milk-batches/<uuid:pk>/delete/",views.goat_milk_batch_delete,name="goat_milk_batch_delete"),

    path("goat-milk-tests/",views.goat_milk_test_list,name="goat_milk_test_list"),
    path("goat-milk-tests/create/",views.goat_milk_test_create,name="goat_milk_test_create"),
    path("goat-milk-tests/<uuid:pk>/edit/",views.goat_milk_test_edit,name="goat_milk_test_edit"),
    path("goat-milk-tests/<uuid:pk>/delete/",views.goat_milk_test_delete,name="goat_milk_test_delete"),

    path("products/",views.product_list,name="product_list"),
    path("products/create/",views.product_create,name="product_create"),
    path("products/<uuid:pk>/edit/",views.product_edit,name="product_edit"),
    path("products/<uuid:pk>/delete/",views.product_delete,name="product_delete"),

    path("product-prices/",views.product_price_list,name="product_price_list"),
    path("product-prices/create/",views.product_price_create,name="product_price_create"),
    path("product-prices/<uuid:pk>/edit/",views.product_price_edit,name="product_price_edit"),
    path("product-prices/<uuid:pk>/delete/",views.product_price_delete,name="product_price_delete"),

    path("ingredients/",views.ingredient_list,name="ingredient_list"),
    path("ingredients/create/",views.ingredient_create,name="ingredient_create"),
    path("ingredients/<uuid:pk>/edit/",views.ingredient_edit,name="ingredient_edit"),
    path("ingredients/<uuid:pk>/delete/",views.ingredient_delete,name="ingredient_delete"),

    path("ingredient-prices/",views.ingredient_price_list,name="ingredient_price_list"),
    path("ingredient-prices/create/",views.ingredient_price_create,name="ingredient_price_create"),
    path("ingredient-prices/<uuid:pk>/edit/",views.ingredient_price_edit,name="ingredient_price_edit"),
    path("ingredient-prices/<uuid:pk>/delete/",views.ingredient_price_delete,name="ingredient_price_delete"),

    path("recipes/",views.recipe_list,name="recipe_list"),
    path("recipes/create/",views.recipe_create,name="recipe_create"),
    path("recipes/<uuid:pk>/edit/",views.recipe_edit,name="recipe_edit"),
    path("recipes/<uuid:pk>/delete/",views.recipe_delete,name="recipe_delete"),

    path("recipe-items/",views.recipe_item_list,name="recipe_item_list"),
    path("recipe-items/create/",views.recipe_item_create,name="recipe_item_create"),
    path("recipe-items/<uuid:pk>/edit/",views.recipe_item_edit,name="recipe_item_edit"),
    path("recipe-items/<uuid:pk>/delete/",views.recipe_item_delete,name="recipe_item_delete"),

    path("product-batches/",views.product_batch_list,name="product_batch_list"),
    path("product-batches/create/",views.product_batch_create,name="product_batch_create"),
    path("product-batches/<uuid:pk>/edit/",views.product_batch_edit,name="product_batch_edit"),
    path("product-batches/<uuid:pk>/delete/",views.product_batch_delete,name="product_batch_delete"),
]