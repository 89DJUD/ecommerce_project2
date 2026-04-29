from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Category, Order, OrderItem, Product


def _get_cart(request):
    return request.session.setdefault("cart", {})


def _cart_details(request):
    cart = _get_cart(request)
    items = []
    total = Decimal("0.00")

    products = Product.objects.filter(id__in=cart.keys())
    product_map = {str(product.id): product for product in products}

    for product_id, quantity in cart.items():
        product = product_map.get(str(product_id))
        if not product:
            continue

        quantity = int(quantity)
        subtotal = product.price * quantity
        total += subtotal
        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return items, total

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = max(1, int(request.POST.get("quantity", 1)))

    cart = _get_cart(request)
    current_quantity = int(cart.get(str(product.id), 0))
    new_quantity = min(current_quantity + quantity, product.stock)

    if product.stock <= 0:
        messages.error(request, "Ce produit est en rupture de stock.")
    else:
        cart[str(product.id)] = new_quantity
        request.session.modified = True
        messages.success(request, f"{product.name} a ete ajoute au panier.")

    return redirect(request.POST.get("next") or "cart_detail")


def cart_detail(request):
    items, total = _cart_details(request)
    return render(request, "cart_detail.html", {
        "cart_items": items,
        "cart_total": total,
    })


@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = max(1, int(request.POST.get("quantity", 1)))

    cart = _get_cart(request)
    cart[str(product.id)] = min(quantity, product.stock)
    request.session.modified = True
    messages.success(request, "Panier mis a jour.")

    return redirect("cart_detail")


@require_POST
def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session.modified = True
    messages.success(request, "Produit supprime du panier.")

    return redirect("cart_detail")


@login_required
def checkout(request):
    items, total = _cart_details(request)

    if not items:
        messages.info(request, "Ton panier est vide.")
        return redirect("cart_detail")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not all([full_name, email, address, city, phone]):
            messages.error(request, "Remplis tous les champs pour finaliser la commande.")
        else:
            with transaction.atomic():
                for item in items:
                    product = Product.objects.select_for_update().get(id=item["product"].id)
                    if item["quantity"] > product.stock:
                        messages.error(request, f"Stock insuffisant pour {product.name}.")
                        return redirect("cart_detail")

                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    email=email,
                    address=address,
                    city=city,
                    phone=phone,
                    total=total,
                    status="paid",
                )

                for item in items:
                    product = Product.objects.select_for_update().get(id=item["product"].id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=item["quantity"],
                    )
                    product.stock -= item["quantity"]
                    product.save(update_fields=["stock"])

                request.session["cart"] = {}
                messages.success(request, "Paiement confirme. Merci pour ta commande.")
                return redirect("order_success", order_id=order.id)

    return render(request, "checkout.html", {
        "cart_items": items,
        "cart_total": total,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "order_success.html", {"order": order})


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})


def category_detail(request, pk):
    category = get_object_or_404(Category, id=pk)
    products = category.products.all()
    return render(request, 'category_detail.html', {
        'category': category,
        'products': products
    })
