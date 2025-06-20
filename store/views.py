from django.shortcuts import render, get_object_or_404
from .models import Product, Category # Make sure Category is imported
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm


from .forms import CheckoutForm , ReviewForm
from .models import Product, Order
from django.db.models import Q


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    category_slug = request.GET.get('category')
    categories = Category.objects.all()

    if category_slug:
        products = Product.objects.filter(category__slug=category_slug)
    else:
        products = Product.objects.all()

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_slug
    })
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all().order_by('-created_at')
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', slug=slug)

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart  # ✅ Save updated cart
    return redirect('cart_view')  # or redirect('home')

def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            pass  # optional: log or handle missing product

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart_view')
from django.shortcuts import redirect

def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart_view')

def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        if cart[str(product_id)] > 1:
            cart[str(product_id)] -= 1
        else:
            del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart_view')
@login_required
def profile_view(request):
    user = request.user
    cart = request.session.get('cart', {})
    orders = Order.objects.filter(user=request.user).order_by('-id')

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            continue

    return render(request, 'profile.html', {
    'user': user,
    'cart_items': cart_items,
    'total': total,
    'orders': orders  # 👈 This was missing
})
def checkout_view(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart_view')

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'get_total_price': subtotal,
            })
            total += subtotal
        except Product.DoesNotExist:
            continue

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                total_price=total
            )
            request.session['cart'] = {}
            return render(request, 'order_success.html')

    else:
        form = CheckoutForm()

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'cart_total': total
    })

# def checkout_view(request):
#     cart = request.session.get('cart', {})

#     if not cart:
#         return redirect('cart_view')

#     if request.method == 'POST':
#         form = CheckoutForm(request.POST)
#         if form.is_valid():
#             total = 0
#             for product_id, quantity in cart.items():
#                 try:
#                     product = Product.objects.get(id=product_id)
#                     total += product.price * quantity
#                 except Product.DoesNotExist:
#                     continue

#             Order.objects.create(
#                 user=request.user,
#                 full_name=form.cleaned_data['full_name'],
#                 address=form.cleaned_data['address'],
#                 phone=form.cleaned_data['phone'],
#                 total_price=total
#             )

#             request.session['cart'] = {}  # Clear cart after ordering
#             return render(request, 'order_success.html')
#     else:
#         form = CheckoutForm()

#     return render(request, 'checkout.html', {'form': form})

def search_view(request):
    query = request.GET.get('q')
    products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)) if query else []
    return render(request, 'search_results.html', {'products': products, 'query': query})