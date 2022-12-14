from django.conf import settings
from django.contrib.auth import get_user
from django.core.cache import cache
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from product.forms import ProductForm, ReviewForm
from product.models import Product, ProductCategory
from shop.models import Shop
from promotion.services import BannerMain
from .services import ReviewForItem, ProductCompareList, SortProductsResult, FilterProductsResult, DetailedProduct
from .services import DailyOffer, BrowsingHistory, PopularCategory, SearchProduct
from constance import config
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, DetailView, CreateView, ListView


class CompareView(View):
    """
    Получение листа сравнений
    """

    def get(self, request, *args, **kwargs):
        compare_list = None
        if request.session.get(settings.CACHE_KEY_COMPARISON):
            compare_list = ProductCompareList(
                request.session.get(settings.CACHE_KEY_COMPARISON),
                True,
                'None'
            )
        return render(request, 'product/compare.html', {'compare_list': compare_list})

    def post(self, request, *args, **kwargs):
        short_list = request.POST.get('differentFeature')
        choice_category = request.POST.get('ChoiceCategory')
        compare_list = ProductCompareList(
            request.session.get(settings.CACHE_KEY_COMPARISON),
            short_list,
            choice_category
        )
        return render(request, 'product/compare.html', {'compare_list': compare_list})


class CompareAdd(View):
    """
    Добавление элемента в список сравнений
    """

    def get(self, request, *args, **kwargs):
        product_list = request.session.get(settings.CACHE_KEY_COMPARISON)
        product = kwargs['pk']

        if not product_list:
            product_list = [product]
        elif product not in product_list:
            product_list.append(product)
        request.session[settings.CACHE_KEY_COMPARISON] = product_list
        return render(request, 'product/compare_change.html', {'message': _('объект добавлен')})


class CompareRemove(View):
    """
    Удаление элемента из списка сравнений
    """

    def get(self, request, *args, **kwargs):
        product_list = request.session.get(settings.CACHE_KEY_COMPARISON)
        product = kwargs['pk']

        if product in product_list:
            product_list.remove(product)
            request.session[settings.CACHE_KEY_COMPARISON] = product_list
        return redirect('/product/compare/')


class CompareClear(View):
    """
    Полная очистка листа сравнений
    """

    def get(self, request, *args, **kwargs):
        product_list = request.session.get(settings.CACHE_KEY_COMPARISON)
        product_list.clear()
        request.session[settings.CACHE_KEY_COMPARISON] = product_list
        return redirect('/')


class CreateProductView(CreateView):
    model = Product
    form_class = ProductForm


class MainPage(TemplateView):
    template_name = "product/index.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["banners"] = BannerMain.get_cache_banners()

        daily_offer = DailyOffer()
        products = FilterProductsResult()
        context["top_product"] = SortProductsResult(products.queryset).by_popularity()[:8]
        context["daily_offer"] = daily_offer.product

        products.only_limited()
        context["limited_product"] = products.queryset.exclude(id=daily_offer.product_id).order_by("?")[:16]

        hot_product = FilterProductsResult()
        hot_product.with_promo()
        context["hot_product"] = hot_product.queryset[:9]

        context['popular_category'] = PopularCategory.get_cached()

        return context


class CatalogView(ListView):

    template_name = "product/catalog.html"
    context_objects_name = "product_list"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category = None
        self.shops = None
        self.price_range = self.current_price_range = None

    def get_queryset(self):

        filter_product = FilterProductsResult(**self.request.GET.dict())

        category = self.kwargs.get("category", None)
        if category:
            self.category = get_object_or_404(ProductCategory, slug=category)
            filter_product.by_category(self.category)

        filter_product.all_filter_without_price()
        self.price_range = filter_product.price_range()
        filter_product.by_price()
        self.current_price_range = {"min": filter_product.min_price, "max": filter_product.max_price}

        self.shops = Shop.objects.filter(product__in=filter_product.queryset).distinct().values_list("name", flat=True)

        queryset = SortProductsResult(products=filter_product.queryset).sort_by_params(**self.request.GET.dict())

        return queryset

    def get_paginate_by(self, queryset):
        return config.OBJECTS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort_data"] = SortProductsResult.get_data_for_sort_links(**self.request.GET.dict())
        context["parent_categories"] = self.category.get_ancestors(include_self=True) if self.category else None
        context["child_categories"] = (
            self.category.get_children() if self.category else ProductCategory.objects.root_nodes()
        )
        context["filter_part_url"] = FilterProductsResult.make_filter_part_url(self.request.GET.dict())
        context["sort_part_url"] = SortProductsResult.make_sort_part_url(self.request.GET.dict())
        context["shops"] = self.shops
        context["price_range"] = self.price_range
        context["current_price_range"] = self.current_price_range
        return context


class DetailedProductView(DetailView):
    model = Product
    template_name = "product/product.html"
    TIMEOUT = settings.SESSION_COOKIE_AGE

    def get_context_data(self, **kwargs):
        context = super(DetailedProductView, self).get_context_data(**kwargs)
        context["detailed_product"] = cache.get_or_set(f"product-{self.object.id}", DetailedProduct(self.object))

        reviews = ReviewForItem(self.object)
        stars_order_by = reviews.get_stars_order_by()
        paginator = Paginator(reviews.get_reviews_product(), config.COMMENTS_PER_PAGE)
        page_obj = paginator.get_page(kwargs.get("page_number", 1))

        context["page_obj"] = page_obj
        context["count_reviews"] = reviews.get_count_reviews_product()
        context["stars_rating_users"] = stars_order_by
        context["stars_rating"] = stars_order_by[::-1]
        context["reviews_form"] = ReviewForm()

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        BrowsingHistory(get_user(self.request)).add_product_to_history(self.object)
        page_number = request.GET.get("page", 1)
        context = self.get_context_data(page_number=page_number, **kwargs)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = request.POST

        if "delete" in data:
            ReviewForItem.delete_review(data["review_id"])
            messages.success(request, _("Отзыв удален."))
        else:
            reviews_form = ReviewForm(data)

            if reviews_form.is_valid():
                review_data = reviews_form.cleaned_data
                review = ReviewForItem(self.object)
                review.add_review(user=request.user, **review_data)
                messages.success(request, _("Отзыв добавлен."))
            else:
                page_number = request.POST.get("page", 1)
                context = self.get_context_data(page_number=page_number, **kwargs)
                context["reviews_form"] = reviews_form
                messages.error(request, _("Отзыв не добавлен, проверьте корректность ввода."))
                return render(request, self.template_name, context=context)

        return redirect("product-page", self.object.pk)


class SearchView(ListView):

    template_name = "product/search.html"
    context_objects_name = "product_list"

    def get_queryset(self):
        search_query = self.request.GET.get('search_query')
        products = SearchProduct(search_query)
        queryset = SortProductsResult(products=products.queryset).sort_by_params(**self.request.GET.dict())
        return queryset

    def get_paginate_by(self, queryset):
        return config.OBJECTS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sort_data"] = SortProductsResult.get_data_for_sort_links(**self.request.GET.dict())
        # context["sort_part_url"] = SortProductsResult.make_sort_part_url(self.request.GET.dict())
        context["filter_part_url"] = f'search_query={self.request.GET.get("search_query")}'
        return context
