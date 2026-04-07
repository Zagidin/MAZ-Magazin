# ================= USER =================

from .user.catalog import (
    index,
    catalog,
    product_detail,
    order_qr_image,
    package_qr_image,
)

from .user.cart import (
    cart_page,
    checkout,
)

from .user.orders import (
    order_detail,
    my_orders,
)

# ================= SELLER =================

from .seller.dashboard import (
    seller_dashboard,
    seller_order_detail,
    seller_assemble,
    seller_verify_qr,
)

from .seller.operations import (
    seller_finish_assembly,
    seller_pack_order,
    seller_print_qr,
    order_add_item_api,
    scan_verify,
)

# ================= API =================

from .api.cart import (
    cart_add_api,
    cart_count_api,
    cart_items_api,
    cart_remove_api,
    cart_update_api,
)

from .api.orders import (
    order_api,
    product_api,
)

from .api.search import (
    product_by_article_api,
)

from .api.updates import (
    order_updates_api,
    orders_updates_api,
)

# ================= AUTH =================

from .auth import (
    register,
    login_view,
    logout_view,
)

# ================= STATIC PAGES =================

from .contacts_page import contacts
from .about_page import about

__all__ = [
    # User
    'index', 'catalog', 'product_detail',
    'order_qr_image', 'package_qr_image',
    'cart_page', 'checkout',
    'order_detail', 'my_orders',

    # Seller
    'seller_dashboard', 'seller_order_detail',
    'seller_assemble', 'seller_verify_qr',
    'seller_finish_assembly', 'seller_pack_order',
    'seller_print_qr', 'order_add_item_api', 'scan_verify',

    # API
    'cart_add_api', 'cart_count_api', 'cart_items_api',
    'cart_remove_api', 'cart_update_api',
    'order_api', 'product_api',
    'product_by_article_api',
    'order_updates_api', 'orders_updates_api',

    # Auth
    'register', 'login_view', 'logout_view',

    # Pages
    'contacts', 'about',
]